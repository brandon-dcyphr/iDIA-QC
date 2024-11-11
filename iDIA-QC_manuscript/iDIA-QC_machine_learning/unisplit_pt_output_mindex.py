
import collections
import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sklearn
from dotmap import DotMap
from matplotlib import rcParams
from pycaret.classification import *
from shapash import SmartExplainer

sys.path.append('../')
from tools import create_data, feat_trans


def load_models(model_dir):

    models = collections.defaultdict(dict)
    for name in os.listdir(model_dir):
        name = name.replace('.pkl', '')
        name_parts = [partn for partn in name.split('_') if partn]
        feat_name = name_parts[-1]
        # dataset_name = u'_'.join(name_parts[:-1])
        mpath = os.path.join(model_dir, name.replace('.pkl', ''))
        model = load_model(mpath)
        models[feat_name] = model
    print('---model keys---', list(models.keys()))
    return models


def create_test_dataset(exp_config, label_genpath, feat_dir):
    """
    """
    # label_genpath = '../dataset/DIAQC_ML_20221221/data4xgb/labels_1222.csv'
    label_dataset = pd.read_csv(label_genpath)

    # feat_dir = '../dataset/DIAQC_ML_20221221/2_features_info/'
    _, (mglc_featdatas, mgms_featdatas) = create_data.read_dataset(feat_dir)
    mglc_featdatas_feattrans = feat_trans.preprocess_feats(mglc_featdatas, exp_config)
    mgms_featdatas_feattrans = feat_trans.preprocess_feats(mgms_featdatas, exp_config)
    if exp_config.test_type == 'time_split':
        cv_datas = create_data.split_time_dataset(mglc_featdatas_feattrans, mgms_featdatas_feattrans, label_dataset,
                                                  test_size=0.2)
    elif exp_config.test_type == 'uniform_split':
        cv_datas = create_data.split_iteml_dataset(mglc_featdatas_feattrans, mgms_featdatas_feattrans, label_dataset,
                                                   test_size=0.2)

    def process_label(in_data, feat_names):
        """
        """
        in_data.set_index('Run_ID', inplace=True)
        in_data = in_data.drop(columns=['machine_tpid', 'machine_id'])
        in_data = in_data.apply(lambda x: x.astype(np.float32) if 'labels' not in x.name else x, axis=0)
        print('--after one hot data shape is---', in_data.shape)
        # label process
        labels_tps = in_data.pop('%s_labels' % exp_config['task_name'])
        labels = labels_tps.apply(lambda x: float(json.loads(x)['vt_label']) if exp_config.label_type == 'vt' \
            else json.loads(x)['count'])
        if exp_config.label_type == 'wt':
            labels = labels.apply(
                lambda x: 0.0 if sum(np.array([float(t) for t in x]) * exp_config.weight_label) / 3 > 0.5 else 1.0)
        in_data['%s_label' % exp_config['task_name']] = labels

        allfeat_labels = in_data.pop('feat_labels')
        for feat_name in feat_names:
            feat_label = allfeat_labels.apply(lambda x: json.loads(x)[feat_name])
            feat_label = feat_label.apply(lambda x: float(json.loads(x)['vt_label']) if exp_config.label_type == 'vt' \
                else json.loads(x)['count'])
            if exp_config.label_type == 'wt':
                feat_label = feat_label.apply(
                    lambda x: 0.0 if sum(np.array([float(t) for t in x]) * exp_config.weight_label) / 3 > 0.5 else 1.0)

            in_data[u'_'.join([feat_name, 'label'])] = feat_label

        return in_data

    trates_datasets = collections.defaultdict(dict)
    if exp_config['task_name'] == 'lc':
        lcfeats_ids = ['F1', 'F2', 'F3']
        all_feats_ids = lcfeats_ids
    elif exp_config['task_name'] == 'ms':
        ms_featids = []
        for idx in range(4, 16):
            ms_featids.append('F%d' % idx)
        all_feats_ids = ms_featids

    if exp_config['test_type'] == 'uniform_split':
        raw_train, raw_test = cv_datas[exp_config['task_name']]['uniform_sample']
        raw_train = process_label(raw_train, all_feats_ids)
        raw_test = process_label(raw_test, all_feats_ids)
    elif exp_config['test_type'] == 'time_split':
        raw_train, raw_test = cv_datas[exp_config['task_name']]['time_split']
        raw_train = process_label(raw_train, all_feats_ids)
        raw_test = process_label(raw_test, all_feats_ids)

    for feat_name in [exp_config['task_name']] + all_feats_ids:
        if feat_name == exp_config['task_name']:
            rel_clsm = [name for name in list(raw_train.columns) if
                        not ('_label' in name and exp_config['task_name'] not in name)]
        else:
            rel_clsm = [name for name in list(raw_train.columns) if '_%s' % feat_name in name]
            rel_clsm += ['%s_label' % feat_name]
            # machine type
            rel_clsm += ['D', 'R', 'W']

        print('--colum names for debug---', rel_clsm[:10])
        feat_raw_test = raw_test[rel_clsm]
        feat_raw_train = raw_train[rel_clsm]

        # _label to label
        label_name = '%s_label' % feat_name
        lbmapper = {label_name: 'label'}
        feat_raw_test = feat_raw_test.rename(columns=lbmapper)
        feat_raw_train = feat_raw_train.rename(columns=lbmapper)
        trates_datasets[exp_config['test_type']][feat_name] = (feat_raw_train, feat_raw_test)

        print('----------the feat:', feat_name, '--test data shape is---', feat_raw_train.shape, feat_raw_test.shape)

    return trates_datasets


def construct_index(datasets, models, exp_config):

    # Score_1.0
    score_1_flag = 'prediction_score_1'
    # Label
    label_flag = 'label'

    roc_datas = {}
    for feat_tsname, (feat_raw_train, test_data) in datasets[exp_config['test_type']].items():
        print('--configuration---', feat_tsname)
        # task level output
        # Feature importance based on SHAP-values. (model interpretation)
        model = models[feat_tsname]
        raw_columns = list(feat_raw_train.columns)
        pred_rlts = predict_model(model, data=test_data, raw_score=True)
        test_labels = test_data.pop('label')

        # output the prediction
        pred_out = pd.DataFrame()
        pred_out['pred_1_score'] = pred_rlts[score_1_flag]
        pred_out['pred_label'] = pred_rlts[label_flag]
        pred_out['label'] = test_labels
        pred_out.reset_index(inplace=True)
        pred_out.to_csv(os.path.join(exp_config['idsout_dir'], '%s_prediction.csv' % (feat_tsname)))

        if feat_tsname in ['ms', 'lc']:
            # score distribution
            pred_data = pd.DataFrame()
            pred_data['pred'] = pred_rlts[score_1_flag]
            pred_data['label'] = test_labels

            # output score dist figure
            rcParams.update({'figure.autolayout': True})
            plt.close("all")
            plt.figure(2)
            displot = sns.displot(data=pred_data, x='pred', hue=pred_data['label'], kind="kde", rug=True).set(
                xlim=(0, 1.0))
            displot.savefig(os.path.join(exp_config['idsout_dir'], '%s_scoredist.pdf' % (feat_tsname)))
            plt.cla()

            # group feature importance
            gp_columns = {}
            for feat_name in raw_columns:
                if 'label' in feat_name:
                    continue
                name_splits = feat_name.split('_')
                feat_tpname = name_splits[-1]
                feat_raw_name = u'_'.join(name_splits[:-1])
                gp_fname = ''
                if feat_tpname in ['F4', 'F5']:
                    gp_fname = feat_tpname
                else:
                    gp_fname = feat_raw_name
                if gp_fname not in gp_columns:
                    gp_columns[gp_fname] = []
                gp_columns[gp_fname].append(feat_name)

            # ypred=pd.DataFrame(list(pred_rlts['Label'].astype('float').values), columns=['pred'],index=test_data.index)
            # explainer = shap.TreeExplainer(model.named_steps["trained_model"])
            # shap_values = explainer.shap_values(test_data)

            xpl = SmartExplainer(model=model.named_steps["trained_model"], features_groups=gp_columns)
            xpl.compile(x=test_data, y_target=test_labels)
            # xpl.compile(x=test_data, y_pred=ypred, y_target=test_labels, contributions=shap_values)
            plt.figure(0)
            xpl.plot.features_importance(
                file_name=os.path.join(exp_config['idsout_dir'], '%s_gpshap_vals.pdf' % (feat_tsname)))
            plt.cla()

            xpl.features_imp_groups[-1].tail(100).to_csv(
                os.path.join(exp_config['idsout_dir'], '%s_gpshap_vals.csv' % (feat_tsname)))

            # Confusion matrix.
            plt.close("all")
            plt.figure(1)
            sklearn.metrics.ConfusionMatrixDisplay.from_estimator(model, test_data, test_labels)
            plt.savefig(os.path.join(exp_config['idsout_dir'], '%s_cfmatrix.pdf' % (feat_tsname)))
            plt.cla()

        fpr, tpr, thresholds = sklearn.metrics.roc_curve(test_labels, pred_rlts[score_1_flag])
        auc = sklearn.metrics.roc_auc_score(test_labels, pred_rlts[score_1_flag])
        roc_datas[feat_tsname] = (fpr, tpr, thresholds, auc)

    plt.figure()
    plt.grid(False)
    rcParams.update({'figure.autolayout': True})
    for label_name, (fpr, tpr, thresholds, auc) in roc_datas.items():
        plt.plot(fpr, tpr, label='%s ROC (area = %0.2f)' % (label_name, auc))
    plt.xlabel('1-Specificity(False Positive Rate)')
    plt.ylabel('Sensitivity(True Positive Rate)')
    plt.title('%s Performance' % exp_config['task_name'])
    plt.legend(loc="lower right")
    plt.savefig(os.path.join(exp_config['idsout_dir'], '%s_data.pdf' % ('roc')))
    plt.cla()

    return True, 'OK'


if __name__ == '__main__':
    # read dataset with preprocess
    # test_type = 'uniform_split'
    model_dir = '/home/niezongxiang/run_code/massspectro_pred/dataset/models_20240104_unisplit/'
    idsout_base_dir = '/home/niezongxiang/run_code/massspectro_pred/dataset/eval_figs_dataupdate_20240102_updataaix_unisplit'
    label_genpath = '/home/niezongxiang/run_code/massspectro_pred/dataset/labels_1222.csv'
    feat_dir = '/home/niezongxiang/run_code/massspectro_pred/dataset/2_features_info'

    test_type = 'uniform_split'

    task_name = 'lc'
    exp_config = dict(
        model_path=model_dir,
        idsout_dir=idsout_base_dir + '/%s_%s/' % (
            task_name, test_type),
        task_name=task_name,
        test_type=test_type,
        naratio_thre=0.3,
        fillna_md='min',
        label_type='vt',
    )
    exp_config = DotMap(exp_config)
    if not os.path.exists(exp_config.idsout_dir):
        os.makedirs(exp_config.idsout_dir)
    datasets = create_test_dataset(exp_config, label_genpath, feat_dir)
    models = load_models(exp_config['model_path'])
    construct_index(datasets, models, exp_config)
    print('***********************************************************')

    task_name = 'ms'
    exp_config = dict(
        model_path=model_dir,
        idsout_dir=idsout_base_dir + '/%s_%s/' % (
            task_name, test_type),
        task_name=task_name,
        test_type=test_type,
        naratio_thre=0.3,
        fillna_md='min',
        label_type='vt',
    )
    exp_config = DotMap(exp_config)
    if not os.path.exists(exp_config.idsout_dir):
        os.makedirs(exp_config.idsout_dir)
    datasets = create_test_dataset(exp_config, label_genpath, feat_dir)
    models = load_models(exp_config['model_path'])
    construct_index(datasets, models, exp_config)

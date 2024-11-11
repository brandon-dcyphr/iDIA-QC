
import collections
import json
import os.path
import sys

import numpy as np
import pandas as pd
from dotmap import DotMap
from pycaret.classification import *
from sklearn.linear_model import LogisticRegression

sys.path.append('../')
from tools import create_data, feat_trans


def train_loop(ts_data, mctes_data, model, sc_params, seed = 100):
    """
    """     
    # exp_clf101 = setup(data = ts_data, target = 'label', session_id=seed, train_size=0.8, silent=True, verbose=False)
    exp_clf101 = setup(data = ts_data, target = 'label', session_id=seed, test_data=mctes_data, \
        numeric_features=['D', 'R', 'W'], preprocess=False)
    # ---for xgb
    if model == 'xgb':
        bxgb = create_model('xgboost', verbose=False)
    elif model == 'lr':
        bxgb = create_model(LogisticRegression(solver='liblinear', class_weight='balanced'))
    
    if sc_params:
        tuned_bxgb = tune_model(bxgb, choose_better = True, n_iter=200, custom_grid = sc_params, optimize='AUC', \
            search_library='scikit-learn', search_algorithm='random', fold=5, return_train_score=True)
    else:
        tuned_bxgb = tune_model(bxgb, choose_better = True, n_iter=200, optimize='AUC', fold=5, return_train_score=True)
    sc_tradev_rlts = pull()
    print('---search parameter model cv results---', sc_tradev_rlts)
    
    xgb_imtfeats = pd.DataFrame({'Feature': get_config('X_train').columns, 'Value' : \
            abs(tuned_bxgb.feature_importances_)}).sort_values(by='Value', ascending=False)[:150]
    
    print('---go into test phrase---')
    _ = predict_model(tuned_bxgb, data=mctes_data, verbose=False, raw_score=True)
    test_results = pull()
    xgbauc_mcvals = round(test_results['AUC'].values[0], 4)
    print('---test auc results---', xgbauc_mcvals)
    
    return tuned_bxgb, ((xgbauc_mcvals, xgbauc_mcvals), []), xgb_imtfeats


def searchconf_exps(datas, model_path):
    """
    datas: dict
    """
    sc_paramsdp = {'learning_rate': [0.01, 0.03, 0.05], 'n_estimators': [100, 300, 500], \
                'reg_lambda': [4.0, 6.0, 8.0], 'max_bin': [10, 20, 50],  'reg_alpha': [1, 2, 3], 'scale_pos_weight': [1.0, 2.5], \
                    'max_depth': [3, 4, 5, 6], 'subsample': [0.8, 0.9], 'colsample_bytree': [0.1, 0.2, 0.4], 'colsample_bynode': [0.6, 0.8], \
                        'min_child_weight': [3, 5, 7]}

    sc_paramssha = {'learning_rate': [0.02, 0.05, 0.1], 'n_estimators': [80, 100, 200, 600], \
                'reg_lambda': [2.0, 3.0, 4.0], 'max_bin': [10, 20, 50],  'reg_alpha': [1, 2, 3], 'scale_pos_weight': [1.0, 2.5], \
                    'max_depth': [2, 3, 5, 6], 'subsample': [0.8, 0.9], 'colsample_bytree': [0.4, 0.5, 0.6, 0.8], \
                        'min_child_weight': [3, 5, 7]}

    all_evalresults = collections.defaultdict(dict)
    for cmbmc_id in datas:
        for feat_tsname, (raw_traindata, mctes_data) in datas[cmbmc_id].items():
            print('--configuration---', cmbmc_id, feat_tsname, raw_traindata.shape, mctes_data.shape, mctes_data.shape)
            print('--label distribution---', raw_traindata[abs(raw_traindata['label'] - 1.0) < 1e-6].shape, \
                mctes_data[abs(mctes_data['label'] - 1.0) < 1e-6].shape, \
                    mctes_data[abs(mctes_data['label'] - 1.0) < 1e-6].shape)
            if raw_traindata.shape[1] >= 500:
                sc_params = sc_paramsdp
            else:
                sc_params = sc_paramssha
            pos_ratio = raw_traindata[abs(raw_traindata['label']) < 1e-6].shape[0] / raw_traindata[abs(raw_traindata['label'] - 1.0) < 1e-6].shape[0]
            sc_params['scale_pos_weight'] = sc_params['scale_pos_weight'] + [pos_ratio]

            tuned_bxgb, (xgbauc_vals, eval_looprlts), xgb_imtfeats = train_loop(raw_traindata, mctes_data, 'xgb', sc_params)
            
            all_evalresults[cmbmc_id][feat_tsname] = (tuned_bxgb.get_params(), (cmbmc_id, xgbauc_vals), \
                eval_looprlts, list(xgb_imtfeats['Feature'].values))
            
            model_name = '%s_%s_%s' % (model_path, cmbmc_id, feat_tsname)
            save_model(tuned_bxgb, model_name)

    return all_evalresults


def create_tradev_dataset(exp_config, label_genpath, feat_dir):
    """
    """
    # label_genpath = '../dataset/DIAQC_ML_20221221/data4xgb/labels_1222.csv'
    label_dataset = pd.read_csv(label_genpath)

    # feat_dir = '../dataset/DIAQC_ML_20221221/2_features_info/'
    _, (mglc_featdatas, mgms_featdatas) = create_data.read_dataset(feat_dir)
    mglc_featdatas_feattrans = feat_trans.preprocess_feats(mglc_featdatas, exp_config)
    mgms_featdatas_feattrans = feat_trans.preprocess_feats(mgms_featdatas, exp_config)
    cv_datas = create_data.split_iteml_dataset(mglc_featdatas_feattrans, mgms_featdatas_feattrans, label_dataset, test_size=0.2)
    
    def process_label(in_data, feat_names):
        """
        """
        in_data = in_data.drop(columns=['machine_tpid', 'machine_id', 'Run_ID'])
        in_data = in_data.apply(lambda x: x.astype(np.float32) if 'labels' not in x.name else x, axis=0)
        print('--after one hot data shape is---', in_data.shape)
        # label process
        labels_tps = in_data.pop('%s_labels' % exp_config['task_name'])
        labels = labels_tps.apply(lambda x: float(json.loads(x)['vt_label']) if exp_config.label_type == 'vt' \
            else json.loads(x)['count'])
        if exp_config.label_type == 'wt':
            labels = labels.apply(lambda x: 0.0 if sum(np.array([float(t) for t in x]) * exp_config.weight_label) / 3 > 0.5 else 1.0)
        in_data['%s_label' % exp_config['task_name']] = labels

        allfeat_labels = in_data.pop('feat_labels')
        for feat_name in feat_names:
            feat_label = allfeat_labels.apply(lambda x: json.loads(x)[feat_name])
            feat_label = feat_label.apply(lambda x: float(json.loads(x)['vt_label']) if exp_config.label_type == 'vt' \
                else json.loads(x)['count'])
            if exp_config.label_type == 'wt':
                feat_label = feat_label.apply(lambda x: 0.0 if sum(np.array([float(t) for t in x]) * exp_config.weight_label) / 3 > 0.5 else 1.0)

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
    
    raw_train, raw_test = cv_datas[exp_config['task_name']]['uniform_sample']
    raw_train = process_label(raw_train, all_feats_ids)
    raw_test = process_label(raw_test, all_feats_ids)
    
    for feat_name in [exp_config['task_name']] + all_feats_ids:
        if feat_name == exp_config['task_name']:
            rel_clsm = [name for name in list(raw_train.columns) if not ('_label' in name and exp_config['task_name'] not in name)]
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
        trates_datasets['uniform_sample'][feat_name] = (feat_raw_train, feat_raw_test)
        
        print('----------the feat:', feat_name, '--test data shape is---', feat_raw_train.shape, feat_raw_test.shape)

    return trates_datasets


if __name__ == '__main__':
    # read dataset with preprocess
    model_output_dir = '/home/niezongxiang/run_code/massspectro_pred/dataset/models_20240104_unisplit'
    label_genpath = '/home/niezongxiang/run_code/massspectro_pred/dataset/labels_1222.csv'
    feat_dir = '/home/niezongxiang/run_code/massspectro_pred/dataset/2_features_info'
    if not os.path.exists(model_output_dir):
        os.makedirs(model_output_dir)

    exp_config = dict(
        model_path=model_output_dir + '/lc_',
        task_name='lc',
        naratio_thre=0.3,
        fillna_md='min',
        label_type='vt',
    )
    exp_config = DotMap(exp_config)
    trates_datasets = create_tradev_dataset(exp_config, label_genpath, feat_dir)
    all_evalresults = searchconf_exps(trates_datasets, exp_config['model_path'])
    print('*****************************************************')

    exp_config = dict(
        model_path=model_output_dir + '/ms_',
        task_name='ms',
        naratio_thre=0.3,
        fillna_md='min',
        label_type='vt',
    )
    exp_config = DotMap(exp_config)
    trates_datasets = create_tradev_dataset(exp_config, label_genpath, feat_dir)
    all_evalresults = searchconf_exps(trates_datasets, exp_config['model_path'])


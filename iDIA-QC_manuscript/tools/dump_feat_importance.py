import collections
import os
import sys

import pandas as pd
from pycaret.classification import *

sys.path.append('../')


def load_models(model_dir):
    """
    加载文件夹下所有的模型文件，并且能够和数据集建立对应关系
    """
    models = collections.defaultdict(dict)
    for name in os.listdir(model_dir):
        name = name.replace('.pkl', '')
        name_cp = name.replace('lc__', '')
        name_cp = name_cp.replace('ms__', '')
        name_parts = [partn for partn in name_cp.split('_') if partn]
        feat_name = name_parts[-1]
        dataset_name = u'_'.join(name_parts[:-1])
        mpath = os.path.join(model_dir, name.replace('.pkl', ''))
        model = load_model(mpath)
        models[dataset_name][feat_name] = model
    print('---model keys---', list(models.keys()))
    return models


def dump_feat_importance(models, feats_rank_dir):
    """
    加载模型, 输出模型重要性排序
    """
    # 
    for dataset_name in models:
        for feat_name in models[dataset_name]:
            model = models[dataset_name][feat_name]
            xgb_model = model.named_steps["trained_model"]

            xgb_imtfeats = pd.DataFrame({'Feature': xgb_model.get_booster().feature_names, 'Value' : \
                abs(xgb_model.feature_importances_)}).sort_values(by='Value', ascending=False)
            out_path = os.path.join(feats_rank_dir, u'_'.join([dataset_name, feat_name]) + '.csv')
            xgb_imtfeats.to_csv(out_path, index=False)

    return True, 'OK'


if __name__ == '__main__':
    # read dataset with preprocess
    test_type = 'mc_split'
    task_name = 'ms'
    exp_config = dict(\
        model_path='../dataset/DIAQC_ML_20221221/data4xgb/models_mcsplit/',
        feats_rank_dir='../dataset/DIAQC_ML_20221221/data4xgb/feat_ranks/', 
        task_name=task_name,
        test_type=test_type,
        naratio_thre=0.3,
        fillna_md='min',
        label_type='vt',
    )
    from dotmap import DotMap
    exp_config = DotMap(exp_config)
    models = load_models(exp_config['model_path'])
    dump_feat_importance(models, exp_config['feats_rank_dir'])
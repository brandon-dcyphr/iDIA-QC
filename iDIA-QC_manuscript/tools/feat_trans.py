"""
数据预处理、特征变换
"""
import copy
import os

import pandas as pd
from sklearn.preprocessing import Normalizer, MinMaxScaler


def preprocess_feats(in_data, conf):
    """
    特征数据预处理: na
    """
    def nainc_clms(name):
        return True if 'labels' not in name and 'machine' not in name else False
    
    print('---preprocess feat----', conf, in_data.shape)
    rc_data = copy.deepcopy(in_data)
    # feature preprocess
    max_number_of_nas = in_data.shape[0] * conf.naratio_thre
    rc_data = rc_data.loc[:, (rc_data.isnull().sum(axis=0) <= max_number_of_nas)]
    print('---preprocess feat after filter na ration----', rc_data.shape)
    if conf.fillna_md == 'min':
        rc_data = rc_data.apply(lambda x: x.fillna(x.min()) if nainc_clms(x.name) else x, axis=0)
    elif conf.fillna_md == 'median':
        rc_data = rc_data.apply(lambda x: x.fillna(x.median()) if nainc_clms(x.name) else x, axis=0)
    elif conf.fillna_md == 'mean':
        rc_data = rc_data.apply(lambda x: x.fillna(x.mean()) if nainc_clms(x.name) else x, axis=0)
    else:
        print('----no method to fill---')
    
    # 特殊列的处理, replace %
    rc_data = rc_data.apply(lambda x: x.replace('%', '', regex=True) if ('_percent' in x.name or 'Intensity_variation' in x.name) else x, axis=0)

    # print('---preprocess_feats--', rc_data.head(3))
    return rc_data


def trans_feats(tra_dataset, test_dataset, fttrans_confs):
    """
    特征变换
    trans_confs: 不同特征对应的变换不一样(手工创建), key: (trans_type, trans_function), value: feature name list
    trans_type: fit(for dl or lr), nonfit(xgb)
    """
    for (trans_type, trans_func), feat_names in fttrans_confs.items():
        if trans_type == 'nonfit':
            tra_dataset = tra_dataset.apply(lambda x: trans_func(x) if x.name in feat_names else x, axis=0)
            test_dataset = test_dataset.apply(lambda x: trans_func(x) if x.name in feat_names else x, axis=0)
        elif trans_type == 'fit':
            if feat_names == None:
                feat_names = list(tra_dataset.columns)
            if trans_func == 'normalizer':
                transformer = Normalizer().fit(tra_dataset[feat_names])
                tra_dataset[feat_names] = transformer.transform(tra_dataset[feat_names])
                test_dataset[feat_names] = transformer.transform(test_dataset[feat_names])
            elif trans_func == 'minmax_scale':
                transformer = MinMaxScaler().fit(tra_dataset[feat_names])
                tra_dataset[feat_names] = transformer.transform(tra_dataset[feat_names])
                test_dataset[feat_names] = transformer.transform(test_dataset[feat_names])
    
    return tra_dataset, test_dataset


if __name__ == '__main__':
    # generate the feature type and feature name mapping configuration
    data_dir = ''
    afeatf_names = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
    afeatf_names = sorted(afeatf_names)
    
    featf_feats = {}
    for ff_name in afeatf_names:
        f_name = ff_name.split('_')[1]
        featf_feats[f_name] = list(pd.read_csv(os.path.join(data_dir, ff_name)).columns)
        
    feat_trans_maps = {}
    feat_trans_maps[('fit', 'normalizer')] = None


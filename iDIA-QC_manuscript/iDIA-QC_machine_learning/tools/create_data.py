"""
划分训练测试数据集
- base数据集
- 特定机器数据集划分

数据集格式:
- LC:  feat1, feat2, ..., mv_label, proba_label, label_dist
"""
import os
import sys
import copy
import re
import collections
import json
import traceback
import pandas as pd
import numpy as np
import sklearn
import sklearn.model_selection

sys.path.append('../')


def read_dataset(data_dir):
    """
    read raw dataset with two format, store by feature and merge by runid
    data_dir: feature dataset dir
    """
    def read_raw_data(ff_name):
        f_name = ff_name.split('_')[1]
        subdata = pd.read_csv(os.path.join(data_dir, ff_name))
        # add sub_feature suffix f_name, except Run_ID
        clms_mapper = {}
        for clm_name in list(subdata.columns):
            if clm_name == 'Run_ID':
                clms_mapper[clm_name] = clm_name
            else:
                clms_mapper[clm_name] = u'_'.join([clm_name, f_name])
        subdata = subdata.rename(columns=clms_mapper)
        return subdata

    afeatf_230_names = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f)) and f.startswith('DIAQC203')]
    afeatf_230_names = sorted(afeatf_230_names)

    afeatf_2435_names = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f)) and f.startswith('DIAQC2435')]
    afeatf_2435_names = sorted(afeatf_2435_names)

    lcfeats_ids = [ 'F1', 'F2', 'F3']
    msfeats_ids = []
    for idx in range(4, 16):
        msfeats_ids.append('F%d' % idx)

    lc_featdatas, ms_featdatas = {}, {}
    for idx, ff_name in enumerate(afeatf_230_names):
        f_name = ff_name.split('_')[1]
        subdata_230 = read_raw_data(ff_name)
        subdata_2435 = read_raw_data(afeatf_2435_names[idx])
        if subdata_230.shape[1] != subdata_2435.shape[1]:
            print('---error data feature shape is not the same---', ff_name, subdata_230.shape[1], subdata_2435.shape[1])
        subdata = pd.concat([subdata_2435, subdata_230])
        subdata.index = list(range(subdata.shape[0]))
        if f_name in lcfeats_ids:
            lc_featdatas[f_name] = subdata
        elif f_name in msfeats_ids:
            ms_featdatas[f_name] = subdata

    def merge_feats(infeat_datas, feats_ids):
        """
        """
        feat_datas = infeat_datas[feats_ids[0]]
        for ff_name in feats_ids[1:]:
            try:
                ff_data = infeat_datas[ff_name]
                feat_datas = feat_datas.merge(ff_data, how='inner', on='Run_ID')
            except:
                print('--error---', feats_ids, ff_name)
                print(ff_data.head(2))
                print(traceback.format_exc())
                sys.exit(1)
        return feat_datas
    
    mglc_featdatas = merge_feats(lc_featdatas, lcfeats_ids)
    mgms_featdatas = merge_feats(ms_featdatas, msfeats_ids)

    print('---after inner merge, lc data shape is---', mglc_featdatas.shape)
    print('---after inner merge, ms data shape is---', mgms_featdatas.shape)

    return (lc_featdatas, ms_featdatas), (mglc_featdatas, mgms_featdatas)


def gen_machineid_test(indata):
    """
    产生机器类型id类测试数据集的枚举: 先产生一些base, 规则:
    - 总数在0.2左右
    - 在本类型中的数据量也小于20%(20%左右)
    """
    combinations = [['D13', 'R08', 'R18', 'W06'], ['D16', 'R09', 'R18', 'W14'], ['D16', 'R12', 'R18', 'W14']]
    tratest_datas = {}
    for mcid_com in combinations:
        tcdata = indata[indata['machine_id'].isin(mcid_com)]
        tradata = indata[~(indata['machine_id'].isin(mcid_com))]
        tratest_datas[u'_'.join(mcid_com)] = (tradata, tcdata)
    return tratest_datas


def split_iteml_dataset(mglc_featdata, mgms_featdata, label_dataset, test_size=0.2):
    """
    target: item level的训练
    - combine feat and label data
        - voting data
        - wt data
    - split the dataset
        - uniform split
        - split based machine id
    - return: dict
    """
    cv_datas = {'lc': {}, 'ms': {}}
    feat_datas = {'lc': mglc_featdata, 'ms': mgms_featdata}

    for ts_type in ['lc', 'ms']:
        data = feat_datas[ts_type]
        if ts_type == 'lc':
            tstp_lbdata = copy.deepcopy(label_dataset[['Run_ID', 'lc_labels', 'feat_labels']])
        else:
            tstp_lbdata = copy.deepcopy(label_dataset[['Run_ID', 'ms_labels', 'feat_labels']])
        
        mgdata = data.merge(tstp_lbdata, how='inner', on='Run_ID')
        mgdata['machine_tpid'] = mgdata['Run_ID'].apply(lambda x: x[0])
        mgdata['machine_id'] = mgdata['Run_ID'].apply(lambda x: re.sub('U[0-9]+', '', x))
        # add one hot feature
        mgdata = pd.concat([mgdata, pd.get_dummies(mgdata['machine_tpid'])], axis=1)
        # mgdata = pd.concat([mgdata, pd.get_dummies(mgdata['machine_id'])], axis=1)
        print('--raw columns after dummy', mgdata.columns)
        # split, here or other in trian loop, one baseline format
        train, test = sklearn.model_selection.train_test_split(mgdata, test_size=test_size, random_state=100)
        cv_datas[ts_type]['uniform_sample'] = (train, test)
        # only using this
        cv_datas[ts_type]['sample_machineid'] = gen_machineid_test(mgdata)
    
    return cv_datas


def split_time_dataset(mglc_featdata, mgms_featdata, label_dataset, test_size=0.2):
    """
    split dataset using time
    """
    cv_datas = {'lc': {}, 'ms': {}}
    feat_datas = {'lc': mglc_featdata, 'ms': mgms_featdata}

    for ts_type in ['lc', 'ms']:
        data = feat_datas[ts_type]
        if ts_type == 'lc':
            tstp_lbdata = copy.deepcopy(label_dataset[['Run_ID', 'lc_labels', 'feat_labels']])
        else:
            tstp_lbdata = copy.deepcopy(label_dataset[['Run_ID', 'ms_labels', 'feat_labels']])
        
        mgdata = data.merge(tstp_lbdata, how='inner', on='Run_ID')
        mgdata['machine_tpid'] = mgdata['Run_ID'].apply(lambda x: x[0])
        mgdata['machine_id'] = mgdata['Run_ID'].apply(lambda x: re.sub('U[0-9]+', '', x))
        # add one hot feature
        mgdata = pd.concat([mgdata, pd.get_dummies(mgdata['machine_tpid'])], axis=1)
        # mgdata = pd.concat([mgdata, pd.get_dummies(mgdata['machine_id'])], axis=1)
        print('--raw columns after dummy', mgdata.columns)
        # split, using time stamp
        train = pd.DataFrame()
        test = pd.DataFrame()
        for key, item_data in mgdata.groupby('machine_id'):
            item_data = item_data.sort_values(by=['Run_ID'])
            total_count = item_data.shape[0]
            train_count = total_count - int(total_count * test_size)
            train = pd.concat([train, item_data.iloc[:train_count, :]])
            test = pd.concat([test, item_data.iloc[train_count:, :]])
        # only using this
        train = sklearn.utils.shuffle(train)
        test = sklearn.utils.shuffle(test)
        cv_datas[ts_type]['time_split'] = (train, test)
    
    return cv_datas


def split_mtg_dataset(mglc_featdata, mgms_featdata, label_dataset, feat_conf, test_size=0.2):
    """
    feat_conf: group feat(F1 ....) and related subfeature list
    多任务学习的训练数据集合并和切分:
    - lc
        - feature data and label
        - cmbfeature and label
    """
    cv_datas = {'lc': {}, 'ms': {}}
    feat_datas = {'lc': mglc_featdata, 'ms': mgms_featdata}
    
    for ts_type in ['lc', 'ms']:
        data = feat_datas[ts_type]
        mgdata = data.merge(label_dataset, how='inner', on='Run_ID')
        mgdata['machine_tpid'] = mgdata['Run_ID'].apply(lambda x: x[0])
        mgdata['machine_id'] = mgdata['Run_ID'].apply(lambda x: re.sub('U[0-9]+', '', x))
        # add one hot feature
        mgdata = pd.concat([mgdata, pd.get_dummies(mgdata['machine_tpid'])], axis=1)
        # train dev split
        train, test = sklearn.model_selection.train_test_split(mgdata, test_size=test_size, random_state=10000)
        
        for gp_ftname, feature_list in feat_conf[ts_type]:
            label_name = '%s_labels' % gp_ftname
            feature_list = list(set(feature_list) & set(list(train.columns)))
            subtrain = train[feature_list + [label_name]]
            subtest = test[feature_list + [label_name]]
            cv_datas[ts_type][gp_ftname] = (subtrain, subtest)

    return cv_datas



if __name__ == '__main__':
    # read raw dataset
    
    # LC dataset

    # MS dataset
    pass
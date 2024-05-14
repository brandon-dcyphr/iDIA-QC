import os
import time

import numpy as np
import pandas as pd
import scipy.interpolate as spi

from applet.obj.Entity import FileInfo
from applet.service import common_service

base_val_min_count = 100


class S5Service(common_service.CommonService):

    def __init__(self, base_output_path, output_dir_s5, output_file_S5_ms1_chazi, s4_file_path, file_list: [FileInfo],
                 logger, step=7, pub_channel='analysis_info', start_time=0):
        common_service.CommonService.__init__(self, base_output_path, file_list, logger, step, pub_channel, start_time)
        self.s4_file_path = s4_file_path
        self.s5_output_file_path = os.path.join(self.base_output_path, output_dir_s5)
        self.output_file_S5_ms1_chazi = output_file_S5_ms1_chazi

    # S5的插值计算，是进行了两段的筛选
    def deal_process(self):
        logger = self.logger
        try:
            self.send_msg(0, '')
            if not os.path.exists(self.s5_output_file_path):
                os.mkdir(self.s5_output_file_path)

            result_tsv_writer_path = self.s4_file_path
            chazi_file_path = os.path.join(self.s5_output_file_path, self.output_file_S5_ms1_chazi)
            logger.info('deal S5 process, s5_chazi_file_path is: {}'.format(chazi_file_path))

            ms1_file_x = pd.read_csv(result_tsv_writer_path, sep='\t')
            ms1_file_x['file'] = ''
            df_run = list(ms1_file_x['Run name'])
            ms1_file_x['file'] = df_run
            #  计算MS1插值
            all_data = pd.DataFrame()

            for run_info in self.file_list:
                # self.send_msg(9, 'Deal S5: {}'.format(run_info.run_name))
                file_tmp = ms1_file_x[ms1_file_x['file'] == run_info.run_name]
                if len(file_tmp) == 0:
                    continue
                file_tmp = file_tmp[file_tmp['mslevel']
                                    == 1].reset_index(drop=True)
                file_tmp = file_tmp.drop_duplicates()

                tmp_x = list(file_tmp['scan.num'])

                Y = np.array(file_tmp['totIonCurrent'])

                tmp_x, Y = filter_data(tmp_x, Y)

                X = np.array(
                    [((i - min(tmp_x)) / (max(tmp_x) - min(tmp_x))) * 999 for i in tmp_x])
                new_x = np.arange(min(X), max(X), ((max(X) - min(X))) / 1000)
                # 进行三次样条拟合
                ipo1 = spi.splrep(X, Y, k=1)  # 样本点导入，生成参数
                iy1 = spi.splev(new_x, ipo1)  # 根据观测点和样条参数，生成插值

                iy_tmp = pd.DataFrame(iy1, columns=[run_info.run_name])
                all_data = pd.concat([all_data, iy_tmp], axis=1)
            all_data.to_csv(chazi_file_path, index=False)
            logger.info('end S5 process, s5_chazi_file_path is: {}'.format(chazi_file_path))
            self.send_msg(1, '')
            return True
        except Exception as e:
            logger.exception('Deal S5 exception')
            self.send_msg(3, 'Deal S5 exception: {}'.format(e))
            return False
        finally:
            self.is_running = False


def find_start_index(data, base_val):
    three_base_val = base_val * 3
    # 从0开始吧
    start_index = 0
    count = 0
    for index in range(len(data)):
        if count > base_val_min_count:
            break
        if data[index] > three_base_val:
            count += 1
            if start_index == 0:
                # 记录一下开始点就行
                start_index = index
        else:
            count = 0
            start_index = 0
    return start_index


# 这个逻辑和start一样，只不过是从后面找，倒反天罡
def find_end_index(data, base_val):
    three_base_val = base_val * 3
    # 从0开始吧，如果找不到这样的点，就取原始值
    end_index = 0
    count = 0
    for index in range(len(data)):
        if count > base_val_min_count:
            break
        if data[len(data) - 1 - index] > three_base_val:
            count += 1
            if end_index == 0:
                # 记录一下开始点就行
                end_index = len(data) - 1 - index
        else:
            count = 0
            end_index = 0
    return len(data) - 1 if end_index == 0 else end_index


# 过滤数据
def filter_data(tmp_x, data):
    # 这是原始数据，理论上tmp_x和data的数据量是一致的

    # 先取前100个数据的平均值当基准值
    base_val = np.mean(data[:100])

    # 找到连续的100个点大于该基准值的开始点
    start_index = find_start_index(data, base_val)
    end_index = find_end_index(data, base_val)
    if end_index < start_index:
        end_index = len(data) - 1
    print('start_index = {}, end_index = {}'.format(start_index, end_index))
    # 取start和end之间的数据，由于计算不包括开始的点，这个点无所谓了吧
    tmp_x_new = tmp_x[start_index: end_index]
    data_new = data[start_index: end_index]
    return tmp_x_new, data_new

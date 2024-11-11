import os
import time

import numpy as np
import pandas as pd
import scipy.interpolate as spi

from applet.obj.Entity import FileInfo
from applet.service import common_service


class S6Service(common_service.CommonService):

    def __init__(self, base_output_path,
                 output_dir_s6, output_file_S6_ms1_chazi, output_file_S6_ms2_chazi, output_file_S6_ms1_org_area,
                 output_file_S6_ms2_org_area, output_file_S6_ms1_under_chazi, output_file_S6_ms2_under_chazi,
                 s4_file_path, file_list: [FileInfo], logger, step=8, pub_channel='analysis_info', start_time=0):
        common_service.CommonService.__init__(self, base_output_path, file_list, logger, step, pub_channel, start_time)
        self.s4_file_path = s4_file_path

        self.s6_output_path = os.path.join(self.base_output_path, output_dir_s6)
        self.ms1_chazi_file_path = os.path.join(self.s6_output_path, output_file_S6_ms1_chazi)
        self.ms2_chazi_file_path = os.path.join(self.s6_output_path, output_file_S6_ms2_chazi)
        self.ms1_org_area_file_path = os.path.join(self.s6_output_path, output_file_S6_ms1_org_area)
        self.ms2_org_area_file_path = os.path.join(self.s6_output_path, output_file_S6_ms2_org_area)
        self.ms1_under_chazi_file_path = os.path.join(self.s6_output_path, output_file_S6_ms1_under_chazi)
        self.ms2_under_chazi_file_path = os.path.join(self.s6_output_path, output_file_S6_ms2_under_chazi)

    #
    def deal_process(self):
        logger = self.logger
        try:
            self.is_running = True
            logger.info('start deal S6 process')
            self.send_msg(0, 'Processing the S6 step to do linear interpolation', with_time=True)

            if not os.path.exists(self.s6_output_path):
                os.makedirs(self.s6_output_path)
            s4_result_file_path = self.s4_file_path
            ms_file_x = pd.read_csv(s4_result_file_path, sep='\t')
            ms_file_x['file'] = ''
            df_run = list(ms_file_x['Run name'])
            ms_file_x['file'] = df_run

            #
            logger.info('start deal S6 process, calc_ms1_chazi')
            # self.send_msg(9, 'Start deal S6 process, calc ms1 chazi')
            calc_ms1_chazi(ms_file_x, self.file_list, self.ms1_chazi_file_path)
            self.send_msg(9, '{} Finished the linear interpolation of MS1'.format(self.get_now_use_time()))

            #
            logger.info('start deal S6 process, calc_ms2_chazi')
            # self.send_msg(9, 'Start deal S6 process, calc ms2 chazi')
            calc_ms2_chazi(ms_file_x, self.file_list, self.ms2_chazi_file_path)
            self.send_msg(9, '{} Finished the linear interpolation of MS2'.format(self.get_now_use_time()))

            #
            logger.info('start deal S6 process, calc_ms1_org_area')
            # self.send_msg(9, 'Start deal S6 process, calc ms1 org area')
            calc_ms1_org_area(ms_file_x, self.file_list, self.ms1_org_area_file_path)
            self.send_msg(9, '{} Calculating the MS1 area'.format(self.get_now_use_time()))

            logger.info('start deal S6 process, calc_ms2_org_area')
            # self.send_msg(9, 'Start deal S6 process, calc ms2 org area')
            calc_ms2_org_area(ms_file_x, self.file_list, self.ms2_org_area_file_path)
            self.send_msg(9, '{} Calculating the MS2 area'.format(self.get_now_use_time()))

            #
            logger.info('start deal S6 process, under_calc_ms1_chazi')
            # self.send_msg(9, 'Start deal S6 process, under calc ms1 chazi')
            under_calc_ms1_chazi(ms_file_x, self.file_list, self.ms1_chazi_file_path, self.ms1_under_chazi_file_path)
            logger.info('start deal S6 process, under_calc_ms2_chazi')
            # self.send_msg(9, 'Start deal S6 process, under calc ms2 chazi')
            under_calc_ms2_chazi(ms_file_x, self.file_list, self.ms2_chazi_file_path, self.ms2_under_chazi_file_path)
            logger.info('end deal S6 process')
            self.send_msg(1, 'Finished the F4 extraction', with_time=True)
            return True
        except Exception as e:
            logger.exception('Deal S6 exception')
            self.send_msg(3, 'Exception deal S6: {}'.format(e))
            return False
        finally:
            self.is_running = False


#
def calc_ms1_chazi(ms_file_x, file_list: [FileInfo], ms1_chazi_file_path):
    all_data = pd.DataFrame()
    for run_info in file_list:
        file_tmp = ms_file_x[ms_file_x['file'] == run_info.run_name]
        if len(file_tmp) == 0:
            continue
        file_tmp = file_tmp[file_tmp['mslevel']
                            == 1].reset_index(drop=True)
        file_tmp = file_tmp.drop_duplicates()
        tmp_x = list(file_tmp['scan.num'])
        X = np.array(
            [((i - min(tmp_x)) / (max(tmp_x) - min(tmp_x))) * 999 for i in tmp_x])
        Y = np.array(file_tmp['totIonCurrent'])

        new_x = np.arange(min(X), max(X), ((max(X) - min(X))) / 1000)
        #
        ipo1 = spi.splrep(X, Y, k=1)
        iy1 = spi.splev(new_x, ipo1)
        iy_tmp = pd.DataFrame(iy1, columns=[run_info.run_name])
        all_data = pd.concat([all_data, iy_tmp], axis=1)

    all_data.to_csv(ms1_chazi_file_path, index=False)
    return ms1_chazi_file_path


#
def calc_ms2_chazi(ms_file_x, file_list: [FileInfo], ms2_chazi_file_path):
    all_data = pd.DataFrame()
    for run_info in file_list:
        file_tmp = ms_file_x[ms_file_x['file'] == run_info.run_name]
        if len(file_tmp) == 0:
            continue
        file_tmp = file_tmp[file_tmp['mslevel'] == 2].reset_index(drop=True)
        file_tmp = file_tmp.drop_duplicates()
        tmp_x = list(file_tmp['scan.num'])
        X = np.array(
            [((i - min(tmp_x)) / (max(tmp_x) - min(tmp_x))) * 9999 for i in tmp_x])
        Y = np.array(file_tmp['totIonCurrent'])
        new_x = np.arange(min(X), max(X), ((max(X) - min(X))) / 10000)
        #
        ipo1 = spi.splrep(X, Y, k=1)  #
        iy1 = spi.splev(new_x, ipo1)  #
        iy_tmp = pd.DataFrame(iy1, columns=[run_info.run_name])
        all_data = pd.concat([all_data, iy_tmp], axis=1)

    all_data.to_csv(ms2_chazi_file_path, index=False)
    return ms2_chazi_file_path


#
def calc_ms1_org_area(ms_file_x, file_list: [FileInfo], ms1_org_area_file_path):
    all_ms1_area = pd.DataFrame(index=[d.run_name for d in file_list])
    all_ms1_area.index.name = 'Run_name'
    all_ms1_area['area'] = 0.0
    for i in range(len(file_list)):
        run_info = file_list[i]
        file_tmp = ms_file_x[ms_file_x['file'] == run_info.run_name]
        if len(file_tmp) == 0:
            continue
        file_tmp = file_tmp[file_tmp['mslevel'] == 1].reset_index(drop=True)
        file_tmp = file_tmp.drop_duplicates()
        tmp_x = list(file_tmp['scan.num'])
        Y = np.array(file_tmp['totIonCurrent'])
        area_tmp = np.trapz(Y, x=tmp_x)
        all_ms1_area['area'][i] = area_tmp
    all_ms1_area.to_csv(ms1_org_area_file_path)


#
def calc_ms2_org_area(ms_file_x, file_list: [FileInfo], ms2_org_area_file_path):
    all_ms2_area = pd.DataFrame(index=[d.run_name for d in file_list])
    all_ms2_area.index.name = 'Run_name'
    all_ms2_area['area'] = 0.0
    for i in range(len(file_list)):
        run_info = file_list[i]
        file_tmp = ms_file_x[ms_file_x['file'] == run_info.run_name]
        if len(file_tmp) == 0:
            continue
        file_tmp = file_tmp[file_tmp['mslevel'] == 2].reset_index(drop=True)
        file_tmp = file_tmp.drop_duplicates()
        tmp_x = list(file_tmp['scan.num'])
        Y = np.array(file_tmp['totIonCurrent'])
        area_tmp = np.trapz(Y, x=tmp_x)
        all_ms2_area['area'][i] = area_tmp

    all_ms2_area.to_csv(ms2_org_area_file_path)


#
def under_calc_ms1_chazi(ms_file_x, file_list: [FileInfo], ms1_chazi_file_path, ms1_under_chazi_file_path):
    all_data = pd.read_csv(ms1_chazi_file_path)
    area = pd.DataFrame(columns=['Run_name', 'Area'])
    a = []
    for i in range(len(file_list)):
        run_info = file_list[i]
        file_tmp = ms_file_x[ms_file_x['file'] == run_info.run_name]
        if len(file_tmp) == 0:
            continue
        file_tmp = file_tmp[file_tmp['mslevel']
                            == 1].reset_index(drop=True)
        file_tmp = file_tmp.drop_duplicates()
        tmp_x = list(file_tmp['scan.num'])
        X = np.array(
            [((i - min(tmp_x)) / (max(tmp_x) - min(tmp_x))) * 999 for i in tmp_x])
        new_x = np.arange(min(X), max(X), ((max(X) - min(X))) / 1000)
        tmp = list(all_data.iloc[:, i])
        tmp_name = all_data.iloc[:, i].name
        area_tmp = np.trapz(tmp, x=new_x)
        a = pd.DataFrame(data=[tmp_name, area_tmp],
                         index=['Run_name', 'Area']).T
        area = pd.concat([area, a])

    area.to_csv(ms1_under_chazi_file_path, index=False)


def under_calc_ms2_chazi(ms_file_x, file_list, ms2_chazi_file_path, ms2_under_chazi_file_path):
    all_data = pd.read_csv(ms2_chazi_file_path)
    area = pd.DataFrame(columns=['Run_name', 'Area'])

    a = []
    for i in range(len(file_list)):
        run_info = file_list[i]
        # i = 1600
        file_tmp = ms_file_x[ms_file_x['file'] == run_info.run_name]
        if len(file_tmp) == 0:
            continue
        file_tmp = file_tmp[file_tmp['mslevel']
                            == 2].reset_index(drop=True)
        file_tmp = file_tmp.drop_duplicates()
        tmp_x = list(file_tmp['scan.num'])

        X = np.array(
            [((i - min(tmp_x)) / (max(tmp_x) - min(tmp_x))) * 9999 for i in tmp_x])

        new_x = np.arange(min(X), max(X), ((max(X) - min(X))) / 10000)

        tmp = list(all_data.iloc[:, i])

        tmp_name = all_data.iloc[:, i].name

        area_tmp = np.trapz(tmp, x=new_x)

        a = pd.DataFrame(data=[tmp_name, area_tmp],
                         index=['Run_name', 'Area']).T
        area = pd.concat([area, a])

    area.to_csv(ms2_under_chazi_file_path, index=False)

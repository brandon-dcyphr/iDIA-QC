import json
import os
import shutil
import time
from threading import Thread

from pubsub import pub

from applet import logger_utils
from applet.ai_service.prediction_score_service import PredictionScoreService
from applet.db import db_utils
from applet.default_config import setting
from applet.obj.Entity import FileInfo, FileTypeEnum
from applet.obj.Msg import AnalysisInfoMsg
from applet.service.clear_mzml_service import ClearMzmlService
from applet.service.data_save_service import DataSaveService
from applet.service.diann_analysis_service import DiannAnalysisService
from applet.service.msconvert_service import MSConvertService
from applet.service.mzxml_build_service import MzxmlService
from applet.service.notify_service import NotifyService
from applet.service.pic_service import PicService
from applet.service.s3_service import S3Service
from applet.service.s4_service import S4Service
from applet.service.s5_service import S5Service
from applet.service.s6_service import S6Service
from applet.utils import convert_utils
from applet.utils import file_utils


class AnalysisMonitorThread(Thread):
    def __init__(self, monitor_dir_list, inst_name, run_prefix, scan_time, interval_time, msconvert_path, diann_path,
                 output_path,
                 model_dir_path, notify_email, wx_token, file_filter_size, filter_type, filter_file_name):
        Thread.__init__(self)
        self.monitor_dir_list = monitor_dir_list
        logger_path, logger = logger_utils.get_current_logger()
        self.logger = logger
        self.logger_path = logger_path
        self.inst_name = inst_name
        self.run_prefix = run_prefix
        self.scan_time = scan_time
        self.interval_time = interval_time
        self.msconvert_path = msconvert_path
        self.diann_path = diann_path
        self.output_path = output_path
        self.pre_score_service = PredictionScoreService(model_dir_path, output_path, [], logger)
        self.run_flag = True
        self.notify_email = notify_email
        self.wx_token = wx_token
        if file_filter_size is None:
            self.file_filter_size = 0
        else:
            self.file_filter_size = int(file_filter_size)
        self.filter_type = filter_type
        self.filter_file_name_list = self.format_filter_name(filter_file_name)

    def close_thread(self):
        self.run_flag = False

    def send_msg(self, msg):
        info_msg = AnalysisInfoMsg(0, 9, msg)
        pub.sendMessage('monitor_log', msg=json.dumps(info_msg.__dict__))

    def notify_reload_data(self):
        pub.sendMessage('channel_reload_data', msg='ssss')

    def run(self):
        self.send_msg(
            'Start thread to monitor, monitor path: {}, scan time(sec): {}, interval time(min): {}, file_filter_size = {}(MB), filter_type = {}, file_name = {},log path: {}'.format(
                self.monitor_dir_list, self.scan_time, self.interval_time, self.file_filter_size, self.filter_type,
                self.filter_file_name_list, self.logger_path))

        while self.run_flag:
            logger = self.logger
            try:
                time.sleep(self.scan_time)
                self.send_msg('Start scan path: {}'.format(self.monitor_dir_list))
                file_list = self.recursive_scanning()
                file_list = self.filter_file_list(file_list)
                file_list = list(set(file_list))
                wait_deal_file = self.check_wait_deal_file(file_list)
                self.send_msg('There is {} files wait to deal'.format(len(wait_deal_file)))
                if len(wait_deal_file) == 0:
                    continue
                notify_file_list = []
                for index, file_info in enumerate(wait_deal_file):
                    file_name = file_info[0]
                    file_path = file_info[1]
                    try:
                        if not self.run_flag:
                            break
                        run_result = self.process_one_file(file_name, file_path)
                        run_result_flag = run_result[0]
                        if run_result_flag:
                            notify_file_list.append(run_result[1])
                        self.send_msg('process [{}/{}]'.format(index + 1, len(wait_deal_file)))
                    except Exception:
                        self.send_msg('deal file: {} exception'.format(file_path))
                        logger.exception('deal file: {} exception'.format(file_path))


                notify_service = NotifyService(self.notify_email, self.wx_token, self.output_path, notify_file_list, self.logger,
                                               pub_channel='monitor_log')
                notify_service.deal_process()
                self.notify_reload_data()

                self.delete_temp_file()

            except Exception:
                logger.exception('Monitor exception')
                self.send_msg('Monitor exception')
        self.send_msg('Stop to monitor')

    def delete_temp_file(self):
        logger = self.logger
        logger.info('Start clear temp mzXML file.')
        temp_mzml_dir = os.path.join(self.output_path, 'mzXML')
        shutil.rmtree(temp_mzml_dir)
        logger.info('Clear temp mzXML file over.')

    def check_wait_deal_file(self, file_list):
        wait_deal_file = []
        for file_info in file_list:
            file_name = file_info[0]
            file_abs_path = file_info[1]
            out_time_limit = file_utils.is_file_modified_days_out_minute(file_abs_path, self.interval_time)
            if not out_time_limit:
                continue
            thiz_file_size = file_utils.get_file_size(file_abs_path)
            thiz_file_mtime = file_utils.get_file_mtime(file_abs_path)

            exist_file_info = db_utils.query_run_info_by_file_name(file_name, 1)
            if exist_file_info:
                if thiz_file_size is None or thiz_file_mtime is None:
                    continue
                if exist_file_info.file_size == thiz_file_size and exist_file_info.last_modify_time == thiz_file_mtime:
                    continue
            wait_deal_file.append(file_info)
        return wait_deal_file


    def process_one_file(self, file_name, file_abs_path):
        info_msg = AnalysisInfoMsg(0, 0, 'Start deal file {}'.format(file_abs_path))
        pub.sendMessage('monitor_log', msg=json.dumps(info_msg.__dict__))

        thiz_file_size = file_utils.get_file_size(file_abs_path)
        thiz_file_mtime = file_utils.get_file_mtime(file_abs_path)
        choose_file_list = self.build_file_list(file_name, file_abs_path, thiz_file_size, thiz_file_mtime)

        msconvert_service = MSConvertService(self.msconvert_path, self.output_path, choose_file_list, self.logger,
                                             pub_channel='monitor_log')
        all_convert = msconvert_service.deal_process()
        if not all_convert:
            msconvert_service.send_msg(3, 'MSConvert file error, skip. {}'.format(file_abs_path))
            return False
        if not self.run_flag:
            return False
        diann_service = DiannAnalysisService(self.diann_path, self.output_path, choose_file_list,
                                             self.logger,
                                             pub_channel='monitor_log')
        diann_run_result = diann_service.deal_process()
        if not self.run_flag:
            return False
        if not diann_run_result:
            diann_service.send_msg(3, 'DIA-NN run error, skip. {}'.format(file_abs_path))
            return False
        mzxml_build_service = MzxmlService(self.inst_name, self.run_prefix, self.output_path, choose_file_list,
                                           self.logger,
                                           pub_channel='monitor_log')
        mzxml_build_service.deal_process()
        if not self.run_flag:
            return False

        s3_deal_service = S3Service(self.output_path, os.path.join(self.output_path, setting.output_dir_s3),
                                    choose_file_list, self.logger, pub_channel='monitor_log')
        s3_result = s3_deal_service.deal_process()
        if not s3_result:
            s3_deal_service.send_msg(9, 'S3 error, skip. {}'.format(file_abs_path))
            return False
        if not self.run_flag:
            return False
        s4_deal_service = S4Service(self.output_path, os.path.join(self.output_path, setting.output_dir_s4),
                                    os.path.join(self.output_path, setting.output_dir_s4,
                                                 setting.output_file_S4_result), choose_file_list, self.logger,
                                    pub_channel='monitor_log')
        s4_result = s4_deal_service.deal_process()
        if not s4_result:
            s4_deal_service.send_msg(3, msg='S4 error, skip. {}'.format(file_abs_path))
            return False
        if not self.run_flag:
            return False
        s5_deal_service = S5Service(self.output_path, setting.output_dir_s5, setting.output_file_S5_ms1_chazi,
                                    os.path.join(self.output_path, setting.output_dir_s4,
                                                 setting.output_file_S4_result),
                                    choose_file_list, self.logger, pub_channel='monitor_log')
        s5_result = s5_deal_service.deal_process()
        if not s5_result:
            s5_deal_service.send_msg(3, msg='S5 error, skip. {}'.format(file_abs_path))
            return False
        if not self.run_flag:
            return False

        s6_deal_service = S6Service(self.output_path,
                                    setting.output_dir_s6, setting.output_file_S6_ms1_chazi,
                                    setting.output_file_S6_ms2_chazi,
                                    setting.output_file_S6_ms1_org_area, setting.output_file_S6_ms2_org_area,
                                    setting.output_file_S6_ms1_under_chazi, setting.output_file_S6_ms2_under_chazi,
                                    os.path.join(self.output_path, setting.output_dir_s4,
                                                 setting.output_file_S4_result),
                                    choose_file_list, self.logger, pub_channel='monitor_log')
        s6_result = s6_deal_service.deal_process()
        if not s6_result:
            s6_deal_service.send_msg(3, msg='S6 error, skip. {}'.format(file_abs_path))
            return False
        if not self.run_flag:
            return False

        self.clear_service = ClearMzmlService(self.output_path, choose_file_list, self.logger,
                                              pub_channel='monitor_log')
        self.clear_service.deal_process()

        data_save_deal_service = DataSaveService(1, self.output_path,
                                                 os.path.join(self.output_path, setting.output_dir_s3),
                                                 os.path.join(self.output_path, setting.output_dir_s7),
                                                 choose_file_list, self.logger, pub_channel='monitor_log')
        # 解析数据，存储至sqlite
        data_save_deal_service.f4_file_path = s6_deal_service.ms1_chazi_file_path
        data_save_deal_service.f8_file_path = s6_deal_service.ms1_org_area_file_path
        data_save_deal_service.f11_file_path = s6_deal_service.ms2_org_area_file_path
        delete_run_info, save_data_list = data_save_deal_service.build_save_data()

        pred_info_list = self.pre_score_service.deal_prediction_score(save_data_list)

        save_result = data_save_deal_service.deal_data_save(delete_run_info, save_data_list, pred_info_list)
        if not save_result:
            data_save_deal_service.send_msg(3, msg='Save data error, skip. {}'.format(file_abs_path))
        if not self.run_flag:
            return False
        pic_dir_path = os.path.join(self.output_path, 'metric_performance_output')
        if not os.path.exists(pic_dir_path):
            os.mkdir(pic_dir_path)
        pic_deal_service = PicService(self.output_path, None, self.logger, pub_channel='analysis_info')
        draw_result = pic_deal_service.draw_pic_all(1)
        if not draw_result:
            pic_deal_service.send_msg(3, msg='Draw result error, skip. {}'.format(file_abs_path))

        data_save_deal_service.send_msg(9, msg='Start save to csv')
        self.pre_score_service.save_to_csv(self.output_path, 1)
        data_save_deal_service.send_msg(9, msg='End deal file {}'.format(file_abs_path))
        return True, choose_file_list[0]

    def build_file_list(self, file_name, file_abs_path, thiz_file_size, thiz_file_mtime) -> [FileInfo]:
        if file_name.endswith('.RAW') or file_name.endswith('.raw'):
            file_type = FileTypeEnum.RAW
        elif file_name.endswith('.WIFF') or file_name.endswith('.wiff'):
            file_type = FileTypeEnum.WIFF
        elif file_name.endswith('.d') or file_name.endswith('.D'):
            file_type = FileTypeEnum.D
        else:
            return None
        file_info = FileInfo()
        # file_info.inst_name = self.inst_name
        # file_info.run_prefix = self.run_prefix
        # file_info.run_name = self.inst_name

        file_info.file_type = file_type
        file_info.file_path = file_abs_path
        file_info.file_name = convert_utils.convert_to_file_name(file_info.file_path)
        convert_utils.convert_to_mzXML_name(file_info)
        file_info.file_size = thiz_file_size
        file_info.last_modify_time = thiz_file_mtime

        return [file_info]

    def check_file_format(self, file_name: str):
        file_type_list = ['.d', '.raw', '.wiff', '.RAW', '.WIFF']
        for file_type in file_type_list:
            if file_name.endswith(file_type):
                return True
        return False


    def recursive_scanning(self):
        file_list = []
        for monitor_dir in self.monitor_dir_list:
            file_list.extend(self.scan_dir(monitor_dir))
        return file_list

    def scan_dir(self, dir_path):
        file_list = []
        for file_name in os.listdir(dir_path):
            thiz_file_path = os.path.join(dir_path, file_name)
            if os.path.isdir(thiz_file_path):
                if file_name.endswith('.d'):
                    file_list.append((file_name, thiz_file_path))
                else:
                    dir_file_list = self.scan_dir(thiz_file_path)
                    file_list.extend(dir_file_list)
            else:
                if not self.check_file_format(file_name):
                    continue
                file_list.append((file_name, thiz_file_path))
        return file_list

    def filter_file_list(self, file_list):
        self.logger.info('Start filter file, limit file size = {}(MB), filter_type = {}, file_name = {}'.format(
            self.file_filter_size, self.filter_type, self.filter_file_name_list))
        if len(file_list) == 0:
            return file_list
        file_list = self.deal_filter_file_name(file_list)
        file_list = self.filter_file_size(file_list)
        return file_list

    def filter_file_size(self, file_list):
        file_size_limit = self.file_filter_size
        if file_size_limit == 0:
            return file_list
        new_file_list = []
        file_size_limit_byte = file_size_limit * 1024 * 1024
        for file_info in file_list:
            current_file_size = file_utils.get_file_size(file_info[1])
            if current_file_size is None or current_file_size < file_size_limit_byte:
                continue
            new_file_list.append(file_info)
        return new_file_list


    def deal_filter_file_name(self, file_list):
        if len(self.filter_file_name_list) == 0:
            return file_list
        if self.filter_type == 1:
            return self.white_filter(file_list)
        elif self.filter_type == 2:
            return self.black_filter(file_list)
        else:
            return file_list


    def white_filter(self, file_list):
        new_file_list = []
        for file_info in file_list:
            current_file_name = file_info[0]
            for filter_file_name in self.filter_file_name_list:
                if filter_file_name in current_file_name:
                    new_file_list.append(file_info)
                    break
        return new_file_list


    def black_filter(self, file_list):
        remove_list = self.white_filter(file_list)
        return list(set(file_list) - set(remove_list))

    def format_filter_name(self, filter_file_name: str):
        filter_list = []
        if filter_file_name is None:
            return filter_list
        filter_file_name = filter_file_name.strip()
        if len(filter_file_name) == 0:
            return filter_list
        file_name_arr = filter_file_name.split(';')
        for file_name in file_name_arr:
            file_name = file_name.strip()
            if len(file_name) == 0:
                continue
            filter_list.append(file_name)
        return filter_list

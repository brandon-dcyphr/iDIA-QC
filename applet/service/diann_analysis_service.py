# coding:utf-8
"""This module is for mzxml msconvert"""

import os
import shutil
import subprocess
import time

from applet.default_config import setting
from applet.obj.Entity import FileInfo, FileTypeEnum
from applet.service import common_service


class DiannAnalysisService(common_service.CommonService):
    def __init__(self, diann_path, base_output_path, file_list: [FileInfo], logger, step=3,
                 pub_channel='analysis_info', start_time=0):
        common_service.CommonService.__init__(self, base_output_path, file_list, logger, step, pub_channel, start_time)
        self.diann_path = diann_path

    # 处理转换
    def deal_process(self):
        logger = self.logger
        try:
            self.is_running = True
            self.send_msg(0, msg='')
            if len(self.file_list) == 0:
                self.send_msg(3, 'File count is zero, stop')
                return False
            diann_out_path = os.path.join(self.base_output_path, setting.output_dir_s2)
            diann_temp_out_path = os.path.join(diann_out_path, setting.output_dir_s2 + '_temp')
            diann_result_out_path = os.path.join(diann_out_path, setting.output_dir_s2 + '_result')
            logger.info('start diann, file count is: {}'.format(len(self.file_list)))
            if not os.path.exists(diann_out_path):
                os.mkdir(diann_out_path)
            if not os.path.exists(diann_temp_out_path):
                os.mkdir(diann_temp_out_path)
            if not os.path.exists(diann_result_out_path):
                os.mkdir(diann_result_out_path)
            deal_count = 0
            for file_info in self.file_list:
                if not self.run_flag:
                    self.send_msg(2, 'Click stop')
                    return False
                # 根据文件名再创建一个文件夹
                diann_temp_file_out_path = os.path.join(diann_temp_out_path, file_info.base_file_name)
                if not os.path.exists(diann_temp_file_out_path):
                    os.mkdir(diann_temp_file_out_path)

                diann_temp_file_path = os.path.join(diann_temp_file_out_path,
                                                    file_info.base_file_name + '_mainoutput.tsv')
                file_info.diann_temp_file_path = diann_temp_file_path
                diann_temp_stats_file_path = os.path.join(diann_temp_file_out_path,
                                                          file_info.base_file_name + '_mainoutput.stats.tsv')
                file_info.diann_temp_stats_file_path = diann_temp_stats_file_path
                file_info.diann_result_stats_file_path = os.path.join(diann_result_out_path,
                                                                      file_info.base_file_name + '_mainoutput.stats.tsv')

                file_info.diann_result_file_name = file_info.base_file_name + '_mainoutput.tsv'
                file_info.diann_result_file_path = os.path.join(diann_result_out_path, file_info.diann_result_file_name)

                file_info.main_file_relative_path = '{}/{}_result/{}_mainoutput.tsv'. \
                    format(setting.output_dir_s2, setting.output_dir_s2, file_info.base_file_name)
                file_info.stats_file_relative_path = '{}/{}_result/{}_mainoutput.stats.tsv'. \
                    format(setting.output_dir_s2, setting.output_dir_s2, file_info.base_file_name)

                self.deal_one_diann(file_info)
                deal_count += 1
                logger.info(
                    'end diann analysis one, {}/{}'.format(file_info.file_name, deal_count, len(self.file_list)))
                if os.path.exists(file_info.diann_temp_file_path):
                    # 移动文件到result目录下
                    logger.info('copy result file, diann_temp_file_path is: {}, target file path is: {}'.format(
                        file_info.diann_temp_file_path, file_info.diann_result_file_path))
                    # os.system(result_file_mv_cmd)
                    shutil.copyfile(file_info.diann_temp_file_path, file_info.diann_result_file_path)

                    logger.info('copy stats file, diann_temp_stats_file_path is: {}, target file path is: {}'.format(
                        file_info.diann_temp_stats_file_path, file_info.diann_result_stats_file_path))
                    shutil.copyfile(file_info.diann_temp_stats_file_path, file_info.diann_result_stats_file_path)
                    continue
                else:
                    logger.error(
                        'diann error, result file is not exist, file name is: {}, temp file path is: {}'.format(
                            file_info.file_name, file_info.diann_temp_file_path))
                    self.send_msg(3,
                                  msg='DIA-NN error, result file is not exist, file name is: {}, temp file path is: {}'.format(
                                      file_info.file_name, file_info.diann_temp_file_path))
                    return False
            # 检测是否都已经处理完成了
            self.send_msg(1, msg='DIA-NN exited.')
            return True
        except Exception as e:
            logger.exception('deal diann exception')
            self.send_msg(3, msg='Exception deal DIA-NN: {}'.format(e))
            return False
        finally:
            self.is_running = False

    # 处理一个分析
    def deal_one_diann(self, file_info: FileInfo):
        logger = self.logger
        file_type = file_info.file_type
        if file_type == FileTypeEnum.D or file_type == FileTypeEnum.RAW:
            mass_acc_ms1 = 20
        elif file_type == FileTypeEnum.WIFF:
            mass_acc_ms1 = 30
        else:
            logger.error(
                'file type is error, file name is: {}, file_type is: {}'.format(file_info.file_name, file_type))
            return None

        # 如果是raw和wiff，就使用mzml的地址
        if file_type == FileTypeEnum.RAW or file_type == FileTypeEnum.WIFF:
            org_file_path = file_info.mzML_file_path
        elif file_type == FileTypeEnum.D:
            org_file_path = file_info.file_path

        lib_path = setting.get_lib_path_by_file_type(file_info.file_type)
        cmd = '"{}" --f "{}" --lib "{}" --threads 2 --verbose 1 --out "{}" --qvalue 0.01 --matrices ' \
              '--met-excision --cut K*,R* --mass-acc {} --mass-acc-ms1 20 --individual-mass-acc --individual-windows --smart-profiling ' \
              '--pg-level 1 --peak-center --no-ifs-removal'.format(self.diann_path, org_file_path, lib_path,
                                                                   file_info.diann_temp_file_path,
                                                                   mass_acc_ms1)

        self.diann_analysis_one(cmd, file_info)

    # 处理一个分析流程
    def diann_analysis_one(self, cmd, file_info: FileInfo):
        logger = self.logger
        logger.info('diann analysis one, file name is: {}, cmd is: {}'.format(file_info.file_name, cmd))
        self.send_msg(20, '')
        self.send_msg(9, msg='{}'.format(cmd), with_time=True)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, creationflags=134217728)
        stdout = p.stdout
        while True:
            output = stdout.readline()
            if output == b'' or (output == '' and p.poll() is not None):
                break
            logger.info(output)
            if output:
                # 将字节形式的输出转换为字符串形式
                info_msg = output.decode('utf-8')
                info_msg = info_msg.rstrip()
                if len(info_msg) == 0:
                    continue
                if 'files will be processed' in info_msg:
                    info_msg = info_msg + ' separately.'
                # 增加一个处理，如果msg是以时间开头的，那么就得把时间去掉
                if '] ' in info_msg:
                    info_msg = info_msg[info_msg.index('] ') + 2:]
                self.send_msg(9, msg='{}'.format(info_msg), with_time=True)
        self.send_msg(21, '')

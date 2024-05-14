import configparser
import os.path

from applet.logger_utils import logger
from applet.obj.Entity import FileTypeEnum


class Setting(object):
    def __init__(self):
        conf = Setting.load_config()

        current_path = os.getcwd()

        self.diann_wiff_lib_path = os.path.join(current_path,
                                                'DIAQC_spectral_library_fasta\\Library_FinalPanMouse_v2_FinalWithoutDecoys.tsv')
        self.diann_raw_lib_path = os.path.join(current_path,
                                               'DIAQC_spectral_library_fasta\\20191030CRDD_Vlib_highpH_SCX_108runs.xls')
        self.diann_d_lib_path = os.path.join(current_path, 'DIAQC_spectral_library_fasta\\library.tsv')

        self.inst_id = conf.get('run_config', 'inst_id')

        self.github_url = conf.get('github_config', 'github_url')

        self.notify_email = conf.get('notify', 'notify_email')
        self.wx_token = conf.get('notify', 'wx_token')

        self.output_dir_base = conf.get('output_dir', 'BASE')
        self.output_dir_s1 = conf.get('output_dir', 'S1')
        self.output_dir_s2 = conf.get('output_dir', 'S2')
        self.output_dir_s3 = conf.get('output_dir', 'S3')
        self.output_dir_s4 = conf.get('output_dir', 'S4')
        self.output_dir_s5 = conf.get('output_dir', 'S5')
        self.output_dir_s6 = conf.get('output_dir', 'S6')
        self.output_dir_s7 = conf.get('output_dir', 'S7')

        self.output_file_md5 = conf.get('output_file', 'ins_id_md5')
        self.output_file_run_id_name = conf.get('output_file', 'Run_Id_Name')
        self.output_file_S4_result = conf.get('output_file', 'S4_result')

        self.output_file_S5_ms1_chazi = conf.get('output_file', 'S5_ms1_chazi')

        self.output_file_S6_ms1_chazi = conf.get('output_file', 'S6_ms1_chazi')
        self.output_file_S6_ms2_chazi = conf.get('output_file', 'S6_ms2_chazi')
        self.output_file_S6_ms1_org_area = conf.get('output_file', 'S6_ms1_org_area')
        self.output_file_S6_ms2_org_area = conf.get('output_file', 'S6_ms2_org_area')

        self.output_file_S6_ms1_under_chazi = conf.get('output_file', 'S6_ms1_under_chazi')
        self.output_file_S6_ms2_under_chazi = conf.get('output_file', 'S6_ms2_under_chazi')

        self.ms_exe_path = conf.get('exe_path', 'ms_exe')
        self.diann_exe_path = conf.get('exe_path', 'diann_exe')

    # 根据文件类型获取lib
    @staticmethod
    def load_config():
        logger.info('load config')
        conf = configparser.ConfigParser()
        # 检查当前目录下是否有config.ini文件
        run_path = os.getcwd()
        custom_config_path = os.path.join(run_path, 'config.ini')
        logger.info('load config, custom config path is exist. custom_config_path is: {}'.format(custom_config_path))
        conf.read(custom_config_path, encoding='utf-8')
        return conf

    def save_config(self):
        logger.info('save config-------------')
        conf = configparser.ConfigParser()

        conf.add_section('output_dir')
        conf.set('output_dir', 'BASE', self.output_dir_base)
        conf.set('output_dir', 'S1', self.output_dir_s1)
        conf.set('output_dir', 'S2', self.output_dir_s2)
        conf.set('output_dir', 'S3', self.output_dir_s3)
        conf.set('output_dir', 'S4', self.output_dir_s4)
        conf.set('output_dir', 'S5', self.output_dir_s5)
        conf.set('output_dir', 'S6', self.output_dir_s6)
        conf.set('output_dir', 'S7', self.output_dir_s7)
        conf.add_section('output_file')
        conf.set('output_file', 'ins_id_md5', self.output_file_md5)
        conf.set('output_file', 'Run_Id_Name', self.output_file_run_id_name)
        conf.set('output_file', 'S4_result', self.output_file_S4_result)
        conf.set('output_file', 'S5_ms1_chazi', self.output_file_S5_ms1_chazi)
        conf.set('output_file', 'S6_ms1_chazi', self.output_file_S6_ms1_chazi)
        conf.set('output_file', 'S6_ms2_chazi', self.output_file_S6_ms2_chazi)
        conf.set('output_file', 'S6_ms1_org_area', self.output_file_S6_ms1_org_area)
        conf.set('output_file', 'S6_ms2_org_area', self.output_file_S6_ms2_org_area)
        conf.set('output_file', 'S6_ms1_under_chazi', self.output_file_S6_ms1_under_chazi)
        conf.set('output_file', 'S6_ms2_under_chazi', self.output_file_S6_ms2_under_chazi)

        conf.add_section('exe_path')
        conf.set('exe_path', 'ms_exe', self.ms_exe_path)
        conf.set('exe_path', 'diann_exe', self.diann_exe_path)

        conf.add_section('notify')
        conf.set('notify', 'notify_email', self.notify_email)
        conf.set('notify', 'wx_token', self.wx_token)

        conf.add_section('run_config')
        conf.set('run_config', 'inst_id', self.inst_id)

        conf.add_section('github_config')
        conf.set('github_config', 'github_url', self.github_url)

        with open("config.ini", "w") as file:
            conf.write(file)
        logger.info('save config over-------------')
        return conf

    # 根据文件类型获取lib
    def get_lib_path_by_file_type(self, file_type: FileTypeEnum):
        if file_type == FileTypeEnum.D:
            return self.diann_d_lib_path
        elif file_type == FileTypeEnum.RAW:
            return self.diann_raw_lib_path
        elif file_type == FileTypeEnum.WIFF:
            return self.diann_wiff_lib_path
        return None


setting = Setting()

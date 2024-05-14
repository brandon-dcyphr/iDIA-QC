from enum import IntEnum, Flag
import os


class FileTypeEnum(IntEnum):
    D = 1
    RAW = 2
    WIFF = 3


class FileInfo(object):

    def __init__(self):
        self.file_path = None
        self.file_type = FileTypeEnum
        self.file_name = None
        self.base_file_name = None
        self.mzXML_file_name = None
        self.mzXML_file_path = None
        self.mzML_file_name = None
        self.mzML_file_path = None
        self.ms_model = None
        self.inst_name = None
        self.run_prefix = None
        self.run_name = None
        self.diann_temp_file_path = None
        self.diann_temp_stats_file_path = None
        self.diann_result_stats_file_path = None
        self.diann_result_file_name = None
        self.diann_result_file_path = None

        self.mzxml_file_relative_path = None
        self.main_file_relative_path = None
        self.stats_file_relative_path = None
        self.jump_deal = False

        self.last_modify_time = None
        self.file_size = None

    def get_mzxml_file_size(self):
        return os.path.getsize(self.mzXML_file_path)


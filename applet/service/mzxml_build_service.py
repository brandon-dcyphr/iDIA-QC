import time

from applet import common_utils
from applet.db import db_utils
from applet.obj.Entity import FileInfo, FileTypeEnum
from applet.service import common_service

common_config = common_utils.read_yml()
ins_list = common_config['inst']


class MzxmlService(common_service.CommonService):

    def __init__(self, inst_name, run_prefix, base_output_path, file_list: [FileInfo], logger, step=4,
                 pub_channel='analysis_info', start_time=0):
        common_service.CommonService.__init__(self, base_output_path, file_list, logger, step, pub_channel, start_time)
        self.inst_name = inst_name
        self.run_prefix = run_prefix

    def deal_process(self):
        logger = self.logger
        try:
            self.is_running = True
            self.send_msg(0, msg='')
            logger.info('Start deal build mzxml info process')
            # inst_info_dict = db_utils.query_inst_info()
            # start_run_id = db_utils.query_max_run_info_id()
            for file_info in self.file_list:
                if not self.run_flag:
                    self.send_msg(2, 'Click stop')
                    return None
                run_name = get_run_name(file_info.mzXML_file_name)
                # standard_ins_id = get_standard_ins_id(file_info.file_type, self.inst_id)
                # file_info.ins_id = ins_list[self.inst_name]
                file_info.inst_name = self.inst_name
                file_info.run_prefix = self.run_prefix
                file_info.run_id = build_run_id(self.run_prefix)
                # start_run_id = start_run_id + 1
                # run_id = get_standard_run_id(standard_ins_id, start_run_id)
                # file_info.run_id = run_id
                file_info.run_name = run_name
            logger.info('Success build mzxml info')
            self.send_msg(1, msg='')
            return True
        except Exception as e:
            logger.exception('Deal build mzxml info exception')
            self.send_msg(3, msg='Deal build mzxml info exception: {}'.format(e))
            return False
        finally:
            self.is_running = False


def get_standard_ins_id(file_type, ins_id):
    if file_type == FileTypeEnum.RAW:
        return 'R%02d' % ins_id
    elif file_type == FileTypeEnum.D:
        return 'D%02d' % ins_id
    elif file_type == FileTypeEnum.WIFF:
        return 'W%02d' % ins_id
    return ''


def get_run_name(mzxml_file):
    return mzxml_file.replace('.mzXML', '')


def build_run_id(run_prefix):
    max_increase_id = db_utils.query_max_run_increase_id(run_prefix)
    if max_increase_id is None:
        max_increase_id = 0
        db_utils.insert_run_increase_id(run_prefix, 0)

    thiz_increase_id = max_increase_id + 1
    run_id = '%sU%04d' % (run_prefix, thiz_increase_id)
    db_utils.update_run_increase_id(run_prefix, thiz_increase_id)
    return run_id

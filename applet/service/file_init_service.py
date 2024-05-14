import json
import time

from pubsub import pub

from applet.obj.Entity import FileInfo
from applet.obj.Msg import AnalysisInfoMsg
from applet.service import common_service
from applet.utils import convert_utils
from applet.utils import file_utils


class FileInitService(common_service.CommonService):

    def __init__(self, base_output_path, file_list: [FileInfo], logger, step=2, pub_channel='analysis_info', start_time=0):
        common_service.CommonService.__init__(self, base_output_path, file_list, logger, step, pub_channel, start_time)

    def deal_process(self):
        logger = self.logger
        try:
            self.send_msg(0, '')
            logger.info('Start deal Init file info')
            for file_info in self.file_list:
                file_info.file_name = convert_utils.convert_to_file_name(file_info.file_path)
                convert_utils.convert_to_mzXML_name(file_info)
                thiz_file_size = file_utils.get_file_size(file_info.file_path)
                thiz_file_mtime = file_utils.get_file_mtime(file_info.file_path)
                file_info.file_size = thiz_file_size
                file_info.last_modify_time = thiz_file_mtime
            self.send_msg(1, '')
            return True
        except Exception as e:
            logger.exception('End deal init file info, deal exception')
            info_msg = AnalysisInfoMsg(1, 3, msg='deal init file info exception: {}'.format(e))
            pub.sendMessage('analysis_info', msg=json.dumps(info_msg.__dict__))
            return False

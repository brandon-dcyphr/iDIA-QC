from applet.service.notify_service import NotifyService
from applet.logger_utils import logger

from applet.obj.Entity import FileInfo

notify_email = '380187273@qq.com'
file_list = []

f1 = FileInfo()
f1.run_id = 'qqqU0022'
file_list.append(f1)


f2 = FileInfo()
f2.run_id = 'qqqU0023'
file_list.append(f2)
wx_token = '94cc39c2ec6a41c9a93c58a8524ea83c;'
notify_service = NotifyService(notify_email, wx_token, '', file_list, logger)

notify_service.deal_process()

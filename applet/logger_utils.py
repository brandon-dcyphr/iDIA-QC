import datetime
import json
import logging  # 引入logging模块
import logging.config as log_config
import os.path

cwd = os.getcwd()
log_dir = os.path.join(cwd, 'logs')
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
log_config_path = os.path.join(cwd, 'config/log.config')
if os.path.exists(log_config_path):
    with open(log_config_path, 'rt') as f:
        config = json.load(f)
    log_config.dictConfig(config)
else:
    logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('iDIA-QC')


def get_current_logger():
    current_logger = logging.getLogger()
    current_logger.setLevel(logging.INFO)
    cwd = os.getcwd()
    log_dir = os.path.join(cwd, 'logs')
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    current_time = datetime.datetime.now()
    format_str = "%Y%m%d%H%M%S"
    formatted_time = current_time.strftime(format_str)
    log_file_path = os.path.join(log_dir, 'iDIA-QC_{}.log'.format(formatted_time))
    fh = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    fh.setLevel(logging.INFO)
    log_format = logging.Formatter('iDIA-QC: %(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    fh.setFormatter(log_format)
    current_logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(log_format)
    current_logger.addHandler(ch)
    return log_file_path, current_logger

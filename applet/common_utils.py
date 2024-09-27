import os

import yaml

VERSION = 'iDIA-QC 1.7.0'

# 读取yml配置文件
def read_yml():
    cwd = os.getcwd()
    yaml_file = os.path.join(cwd, 'config/applet.yml')
    content = None
    with open(yaml_file, 'r', encoding='utf-8') as stream:
        try:
            content = yaml.safe_load(stream)
        except yaml.YAMLError as err:
            raise yaml.YAMLError("The yaml file {} could not be parsed. {}".format(yaml_file, err))
    return content


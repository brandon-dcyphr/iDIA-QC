import os.path
import pickle

import wx

from applet import common_utils

common_config = common_utils.read_yml()

setting_pkl_path = os.path.join(common_config['setting']['pkl'])
if os.path.exists(setting_pkl_path):
    with open(setting_pkl_path, 'rb') as f:
        setting_info = pickle.load(f)
else:
    setting_info = None

common_font = wx.Font()

introduce_font = wx.Font()

version_font = wx.Font()

wx_notify_token = ''

#
if setting_info:
    default_font = setting_info[0]
    wx_notify_token = setting_info[1]

    common_font.SetFamily(default_font['Family'])
    common_font.SetWeight(default_font['Weight'])
    common_font.SetFaceName(default_font['FaceName'])
    common_font.SetPointSize(default_font['PointSize'])

    introduce_font.SetFamily(default_font['Family'])
    introduce_font.SetWeight(default_font['Weight'])
    introduce_font.SetFaceName(default_font['FaceName'])
    introduce_font.SetPointSize(default_font['PointSize'])

    version_font.SetFamily(default_font['Family'])
    version_font.SetWeight(default_font['Weight'])
    version_font.SetFaceName(default_font['FaceName'])
    version_font.SetPointSize(common_config['about']['version']['fontSize'])
    # version_font.SetPointSize(common_config['about']['version']['fontSize'])

else:
    common_font.SetFamily(common_config['font']['family'])
    common_font.SetWeight(common_config['font']['weight'])
    common_font.SetFaceName(common_config['font']['faceName'])
    common_font.SetPointSize(common_config['font']['size'])

    introduce_font.SetFamily(common_config['font']['family'])
    introduce_font.SetWeight(common_config['about']['introduce']['weight'])
    introduce_font.SetFaceName(common_config['font']['faceName'])
    introduce_font.SetPointSize(common_config['about']['introduce']['fontSize'])

    version_font.SetFamily(common_config['font']['family'])
    version_font.SetWeight(common_config['about']['version']['weight'])
    version_font.SetFaceName(common_config['font']['faceName'])
    version_font.SetPointSize(common_config['about']['version']['fontSize'])

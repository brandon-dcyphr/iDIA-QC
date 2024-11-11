import os

import wx

from applet.default_config import setting
from applet.gui.common_config import common_font
from applet import common_utils

btn_width = 120


common_config = common_utils.read_yml()


class MonitorPanel(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(400, 100), style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        run_info_gb_sizer = wx.GridBagSizer(0, 0)
        run_info_gb_sizer.SetFlexibleDirection(wx.BOTH)
        run_info_gb_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        # self.run_data_panel = RunDataPanel(self)
        self.monitor_control_panel = MonitorControlPanel(self)
        self.monitor_log_panel = MonitorLogPanel(self)

        # run_info_gb_sizer.Add(self.run_data_panel, wx.GBPosition(0, 0), wx.GBSpan(6, 10), wx.ALL | wx.EXPAND, 5)
        run_info_gb_sizer.Add(self.monitor_control_panel, wx.GBPosition(0, 0), wx.GBSpan(5, 8), wx.ALL | wx.EXPAND, 5)
        run_info_gb_sizer.Add(self.monitor_log_panel, wx.GBPosition(5, 0), wx.GBSpan(3, 8), wx.ALL | wx.EXPAND, 5)

        run_info_gb_sizer.AddGrowableRow(5)
        run_info_gb_sizer.AddGrowableCol(7)

        self.SetSizer(run_info_gb_sizer)
        self.Layout()

    def __del__(self):
        pass


class MonitorControlPanel(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(-1, 350), style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        run_info_gb_sizer = wx.GridBagSizer(0, 0)
        run_info_gb_sizer.SetFlexibleDirection(wx.BOTH)
        run_info_gb_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.monitor_dir_choose_button = wx.Button(self, wx.ID_ANY, u"Monitor dir",
                                                   wx.DefaultPosition, wx.Size(120, -1), 0)
        self.monitor_dir_choose_button.SetFont(common_font)

        run_info_gb_sizer.Add(self.monitor_dir_choose_button, wx.GBPosition(0, 0), wx.GBSpan(1, 2),
                              wx.ALIGN_RIGHT | wx.ALL, 5)

        self.monitor_dir_text = wx.TextCtrl(self, wx.ID_ANY, '',
                                            wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.monitor_dir_text.SetFont(common_font)
        run_info_gb_sizer.Add(self.monitor_dir_text, wx.GBPosition(0, 2), wx.GBSpan(1, 16),
                              wx.ALL | wx.EXPAND, 5)

        self.diann_exe_btn = wx.Button(self, wx.ID_ANY, u"DIA-NN.exe", wx.DefaultPosition,
                                       wx.Size(btn_width, -1), 0)
        self.diann_exe_btn.SetFont(common_font)

        run_info_gb_sizer.Add(self.diann_exe_btn, wx.GBPosition(1, 0), wx.GBSpan(1, 2), wx.ALL, 5)

        self.diann_path_text = wx.TextCtrl(self, wx.ID_ANY, setting.diann_exe_path,
                                           wx.DefaultPosition, wx.Size(250, -1), 0)
        self.diann_path_text.SetFont(common_font)

        run_info_gb_sizer.Add(self.diann_path_text, wx.GBPosition(1, 2), wx.GBSpan(1, 16), wx.ALL | wx.EXPAND, 5)

        self.msconvert_btn = wx.Button(self, wx.ID_ANY, u"MSConvert", wx.DefaultPosition,
                                       wx.Size(btn_width, -1), 0)
        self.msconvert_btn.SetFont(common_font)

        run_info_gb_sizer.Add(self.msconvert_btn, wx.GBPosition(2, 0), wx.GBSpan(1, 2), wx.ALL, 5)

        self.msconvert_path_text = wx.TextCtrl(self, wx.ID_ANY, setting.ms_exe_path,
                                               wx.DefaultPosition, wx.Size(250, -1), 0)
        self.msconvert_path_text.SetFont(common_font)

        run_info_gb_sizer.Add(self.msconvert_path_text, wx.GBPosition(2, 2), wx.GBSpan(1, 16), wx.ALL | wx.EXPAND, 5)

        self.output_path_choose_button = wx.Button(self, wx.ID_ANY, u"Output dir",
                                                   wx.DefaultPosition, wx.Size(btn_width, -1), 0)
        self.output_path_choose_button.SetFont(common_font)

        run_info_gb_sizer.Add(self.output_path_choose_button, wx.GBPosition(3, 0), wx.GBSpan(1, 2),
                              wx.ALIGN_RIGHT | wx.ALL, 5)

        self.file_output_dir_text = wx.TextCtrl(self, wx.ID_ANY, '',
                                                wx.DefaultPosition, wx.Size(250, -1), 0)
        self.file_output_dir_text.SetFont(common_font)

        run_info_gb_sizer.Add(self.file_output_dir_text, wx.GBPosition(3, 2), wx.GBSpan(1, 16), wx.ALL | wx.EXPAND, 5)

        '''******* scan time *******'''

        inst_btn_btn = wx.Button(self, wx.ID_ANY, u"Instrument type", wx.DefaultPosition,
                                      wx.Size(btn_width, -1), 0)
        inst_btn_btn.SetFont(common_font)
        run_info_gb_sizer.Add(inst_btn_btn, wx.GBPosition(4, 0), wx.GBSpan(1, 2), wx.ALL, 5)

        self.ins_id_choice_list = common_config['inst']
        self.ins_id_choice = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.ins_id_choice_list, 0)
        self.ins_id_choice.SetFont(common_font)
        run_info_gb_sizer.Add(self.ins_id_choice, wx.GBPosition(4, 2), wx.GBSpan(1, 2), wx.ALL | wx.EXPAND, 5)

        run_prefix_btn_btn = wx.Button(self, wx.ID_ANY, u"Instrument ID", wx.DefaultPosition,
                                       wx.Size(btn_width, -1), 0)
        run_prefix_btn_btn.SetFont(common_font)
        run_info_gb_sizer.Add(run_prefix_btn_btn, wx.GBPosition(4, 4), wx.GBSpan(1, 2), wx.ALL, 5)

        self.run_prefix_text = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString,
                                           wx.DefaultPosition, wx.Size(100, -1), 0)
        self.run_prefix_text.SetFont(common_font)
        run_info_gb_sizer.Add(self.run_prefix_text, wx.GBPosition(4, 6), wx.GBSpan(1, 2), wx.ALL | wx.EXPAND, 5)

        scan_time_button = wx.Button(self, wx.ID_ANY, u"Scan time(sec)",
                                     wx.DefaultPosition, wx.Size(btn_width, -1), 0)
        scan_time_button.SetFont(common_font)
        # scan_time_button.Disable()
        run_info_gb_sizer.Add(scan_time_button, wx.GBPosition(4, 8), wx.GBSpan(1, 2),
                              wx.ALIGN_RIGHT | wx.ALL, 5)
        self.scan_time_ctrl = wx.SpinCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                          wx.SP_ARROW_KEYS, 0, 1000, 30)
        self.scan_time_ctrl.SetFont(common_font)
        run_info_gb_sizer.Add(self.scan_time_ctrl, wx.GBPosition(4, 10), wx.GBSpan(1, 2), wx.ALL | wx.EXPAND, 5)

        interval_time_button = wx.Button(self, wx.ID_ANY, u"Interval time(min)",
                                         wx.DefaultPosition, wx.Size(140, -1), 0)
        interval_time_button.SetFont(common_font)
        # interval_time_button.Disable()
        run_info_gb_sizer.Add(interval_time_button, wx.GBPosition(4, 12), wx.GBSpan(1, 2),
                              wx.ALIGN_RIGHT | wx.ALL, 5)
        self.interval_time_ctrl = wx.SpinCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                              wx.SP_ARROW_KEYS, 0, 1000, 10)
        self.interval_time_ctrl.SetFont(common_font)
        run_info_gb_sizer.Add(self.interval_time_ctrl, wx.GBPosition(4, 14), wx.GBSpan(1, 2), wx.ALL | wx.EXPAND, 5)
        '''*************************************'''

        notify_email_button = wx.Button(self, wx.ID_ANY, u"Email address",
                                        wx.DefaultPosition, wx.Size(btn_width, -1), 0)
        notify_email_button.SetFont(common_font)
        # notify_email_button.Disable()
        run_info_gb_sizer.Add(notify_email_button, wx.GBPosition(5, 0), wx.GBSpan(1, 2),
                              wx.ALIGN_RIGHT | wx.ALL, 5)
        self.notify_email_text = wx.TextCtrl(self, wx.ID_ANY, setting.notify_email,
                                             wx.DefaultPosition, wx.Size(250, -1), 0)
        self.notify_email_text.SetFont(common_font)
        run_info_gb_sizer.Add(self.notify_email_text, wx.GBPosition(5, 2), wx.GBSpan(1, 16), wx.ALL | wx.EXPAND, 5)

        '''wx token'''
        wx_token_btn = wx.Button(self, wx.ID_ANY, u"Wechat token", wx.DefaultPosition,
                                 wx.Size(btn_width, -1), 0)
        wx_token_btn.SetFont(common_font)

        run_info_gb_sizer.Add(wx_token_btn, wx.GBPosition(6, 0), wx.GBSpan(1, 2), wx.ALL, 5)

        self.wx_token_text = wx.TextCtrl(self, wx.ID_ANY,
                                         setting.wx_token,
                                         wx.DefaultPosition,
                                         wx.Size(250, -1), 0)
        self.wx_token_text.SetFont(common_font)

        run_info_gb_sizer.Add(self.wx_token_text, wx.GBPosition(6, 2), wx.GBSpan(1, 16), wx.ALL | wx.EXPAND, 5)
        '''***************************'''

        self.file_filter_panel = FileFilterInfoPanel(self)
        run_info_gb_sizer.Add(self.file_filter_panel, wx.GBPosition(7, 0), wx.GBSpan(2, 18), wx.ALL| wx.EXPAND, 5)

        self.monitor_start_button = wx.Button(self, wx.ID_ANY, u"Start", wx.DefaultPosition, wx.Size(120, -1), 0)
        self.monitor_start_button.SetFont(common_font)
        run_info_gb_sizer.Add(self.monitor_start_button, wx.GBPosition(9, 0), wx.GBSpan(1, 2), wx.ALL, 5)

        self.monitor_status_button = wx.Button(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(25, -1),
                                               wx.BU_NOTEXT)
        run_info_gb_sizer.Add(self.monitor_status_button, wx.GBPosition(9, 2), wx.GBSpan(1, 1), wx.ALL, 5)

        self.monitor_stop_button = wx.Button(self, wx.ID_ANY, u"Stop", wx.DefaultPosition, wx.Size(120, -1),
                                             0)
        self.monitor_stop_button.SetFont(common_font)
        run_info_gb_sizer.Add(self.monitor_stop_button, wx.GBPosition(9, 3), wx.GBSpan(1, 2), wx.ALL, 5)

        run_info_gb_sizer.AddGrowableCol(17)

        self.SetSizer(run_info_gb_sizer)
        self.Layout()

    def __del__(self):
        pass


class MonitorLogPanel(wx.Panel):
    def __init__(self, parent, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, pos=pos, style=style, name=name)
        dlog_sb = wx.StaticBox(self, wx.ID_ANY, u"Monitoring log")
        dlog_sb.SetFont(common_font)

        log_info_box_sizer = wx.StaticBoxSizer(dlog_sb, wx.VERTICAL)

        log_info_sizer = wx.GridBagSizer(0, 0)
        log_info_sizer.SetFlexibleDirection(wx.BOTH)
        log_info_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.log_text = wx.TextCtrl(log_info_box_sizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString,
                                    wx.DefaultPosition, wx.DefaultSize,
                                    style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2)
        self.log_text.SetFont(common_font)

        log_info_sizer.Add(self.log_text, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.ALL | wx.EXPAND, 5)

        log_info_box_sizer.Add(log_info_sizer, 1, wx.EXPAND, 5)

        log_info_sizer.AddGrowableCol(0)
        log_info_sizer.AddGrowableRow(0)

        self.SetSizer(log_info_box_sizer)
        self.Layout()

    def __del__(self):
        pass

'''

'''
class FileFilterInfoPanel(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(-1, 60), style=wx.TAB_TRAVERSAL|wx.ALL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        rd_sb = wx.StaticBox(self, wx.ID_ANY, u"File filtering")
        rd_sb.SetFont(common_font)

        info_panel_sb_sizer = wx.StaticBoxSizer(rd_sb, wx.VERTICAL)

        info_panel_gb_sizer = wx.GridBagSizer(0, 0)
        info_panel_gb_sizer.SetFlexibleDirection(wx.BOTH)
        info_panel_gb_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        ''' file size'''
        min_size_button = wx.Button(self, wx.ID_ANY, u"Min size(MB)",
                                     wx.DefaultPosition, wx.Size(btn_width, -1), 0)
        min_size_button.SetFont(common_font)

        info_panel_gb_sizer.Add(min_size_button, wx.GBPosition(0, 0), wx.GBSpan(1, 2), wx.ALIGN_RIGHT | wx.ALL, 5)

        self.min_size_ctrl = wx.SpinCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                          wx.SP_ARROW_KEYS, 0, 2000, 0)
        self.min_size_ctrl.SetFont(common_font)
        info_panel_gb_sizer.Add(self.min_size_ctrl, wx.GBPosition(0, 2), wx.GBSpan(1, 2), wx.ALL | wx.EXPAND, 5)

        ''' filtering file name  '''
        self.reserve_btn = wx.RadioButton(info_panel_sb_sizer.GetStaticBox(), wx.ID_ANY, u"Inclusion", wx.DefaultPosition,
                                            wx.DefaultSize, wx.RB_GROUP)
        info_panel_gb_sizer.Add(self.reserve_btn, wx.GBPosition(0, 5), wx.GBSpan(1, 2), wx.ALL, 5)

        self.remove_btn = wx.RadioButton(info_panel_sb_sizer.GetStaticBox(), wx.ID_ANY, u"Exclusion",
                                             wx.DefaultPosition, wx.DefaultSize, 0)
        info_panel_gb_sizer.Add(self.remove_btn, wx.GBPosition(0, 7), wx.GBSpan(1, 2), wx.ALL, 5)

        filter_name_button = wx.Button(self, wx.ID_ANY, u"Key words",
                                         wx.DefaultPosition, wx.Size(btn_width, -1), 0)
        filter_name_button.SetFont(common_font)
        # filter_name_button.Disable()

        info_panel_gb_sizer.Add(filter_name_button, wx.GBPosition(0, 9), wx.GBSpan(1, 2), wx.ALIGN_RIGHT | wx.ALL, 5)

        self.filter_name_text = wx.TextCtrl(self, wx.ID_ANY, '',
                                              wx.DefaultPosition, wx.Size(250, -1), 0)
        self.filter_name_text.SetFont(common_font)
        info_panel_gb_sizer.Add(self.filter_name_text, wx.GBPosition(0, 11), wx.GBSpan(1, 2), wx.ALL | wx.EXPAND, 5)

        info_panel_gb_sizer.AddGrowableCol(11)
        info_panel_sb_sizer.Add(info_panel_gb_sizer, 1, wx.EXPAND, 5)

        self.SetSizer(info_panel_sb_sizer)
        self.Layout()

    def __del__(self):
        pass

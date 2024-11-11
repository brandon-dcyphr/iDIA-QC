import os.path

import wx

from applet import common_utils
from applet.gui.monitor_info_panel import MonitorPanel
from applet.logger_utils import logger
from applet.thread_util.analysis_monitor_thread import AnalysisMonitorThread

common_config = common_utils.read_yml()
ins_list = common_config['inst']

RUNNING_COLOR = '#f8c108'
OVER_COLOR = '#27c14c'
ERROR_COLOR = '#e91b40'


class MonitorEventHandler(object):

    def __init__(self, monitor_panel: MonitorPanel):
        self.monitor_panel = monitor_panel
        self.an_monitor_thread = None

    def monitor_dir_choose_click(self, event):
        dir_choose_bt = wx.DirDialog(self.monitor_panel, 'Choose monitor dir path', style=wx.DD_DIR_MUST_EXIST)
        if dir_choose_bt.ShowModal() == wx.ID_OK:
            old_value = self.monitor_panel.monitor_control_panel.monitor_dir_text.GetValue()
            self.monitor_panel.monitor_control_panel.monitor_dir_text.ChangeValue(
                old_value + dir_choose_bt.GetPath() + ';')
        dir_choose_bt.Destroy()

    def output_dir_choose(self, event):
        dir_choose_bt = wx.DirDialog(self.monitor_panel, 'Choose output dir path', style=wx.DD_DIR_MUST_EXIST)
        if dir_choose_bt.ShowModal() == wx.ID_OK:
            self.monitor_panel.monitor_control_panel.file_output_dir_text.ChangeValue(dir_choose_bt.GetPath())
        dir_choose_bt.Destroy()

    def diann_choose(self, event):
        filesFilter = "DiaNN.exe"
        file_choose_bt = wx.FileDialog(self.monitor_panel, message='Choose DiaNN.exe', wildcard=filesFilter,
                                       style=wx.FD_DEFAULT_STYLE)
        if file_choose_bt.ShowModal() == wx.ID_OK:
            self.monitor_panel.monitor_control_panel.diann_path_text.ChangeValue(file_choose_bt.GetPath())
        file_choose_bt.Destroy()

    def msconvert_choose(self, event):
        filesFilter = "msconvert.exe"
        file_choose_bt = wx.FileDialog(self.monitor_panel, message='Choose msconvert.exe', wildcard=filesFilter,
                                       style=wx.FD_DEFAULT_STYLE)
        if file_choose_bt.ShowModal() == wx.ID_OK:
            self.monitor_panel.monitor_control_panel.msconvert_path_text.ChangeValue(file_choose_bt.GetPath())
        file_choose_bt.Destroy()

    def fasta_choose(self, event):
        file_choose_bt = wx.FileDialog(self.monitor_panel, message='choose FASTA file', style=wx.FD_DEFAULT_STYLE)
        if file_choose_bt.ShowModal() == wx.ID_OK:
            self.monitor_panel.monitor_control_panel.fasta_path_text.ChangeValue(file_choose_bt.GetPath())
        file_choose_bt.Destroy()

    def format_monitor_dir(self, monitor_dir):
        monitor_dir_list = str(monitor_dir).split(';')
        new_dir_list = []
        for current_dir in monitor_dir_list:
            current_dir = current_dir.rstrip()
            if len(current_dir) == 0:
                continue
            new_dir_list.append(current_dir)
        return list(set(new_dir_list))

    def monitor_start_click(self, event):
        #
        monitor_dir = self.monitor_panel.monitor_control_panel.monitor_dir_text.GetValue()
        logger.info('monitor_dir_text: {}'.format(monitor_dir))
        if not monitor_dir or len(monitor_dir) == 0:
            msg_box = wx.MessageDialog(None, 'Please choose monitor dir', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return
        #
        monitor_dir_list = self.format_monitor_dir(monitor_dir)
        if len(monitor_dir_list) == 0:
            msg_box = wx.MessageDialog(None, 'Please choose monitor dir', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return
        for current_dir in monitor_dir_list:
            if not os.path.exists(current_dir):
                msg_box = wx.MessageDialog(None, 'Monitor dir is not exist', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
                if msg_box.ShowModal() == wx.ID_YES:
                    msg_box.Destroy()
                return
        #
        ins_select_id = self.monitor_panel.monitor_control_panel.ins_id_choice.GetSelection()
        if ins_select_id == -1:
            msg_box = wx.MessageDialog(None, 'Instrument type is not selected', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return
        inst_name = ins_list[ins_select_id]

        run_prefix = self.monitor_panel.monitor_control_panel.run_prefix_text.GetValue()
        if not run_prefix or len(run_prefix) == 0:
            msg_box = wx.MessageDialog(None, 'Please input instrument id', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

        self.monitor_panel.monitor_control_panel.monitor_start_button.SetLabel('Running')
        self.monitor_panel.monitor_control_panel.monitor_status_button.SetBackgroundColour(RUNNING_COLOR)
        self.monitor_panel.monitor_control_panel.monitor_start_button.Disable()
        #
        msconvert_path = self.monitor_panel.monitor_control_panel.msconvert_path_text.GetValue()
        diann_path = self.monitor_panel.monitor_control_panel.diann_path_text.GetValue()
        output_path = self.monitor_panel.monitor_control_panel.file_output_dir_text.GetValue()

        scan_time = self.monitor_panel.monitor_control_panel.scan_time_ctrl.GetValue()
        interval_time = self.monitor_panel.monitor_control_panel.interval_time_ctrl.GetValue()

        notify_email = self.monitor_panel.monitor_control_panel.notify_email_text.GetValue()
        wx_token = self.monitor_panel.monitor_control_panel.wx_token_text.GetValue()

        file_filter_size = self.monitor_panel.monitor_control_panel.file_filter_panel.min_size_ctrl.GetValue()
        filter_type = self.get_filter_type_checked()
        file_name = self.monitor_panel.monitor_control_panel.file_filter_panel.filter_name_text.GetValue()

        #
        logger.info('Start analysis monitor thread')
        self.an_monitor_thread = AnalysisMonitorThread(monitor_dir_list, inst_name, run_prefix, scan_time,
                                                       interval_time,
                                                       msconvert_path, diann_path, output_path,
                                                       './resource/model/unisplit', notify_email, wx_token,
                                                       file_filter_size, filter_type, file_name)
        self.an_monitor_thread.daemon = True
        #
        self.monitor_panel.monitor_log_panel.log_text.SetValue('')
        self.an_monitor_thread.start()

    def monitor_stop_click(self, event):
        #
        if self.an_monitor_thread:
            self.an_monitor_thread.close_thread()
        self.monitor_panel.monitor_control_panel.monitor_start_button.SetLabel('Run')
        self.monitor_panel.monitor_control_panel.monitor_start_button.Enable()
        self.monitor_panel.monitor_control_panel.monitor_status_button.SetBackgroundColour(None)


    def get_filter_type_checked(self):
        if self.monitor_panel.monitor_control_panel.file_filter_panel.reserve_btn.GetValue():
            return 1
        elif self.monitor_panel.monitor_control_panel.file_filter_panel.remove_btn.GetValue():
            return 2
        else:
            return None

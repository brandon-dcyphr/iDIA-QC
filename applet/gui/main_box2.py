import json
import os
import pickle

import wx
import wx.grid
from pubsub import pub

from applet import common_utils
from applet.default_config import setting
# from applet.event_handler import data_info_event_handler
from applet.event_handler.data_info_event_handler import DataInfoEventHandler
from applet.event_handler.monitor_event import MonitorEventHandler
from applet.gui.about_panel import AboutInfoPanel
from applet.gui.common_config import common_font
from applet.gui.data_info_panel import DataInfoPanel
from applet.gui.help_panel import HelpPanel
from applet.gui.monitor_info_panel import MonitorPanel
from applet.gui.run_info_panel import RunInfoPanel
from applet.gui.set_panel import SetPanel
from applet.logger_utils import logger
from applet.obj.Entity import FileInfo, FileTypeEnum
from applet.thread_util.analysis_thread import AnalysisThread

common_config = common_utils.read_yml()
ins_list = common_config['inst']

RUNNING_COLOR = '#f8c108'
OVER_COLOR = '#27c14c'
ERROR_COLOR = '#e91b40'


class MyListBook(wx.Listbook):

    def __init__(self, parent):
        wx.Listbook.__init__(self, parent, wx.ID_ANY)

        imagelist = wx.ImageList(64, 64)
        imagelist.Add(wx.Bitmap('./resource/icon/about.png', wx.BITMAP_TYPE_ANY))
        imagelist.Add(wx.Bitmap('./resource/icon/param.png', wx.BITMAP_TYPE_ANY))
        imagelist.Add(wx.Bitmap('./resource/icon/draw.png', wx.BITMAP_TYPE_ANY))
        imagelist.Add(wx.Bitmap('./resource/icon/ai.png', wx.BITMAP_TYPE_ANY))
        imagelist.Add(wx.Bitmap('./resource/icon/set.png', wx.BITMAP_TYPE_ANY))
        # imagelist.Add(wx.Bitmap('./resource/icon/help.png', wx.BITMAP_TYPE_ANY))
        # 将ImageList对象加入到m_listbook1里面，供后结菜单使用
        self.AssignImageList(imagelist)


class MainBox(wx.Frame):

    def __init__(self, ):
        logger.info('start init frame')
        self.msconvert_deal_count = 0
        self.msconvert_all_count = 0
        self.deal_step = 0
        self.all_step_count = 11

        self.diann_deal_count = 0
        self.diann_all_count = 0
        self.analysis_thread = None

        wx.Frame.__init__(self, None, title=common_utils.VERSION,
                          size=(1320, 680))

        self.SetIcon(wx.Icon('./resource/logo/iDIAQC-logo.png', wx.BITMAP_TYPE_PNG))

        self.Centre(wx.BOTH)

        main_panel = wx.Panel(self)

        self.notebook = MyListBook(main_panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.ALL | wx.EXPAND, 5)
        main_panel.SetSizer(sizer)

        self.about_info_panel = AboutInfoPanel(self.notebook)
        self.run_info_panel = RunInfoPanel(self.notebook)
        self.monitor_panel = MonitorPanel(self.notebook)
        self.data_info_panel = DataInfoPanel(self.notebook)
        # self.set_panel = SetPanel(self.notebook)
        # self.help_panel = HelpPanel(self.notebook)

        self.notebook.AddPage(self.about_info_panel, 'About', select=True, imageId=0)
        self.notebook.AddPage(self.run_info_panel, 'Manual mode', imageId=1)
        self.notebook.AddPage(self.data_info_panel, 'Data', imageId=2)
        self.notebook.AddPage(self.monitor_panel, 'Monitoring mode', imageId=3)
        # self.notebook.AddPage(self.set_panel, 'Settings', imageId=4)
        # self.notebook.AddPage(self.help_panel, 'Help', imageId=5)

        self.notebook.SetFont(common_font)

        self.data_panel_event_handler = DataInfoEventHandler(self.data_info_panel)

        # 选择exe事件
        self.Bind(wx.EVT_BUTTON, self.diann_path_choose, self.run_info_panel.config_panel.diann_exe_btn)
        self.Bind(wx.EVT_BUTTON, self.msconvert_path_choose, self.run_info_panel.config_panel.msconvert_btn)

        # 选择质谱文件事件
        self.Bind(wx.EVT_BUTTON, self.raw_file_choose, self.run_info_panel.input_panel.raw_select_button)
        self.Bind(wx.EVT_BUTTON, self.d_file_choose, self.run_info_panel.input_panel.d_select_button)
        self.Bind(wx.EVT_BUTTON, self.wiff_file_choose, self.run_info_panel.input_panel.wiff_select_button)

        self.Bind(wx.EVT_BUTTON, self.clear_button_click, self.run_info_panel.input_panel.clear_button)

        self.Bind(wx.EVT_BUTTON, self.run_btn_click, self.run_info_panel.run_control_panel.run_button)
        self.Bind(wx.EVT_BUTTON, self.stop_btn_click, self.run_info_panel.run_control_panel.stop_button)
        # 输出文件夹选择按钮事件
        self.Bind(wx.EVT_BUTTON, self.output_path_choose, self.run_info_panel.input_panel.output_path_choose_button)

        # 画图的事件
        self.Bind(wx.EVT_BUTTON, self.data_panel_event_handler.load_grid_data_with_param,
                  self.data_info_panel.run_data_panel.search_button)
        # 画图文件夹选择事件
        self.Bind(wx.EVT_BUTTON, self.data_panel_event_handler.draw_dir_choose,
                  self.data_info_panel.data_control_panel.output_path_choose_button)
        self.Bind(wx.EVT_BUTTON, self.data_panel_event_handler.draw_all,
                  self.data_info_panel.data_control_panel.draw_all_button)
        self.Bind(wx.EVT_BUTTON, self.data_panel_event_handler.draw_selected,
                  self.data_info_panel.data_control_panel.draw_selected_button)
        self.Bind(wx.EVT_BUTTON, self.data_panel_event_handler.draw_search,
                  self.data_info_panel.data_control_panel.draw_search_button)

        # AI事件
        self.Bind(wx.EVT_BUTTON, self.data_panel_event_handler.export_pred,
                  self.data_info_panel.data_control_panel.export_pred_button)

        self.monitor_event_handler = MonitorEventHandler(self.monitor_panel)
        # monitor事件
        self.Bind(wx.EVT_BUTTON, self.monitor_event_handler.monitor_dir_choose_click,
                  self.monitor_panel.monitor_control_panel.monitor_dir_choose_button)
        self.Bind(wx.EVT_BUTTON, self.monitor_event_handler.diann_choose,
                  self.monitor_panel.monitor_control_panel.diann_exe_btn)
        self.Bind(wx.EVT_BUTTON, self.monitor_event_handler.msconvert_choose,
                  self.monitor_panel.monitor_control_panel.msconvert_btn)

        self.Bind(wx.EVT_BUTTON, self.monitor_event_handler.output_dir_choose,
                  self.monitor_panel.monitor_control_panel.output_path_choose_button)

        self.Bind(wx.EVT_BUTTON, self.monitor_event_handler.monitor_start_click,
                  self.monitor_panel.monitor_control_panel.monitor_start_button)
        self.Bind(wx.EVT_BUTTON, self.monitor_event_handler.monitor_stop_click,
                  self.monitor_panel.monitor_control_panel.monitor_stop_button)

        # self.Bind(wx.EVT_BUTTON, self.setting_save, self.set_panel.save_btn)

        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.data_panel_event_handler.load_grid_data()

        # 下面是内存变量
        self.choose_file_list = []

        # 消息订阅
        pub.subscribe(self.sub_analysis_info, 'analysis_info')
        pub.subscribe(self.sub_reload_data, 'channel_reload_data')
        pub.subscribe(self.monitor_log, 'monitor_log')

        logger.info('end init frame')

    def on_close(self, event):
        if self.analysis_thread is not None:
            self.analysis_thread.set_run_flag(False)

        if self.monitor_event_handler.an_monitor_thread:
            self.monitor_event_handler.an_monitor_thread.run_flag = False
        event.Skip()

    # 选择output的路径
    def output_path_choose(self, event):
        dir_choose_bt = wx.DirDialog(self, 'Choose output path dir', style=wx.DD_DIR_MUST_EXIST)
        if dir_choose_bt.ShowModal() == wx.ID_OK:
            self.run_info_panel.input_panel.file_output_dir_text.ChangeValue(dir_choose_bt.GetPath())
        dir_choose_bt.Destroy()

    # 选择diann的路径
    def diann_path_choose(self, event):
        filesFilter = "DiaNN.exe"
        file_choose_bt = wx.FileDialog(self, message='Choose DiaNN.exe', wildcard=filesFilter,
                                       style=wx.FD_DEFAULT_STYLE)
        if file_choose_bt.ShowModal() == wx.ID_OK:
            self.run_info_panel.config_panel.diann_path_text.ChangeValue(file_choose_bt.GetPath())
        file_choose_bt.Destroy()

    # 选择msconvert路径
    def msconvert_path_choose(self, event):
        filesFilter = "msconvert.exe"
        file_choose_bt = wx.FileDialog(self, message='Choose msconvert.exe', wildcard=filesFilter,
                                       style=wx.FD_DEFAULT_STYLE)
        if file_choose_bt.ShowModal() == wx.ID_OK:
            self.run_info_panel.config_panel.msconvert_path_text.ChangeValue(file_choose_bt.GetPath())
        file_choose_bt.Destroy()

    def fasta_choose(self, event):
        file_choose_bt = wx.FileDialog(self, message='choose FASTA file', style=wx.FD_DEFAULT_STYLE)
        if file_choose_bt.ShowModal() == wx.ID_OK:
            self.run_info_panel.config_panel.fasta_path_text.ChangeValue(file_choose_bt.GetPath())
        file_choose_bt.Destroy()

    # 选择文件公共插件
    def common_file_choose(self, filesFilter, file_type):
        file_choose_bt = wx.FileDialog(self, message='Choose raw', wildcard=filesFilter, style=wx.FD_MULTIPLE)
        if file_choose_bt.ShowModal() == wx.ID_OK:
            choose_file_path_list = file_choose_bt.GetPaths()
            for choose_file_path in choose_file_path_list:
                file_info = FileInfo()
                file_info.file_path = choose_file_path
                file_info.file_type = file_type
                self.choose_file_list.append(file_info)
            path_text = '\n'.join([data.file_path for data in self.choose_file_list])
            self.run_info_panel.input_panel.raw_file_path_text.ChangeValue(path_text)
            self.msconvert_all_count = len(self.choose_file_list)
            self.msconvert_deal_count = 0
            self.run_info_panel.output_panel.msconvert_gauge.SetRange(self.msconvert_all_count)
            self.run_info_panel.output_panel.msconvert_gauge.SetValue(self.msconvert_deal_count)
            self.run_info_panel.output_panel.msconvert_pro_label.SetLabel('0/{}'.format(self.msconvert_all_count))

            self.diann_all_count = len(self.choose_file_list)
            self.run_info_panel.output_panel.diann_gauge.SetRange(self.diann_all_count)
            self.diann_deal_count = 0
            self.run_info_panel.output_panel.diann_gauge.SetValue(self.diann_deal_count)
            self.run_info_panel.output_panel.diann_pro_label.SetLabel('0/{}'.format(self.diann_all_count))

        file_choose_bt.Destroy()

    # 点击开始按钮后的初始化
    def run_init(self):
        self.msconvert_all_count = len(self.choose_file_list)
        self.msconvert_deal_count = 0
        self.run_info_panel.output_panel.msconvert_gauge.SetRange(self.msconvert_all_count)
        self.run_info_panel.output_panel.msconvert_gauge.SetValue(self.msconvert_deal_count)
        self.run_info_panel.output_panel.msconvert_pro_label.SetLabel('0/{}'.format(self.msconvert_all_count))

        self.diann_all_count = len(self.choose_file_list)
        self.run_info_panel.output_panel.diann_gauge.SetRange(self.diann_all_count)
        self.diann_deal_count = 0
        self.run_info_panel.output_panel.diann_gauge.SetValue(self.diann_deal_count)
        self.run_info_panel.output_panel.diann_pro_label.SetLabel('0/{}'.format(self.diann_all_count))

        self.deal_step = 0
        self.run_info_panel.output_panel.all_progress_gauge.SetValue(self.deal_step)
        self.run_info_panel.output_panel.all_progress_gauge.SetRange(self.all_step_count)
        self.run_info_panel.output_panel.all_pro_label.SetLabel('0/{}'.format(self.all_step_count))

    def raw_file_choose(self, event):
        file_filter = "*.raw"
        self.common_file_choose(file_filter, FileTypeEnum.RAW)

    def d_file_choose(self, event):
        file_filter = "*.d"
        dir_choose_bt = wx.DirDialog(self.monitor_panel, 'Choose .d file dir', style=wx.DD_DIR_MUST_EXIST)
        # dir_choose_bt = wx.FileDialog(self.monitor_panel, message="选择文件夹", style=wx.FD_OPEN | wx.FD_MULTIPLE)
        if dir_choose_bt.ShowModal() == wx.ID_OK:
            choose_file_path = dir_choose_bt.GetPath()
            file_info = FileInfo()
            file_info.file_path = choose_file_path
            file_info.file_type = FileTypeEnum.D
            self.choose_file_list.append(file_info)

            path_text = '\n'.join([data.file_path for data in self.choose_file_list])
            self.run_info_panel.input_panel.raw_file_path_text.ChangeValue(path_text)
            self.msconvert_all_count = len(self.choose_file_list)
            self.msconvert_deal_count = 0
            self.run_info_panel.output_panel.msconvert_gauge.SetRange(self.msconvert_all_count)
            self.run_info_panel.output_panel.msconvert_gauge.SetValue(self.msconvert_deal_count)
            self.run_info_panel.output_panel.msconvert_pro_label.SetLabel('0/{}'.format(self.msconvert_all_count))

            self.diann_all_count = len(self.choose_file_list)
            self.run_info_panel.output_panel.diann_gauge.SetRange(self.diann_all_count)
            self.diann_deal_count = 0
            self.run_info_panel.output_panel.diann_gauge.SetValue(self.diann_deal_count)
            self.run_info_panel.output_panel.diann_pro_label.SetLabel('0/{}'.format(self.diann_all_count))

            # old_value = self.monitor_panel.monitor_control_panel.monitor_dir_text.GetValue()
            # self.monitor_panel.monitor_control_panel.monitor_dir_text.ChangeValue(old_value + dir_choose_bt.GetPath() + ';')
        dir_choose_bt.Destroy()

        # self.common_file_choose(file_filter, FileTypeEnum.D)

    def wiff_file_choose(self, event):
        file_filter = "*.wiff"
        self.common_file_choose(file_filter, FileTypeEnum.WIFF)

    def clear_button_click(self, event):
        self.choose_file_list = []
        self.run_info_panel.input_panel.raw_file_path_text.ChangeValue('')

    def run_btn_click(self, event):
        # 获取diann路径
        logger.info('----click start analysis button-------')
        if len(self.choose_file_list) == 0:
            msg_box = wx.MessageDialog(None, 'Please choose raw file', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return
        cwd = os.getcwd()
        self.run_init()
        diann_path = self.run_info_panel.config_panel.diann_path_text.GetValue()
        # msconvert路径
        msconvert_path = self.run_info_panel.config_panel.msconvert_path_text.GetValue()

        # 质谱文件路径
        output_path = self.run_info_panel.input_panel.file_output_dir_text.GetValue()
        output_path = os.path.join(cwd, output_path)
        if output_path is None or len(output_path) == 0:
            msg_box = wx.MessageDialog(None, 'No selected output dir', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

        # 检查ins id
        ins_select_id = self.run_info_panel.config_panel.ins_id_choice.GetSelection()
        if ins_select_id == -1:
            msg_box = wx.MessageDialog(None, 'Instrument type is not selected', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

        inst_name = ins_list[ins_select_id]

        run_prefix = self.run_info_panel.config_panel.run_prefix_text.GetValue()
        if run_prefix is None or len(run_prefix) == 0:
            msg_box = wx.MessageDialog(None, 'Please input instrument id', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

        if not os.path.exists(output_path):
            os.makedirs(output_path)
        # 开始分析
        logger.info('----start analysis-------')
        setting.output_dir_base = output_path
        setting.diann_exe_path = diann_path
        setting.ms_exe_path = msconvert_path

        notify_email = self.run_info_panel.config_panel.notify_email_text.GetValue()
        wx_token = self.run_info_panel.config_panel.wx_token_text.GetValue()
        inst_id = self.run_info_panel.config_panel.run_prefix_text.GetValue()
        setting.notify_email = notify_email
        setting.wx_token = wx_token
        setting.inst_id = inst_id
        setting.save_config()

        # 每次执行都输出为不同的目录下
        thread_output_dir_path = output_path
        try:
            self.analysis_thread = AnalysisThread(diann_path, msconvert_path, thread_output_dir_path, inst_name,
                                                  run_prefix, self.choose_file_list, notify_email, wx_token)
            self.analysis_thread.daemon = True
            self.analysis_thread.start()
            # # 改变Finished按钮的颜色，及文字
            self.analysis_start()
        except Exception as e:
            logger.info('start analysis exception')
            msg_box = wx.MessageDialog(None, 'Start analysis exception {}'.format(e), 'alert',
                                       wx.YES_DEFAULT | wx.ICON_ERROR)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

    # def setting_save(self, event):
    #     default_font = self.set_panel.default_font_ctrl.GetSelectedFont()
    #
    #     # wx_notify_token = self.set_panel.wx_notify_token_text.GetValue()
    #     wx_notify_token = ''
    #
    #     default_font_dict = {
    #         'Family': default_font.Family,
    #         'FaceName': default_font.FaceName,
    #         'Weight': default_font.Weight,
    #         'PointSize': default_font.PointSize,
    #     }
    #
    #     setting_info = (
    #         default_font_dict, wx_notify_token)
    #     setting_pkl_path = os.path.join(common_config['setting']['pkl'])
    #     with open(setting_pkl_path, 'wb') as f:
    #         pickle.dump(setting_info, f)
    #
    #     # 创建提示对话框
    #     dlg = wx.MessageDialog(None, "The setting information is saved and will take effect after restarting.",
    #                            "Message", wx.OK)
    #     # 显示对话框
    #     result = dlg.ShowModal()
    #     # 关闭对话框
    #     dlg.Destroy()

    def stop_btn_click(self, event):
        logger.info('----click stop analysis button-------')
        # 修改按钮为Stopping
        self.run_info_panel.run_control_panel.stop_button.SetLabel('Stopping')
        self.run_info_panel.run_control_panel.stop_button.Disable()
        # 发送stop通知
        if self.analysis_thread is not None:
            self.analysis_thread.set_run_flag(False)
        self.run_info_panel.run_control_panel.run_status_label.SetLabel('Stopping')
        if self.analysis_thread is None:
            pub.sendMessage('analysis_over', msg=True)

    # 订阅分析过程中的消息
    def sub_analysis_info(self, msg):
        logger.info('receive msg: {}'.format(msg))
        # {'status': 1, 'msg': 'xxxx', 'start_time':5555}
        an_info = json.loads(msg)
        status = an_info['status']
        step = an_info['step']
        msg = an_info['msg']
        if status == 99:
            self.sub_analysis_over(msg)
        else:
            if msg is not None and len(msg) > 0:
                self.run_info_panel.log_panel.log_text.AppendText('{}\r\n'.format(an_info['msg']))
            if status == 1:
                # 该阶段正常结束，step进度+1
                self.sub_analysis_step(None)
            elif status == 11:
                # 完成一个msconvert
                self.add_one_msconvert_deal()
            elif status == 21:
                # 完成一个diann
                self.add_one_diann_deal()
            elif status == 2:
                # 手动停止
                self.analysis_stop_stopped()
            elif status == 3:
                # 异常停止
                self.analysis_error_stopped()
            elif status == 9:
                pass

    def monitor_log(self, msg):
        logger.info('receive monitor msg: {}'.format(msg))
        an_info = json.loads(msg)
        msg = an_info['msg']
        self.monitor_panel.monitor_log_panel.log_text.AppendText('{}\r\n'.format(msg))
        # 由于日志过多会影响性能，所以，到一定数量的时候，要清空

    def sub_reload_data(self, msg):
        logger.info('reload data')
        self.data_panel_event_handler.load_grid_data()

    # 分析完成消息处理
    def sub_analysis_over(self, msg):
        logger.info('sub analysis over msg')
        self.run_info_panel.log_panel.log_text.AppendText('{}\r\n'.format(msg))
        self.change_status_btn_label_finished()
        self.data_panel_event_handler.load_grid_data()

    def sub_analysis_step(self, msg):
        self.deal_step += 1
        self.run_info_panel.output_panel.all_progress_gauge.SetValue(self.deal_step)
        self.run_info_panel.output_panel.all_pro_label.SetLabel('{}/{}'.format(self.deal_step, self.all_step_count))

    # 增加一次msconvert处理完成
    def add_one_msconvert_deal(self):
        self.msconvert_deal_count += 1
        self.run_info_panel.output_panel.msconvert_gauge.SetValue(self.msconvert_deal_count)
        self.run_info_panel.output_panel.msconvert_pro_label.SetLabel(
            '{}/{}'.format(self.msconvert_deal_count, self.msconvert_all_count))

    # 增加一次diann处理完成
    def add_one_diann_deal(self):
        self.diann_deal_count += 1
        self.run_info_panel.output_panel.diann_gauge.SetValue(self.diann_deal_count)
        self.run_info_panel.output_panel.diann_pro_label.SetLabel(
            '{}/{}'.format(self.diann_deal_count, self.diann_all_count))

    '''
    手动停止
    1、状态颜色不变
    2、Run释放
    3、Stop禁用
    '''

    def analysis_stop_stopped(self):
        self.run_info_panel.run_control_panel.run_status_label.SetLabel('STOPPED')

        self.run_info_panel.run_control_panel.stop_button.SetLabel('Stop')
        self.run_info_panel.run_control_panel.stop_button.Disable()

        self.run_info_panel.run_control_panel.run_button.Enable()

    '''
    分析异常停止了
    1、修改状态标记为ERROR
    2、Run释放
    3、Stop禁用
    '''

    def analysis_error_stopped(self):
        self.run_info_panel.run_control_panel.run_status_button.SetBackgroundColour(ERROR_COLOR)
        self.run_info_panel.run_control_panel.run_status_label.SetLabel('ERROR')

        self.run_info_panel.run_control_panel.stop_button.SetLabel('Stop')
        self.run_info_panel.run_control_panel.stop_button.Disable()

        self.run_info_panel.run_control_panel.run_button.Enable()

    '''
    开始分析
    1、修改状态标记为RUNNING
    2、Run禁用
    3、Stop释放
    '''

    def analysis_start(self):
        # 日志区域清空
        self.run_info_panel.log_panel.log_text.SetValue('')

        self.run_info_panel.run_control_panel.run_status_button.SetBackgroundColour(RUNNING_COLOR)
        self.run_info_panel.run_control_panel.run_status_label.SetLabel('Running')

        self.run_info_panel.run_control_panel.stop_button.SetLabel('Stop')
        self.run_info_panel.run_control_panel.stop_button.Enable()

        self.run_info_panel.run_control_panel.run_button.Disable()

    def change_status_btn_label_finished(self):
        self.run_info_panel.run_control_panel.run_status_button.SetBackgroundColour(OVER_COLOR)
        self.run_info_panel.run_control_panel.run_status_label.SetLabel('Finished')

        self.run_info_panel.run_control_panel.run_button.Enable()

        self.run_info_panel.run_control_panel.stop_button.SetLabel('Stop')
        self.run_info_panel.run_control_panel.stop_button.Disable()

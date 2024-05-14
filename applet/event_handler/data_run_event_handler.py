# import os
#
# import wx
#
# from applet.gui.run_info_panel import RunInfoPanel
# from applet.logger_utils import logger
#
#
# class DataRunEventHandler(object):
#     def __init__(self, run_info_panel: RunInfoPanel):
#         self.run_info_panel = run_info_panel
#
#     def run_btn_click(self, choose_file_list):
#         # 获取diann路径
#         # logger.info('----click start analysis button-------')
#         # if len(choose_file_list) == 0:
#         #     msg_box = wx.MessageDialog(None, 'please choose raw file', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
#         #     if msg_box.ShowModal() == wx.ID_YES:
#         #         msg_box.Destroy()
#         #     return
#         # cwd = os.getcwd()
#         # self.run_init()
#         diann_path = self.run_info_panel.config_panel.diann_path_text.GetValue()
#         # msconvert路径
#         msconvert_path = self.run_info_panel.config_panel.msconvert_path_text.GetValue()
#
#         # 质谱文件路径
#         cwd = os.getcwd()
#         output_path = self.run_info_panel.input_panel.file_output_dir_text.GetValue()
#         output_path = os.path.join(cwd, output_path)
#         if output_path is None or len(output_path) == 0:
#             msg_box = wx.MessageDialog(None, 'no selected output dir', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
#             if msg_box.ShowModal() == wx.ID_YES:
#                 msg_box.Destroy()
#             return
#
#         # 转为绝对路径
#         fasta_path = self.run_info_panel.config_panel.fasta_path_text.GetValue()
#         if not os.path.exists(fasta_path):
#             msg_box = wx.MessageDialog(None, 'fasta is not exist', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
#             if msg_box.ShowModal() == wx.ID_YES:
#                 msg_box.Destroy()
#             return
#         # 检查ins id
#         ins_select_id = self.run_info_panel.config_panel.ins_id_choice.GetSelection()
#         if ins_select_id == -1:
#             msg_box = wx.MessageDialog(None, 'Inst is not selected', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
#             if msg_box.ShowModal() == wx.ID_YES:
#                 msg_box.Destroy()
#             return
#
#         if not os.path.exists(output_path):
#             os.makedirs(output_path)
#         # 开始分析
#         logger.info('----start analysis-------')
#         setting.output_dir_base = output_path
#         setting.diann_exe_path = diann_path
#         setting.ms_exe_path = msconvert_path
#
#         notify_email = self.run_info_panel.config_panel.notify_email_text.GetValue()
#         setting.notify_email = notify_email
#         setting.save_config()
#
#         # 每次执行都输出为不同的目录下
#         thread_output_dir_path = output_path
#         try:
#             self.analysis_thread = AnalysisThread(diann_path, msconvert_path, thread_output_dir_path,
#                                                   fasta_path, ins_select_id, self.choose_file_list, notify_email)
#             self.analysis_thread.daemon = True
#             self.analysis_thread.start()
#             # # 改变Finished按钮的颜色，及文字
#             self.analysis_start()
#         except Exception as e:
#             logger.info('start analysis exception')
#             msg_box = wx.MessageDialog(None, 'Start analysis exception {}'.format(e), 'alert',
#                                        wx.YES_DEFAULT | wx.ICON_ERROR)
#             if msg_box.ShowModal() == wx.ID_YES:
#                 msg_box.Destroy()
#             return
#
#     def stop_btn_click(self, event):
#         logger.info('----click stop analysis button-------')
#         # 修改按钮为Stopping
#         self.run_info_panel.run_control_panel.stop_button.SetLabel('Stopping')
#         self.run_info_panel.run_control_panel.stop_button.Disable()
#         # 发送stop通知
#         if self.analysis_thread is not None:
#             self.analysis_thread.set_run_flag(False)
#         self.run_info_panel.run_control_panel.run_status_label.SetLabel('Stopping')
#         if self.analysis_thread is None:
#             pub.sendMessage('analysis_over', msg=True)

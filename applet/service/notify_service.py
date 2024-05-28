import os
import smtplib
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

from applet import common_utils
from applet.db import db_utils_run_data
from applet.default_config import setting
from applet.obj.DBEntity import RunInfo, RunData, PredInfo
from applet.obj.Entity import FileInfo
from applet.service import common_service

common_config = common_utils.read_yml()

# 配置邮箱服务器信息
mail_host = common_config['notify']['mail_host']  # 设置服务器
mail_user = common_config['notify']['mail_user']  # 用户名
mail_pass = common_config['notify']['mail_pass']  # 口令是授权码，不是邮箱密码


class NotifyService(common_service.CommonService):
    def __init__(self, notify_email: str, wx_token, base_output_path, file_list: [FileInfo], logger,
                 step=13,
                 pub_channel='analysis_info', start_time=0):
        common_service.CommonService.__init__(self, base_output_path, file_list, logger, step, pub_channel, start_time)
        self.notify_email = notify_email
        self.wx_token = wx_token

    # 处理转换
    def deal_process(self):
        logger = self.logger
        try:
            self.send_msg(0, 'Sending the result to: {}'.format(self.notify_email), with_time=True)
            # 查询这些文件的数据
            run_info_list, pred_info_list, run_data_list = self.query_build_data()
            self.deal_send_email(run_info_list, pred_info_list)
            self.deal_send_wx(run_info_list, pred_info_list, run_data_list)
            self.send_msg(1, msg='')
            return True
        except Exception as e:
            logger.exception('msg send exception')
            self.send_msg(3, msg='Notify send exception: {}'.format(e))
        return True

    def query_build_data(self):
        run_id_list = [f.run_id for f in self.file_list]
        run_info_list = db_utils_run_data.query_run_info_list(run_id_list)
        seq_id_list = [d.seq_id for d in run_info_list]
        pred_info_list = db_utils_run_data.query_all_pred_info(seq_id_list)

        run_data_list = db_utils_run_data.query_run_data(seq_id_list)

        return run_info_list, pred_info_list, run_data_list

    def message_config(self, run_info_list, pred_info_list):
        """
        配置邮件信息
        :return: 消息对象
        """
        # 第三方 SMTP 服务
        lc_dict = {}
        ms_dict = {}
        for pred_info in pred_info_list:
            pred_key = pred_info.pred_key
            if pred_key not in ['lc', 'ms']:
                continue
            if pred_info.pred_label == 0:
                pred_label = 'qualified '
            elif pred_info.pred_label == 1:
                pred_label = 'unqualified'
            else:
                pred_label = 'unknown'
            if pred_key == 'lc':
                lc_dict[pred_info.seq_id] = pred_label
            elif pred_key == 'ms':
                ms_dict[pred_info.seq_id] = pred_label

        send_data_list = []
        inst_list = []
        for run_info in run_info_list:
            send_data_list.append(
                '{}_{}_{}_{}'.format(run_info.run_id, run_info.run_name, lc_dict[run_info.seq_id],
                                     ms_dict[run_info.seq_id]))
            inst_list.append(run_info.run_prefix)
        inst_list = list(set(inst_list))

        subject_str = '\n'.join(send_data_list)

        message = MIMEMultipart()  # 多个MIME对象
        message['From'] = 'iDIA-QC<{}>'.format(mail_user)
        message['To'] = self.notify_email
        message['Subject'] = Header(subject_str, 'utf-8')  # 主题

        if len(run_info_list) == 1:
            content_str = 'Dear iDIA-QC user, <br/>'
            content_str = content_str + 'The MS raw file you uploaded with the name {} has been analyzed. Here is a summary of the results.<br/>'.format(
                run_info_list[0].run_name)
            content_str = content_str + 'For detailed results and illustrations, please refer to the attached HTML file. <br/>'
            content_str = content_str + 'Thank you for using our service.  <br/>'
            content_str = content_str + 'If you have any further questions, please upload them to GitHub. <a href="{}">Click there</a> <br/>'.format(
                setting.github_url)
            content_str = content_str + 'iDIA-QC Support, iDIA-QC team'
        else:
            # 是否是单个仪器
            if len(inst_list) == 1:
                content_str = 'Dear iDIA-QC user, <br/>'
                content_str = content_str + 'The MS raw files you uploaded have been analyzed. Here is a summary of the results. For detailed results and illustrations, please refer to the attached HTML file. <br/>'
                content_str = content_str + 'Thank you for using our service.  <br/>'
                content_str = content_str + 'If you have any further questions, please upload them to GitHub. <a href="{}">Click there</a> <br/>'.format(
                    setting.github_url)
                content_str = content_str + 'iDIA-QC Support, iDIA-QC team'
            else:
                content_str = 'Dear iDIA-QC user, <br/>'
                content_str = content_str + 'The MS raw files you uploaded have been analyzed. Here is a summary of the results. For detailed results and illustrations, please refer to the attached HTML files. The results from each instrument are placed in a separate HTML file. <br/>'
                content_str = content_str + 'Thank you for using our service.  <br/>'
                content_str = content_str + 'If you have any further questions, please upload them to GitHub. <a href="{}">Click there</a> <br/>'.format(
                    setting.github_url)
                content_str = content_str + 'iDIA-QC Support, iDIA-QC team'
        content = MIMEText(content_str, 'html')
        message.attach(content)  # 添加内容
        return message

    def send_mail(self, run_info_list, pred_info_list):
        logger = self.logger
        """
        发送邮件
        :param message: 消息对象
        :return: None
        """
        receivers = self.notify_email.split(';')
        logger.info('email receivers: {}'.format(receivers))
        message = self.message_config(run_info_list, pred_info_list)
        # # 添加Excel类型附件
        # 添加html
        pic_dir_path = os.path.join(self.base_output_path, 'pic')
        if os.path.exists(pic_dir_path):
            html_list = os.listdir(pic_dir_path)
            for html_name in html_list:
                xlsx = MIMEApplication(open(os.path.join(pic_dir_path, html_name), 'rb').read())  # 打开Excel,读取Excel文件
                xlsx["Content-Type"] = 'application/octet-stream'  # 设置内容类型
                xlsx.add_header('Content-Disposition', 'attachment', filename=html_name)  # 添加到header信息
                message.attach(xlsx)
        smtpObj = smtplib.SMTP(mail_host, port=587, timeout=30)  # 使用SSL连接邮箱服务器
        smtpObj.starttls()
        smtpObj.login(mail_user, mail_pass)  # 登录服务器
        smtpObj.sendmail(mail_user, receivers, message.as_string())  # 发送邮件
        logger.info('邮件发送成功')

    '''
    处理邮件发送的逻辑
    '''

    def deal_send_email(self, run_info_list, pred_info_list):
        logger = self.logger
        try:
            if self.notify_email is None or len(self.notify_email) == 0:
                logger.info('There is no need email to notify')
                self.send_msg(1, msg='')
                return True
            self.send_mail(run_info_list, pred_info_list)
        except Exception as e:
            logger.exception('email send exception')
            self.send_msg(3, msg='Email send exception: {}'.format(e))

    '''
    处理微信发送
    '''

    def deal_send_wx(self, run_info_list, pred_info_list, run_data_list):
        logger = self.logger
        try:
            if self.wx_token is None or len(self.wx_token) == 0:
                self.send_msg(1, msg='There is no need email to notify')
                return True
            # 查询这些文件的数据
            title, markdown_content = self.build_wx_msg_markdown_content(run_info_list, pred_info_list, run_data_list)
            token_list = self.wx_token.split(';')
            for token in token_list:
                self.send_wx_msg(token, title, markdown_content)
        except Exception as e:
            logger.exception('wx send exception')
            self.send_msg(3, msg='Email send exception: {}'.format(e))

    def send_wx_msg(self, token, title, markdown_content):
        logger = self.logger
        try:
            url = 'http://www.pushplus.plus/send'
            data_json = {
                'token': token,
                'template': 'markdown',
                'title': title,
                'content': markdown_content
            }
            logger.info('push wx msg：{}'.format(data_json))
            resp = requests.post(url, json=data_json)
            logger.info('push wx success：{}'.format(resp.text))
        except Exception:
            logger.exception('push wx exception')

    def build_wx_msg_markdown_content(self, run_info_list: [RunInfo], pred_info_list: [PredInfo],
                                      run_data_list: [RunData]):
        title = 'DIA分析结束'

        new_key_map = {'F3': 'F2', 'F4': 'F3', 'F5': 'F4', 'F6': 'F5', 'F7': 'F6', 'F8': 'F7', 'F9': 'F1', 'F10': 'F8', 'F11': 'F9', 'F12': 'F10',
                       'F13': 'F11', 'F14': 'F12', 'F15': 'F13', 'F16': 'F14', 'F17': 'F15', 'lc': 'LC', 'ms': 'MS', 'F2': 'F1' }

        pred_dict = {}
        run_id_qual_feat_dict = {}
        run_id_unqual_feat_dict = {}
        for pred_info in pred_info_list:
            if pred_info.pred_label == 0:
                if pred_info.pred_label not in ['lc', 'ms']:
                    run_id_qual_feat_dict.setdefault(pred_info.run_id, []).append(new_key_map.get(pred_info.pred_key))
                pred_dict['{}_{}'.format(pred_info.run_id, pred_info.pred_key)] = 'Qualified'

            elif pred_info.pred_label == 1:
                if pred_info.pred_label not in ['lc', 'ms']:
                    run_id_unqual_feat_dict.setdefault(pred_info.run_id, []).append(new_key_map.get(pred_info.pred_key))
                pred_dict['{}_{}'.format(pred_info.run_id, pred_info.pred_key)] = 'Unqualified'

        run_data_seq_dict = {}
        for run_data in run_data_list:
            run_data_seq_dict['{}_{}'.format(run_data.seq_id, run_data.data_tag)] = run_data.data_val

        run_id_name_list = ['']
        run_id_name_pred_list = ['']
        run_id_qual_feat_list = ['']
        run_id_unqual_feat_list = ['']
        f6_data_list = ['']
        f7_data_list = ['']
        f8_data_list = ['']
        f10_data_list = ['']
        f11_data_list = ['']
        f13_data_list = ['']
        f14_data_list = ['']
        f17_data_list = ['']
        for run_info in run_info_list:
            run_id_name_list.append('{}: {}'.format(run_info.run_id, run_info.run_name))
            run_id_name_pred_list.append(
                '{}: {}; {}'.format(run_info.run_id, pred_dict['{}_{}'.format(run_info.run_id, 'lc')],
                                    pred_dict['{}_{}'.format(run_info.run_id, 'ms')]))

            qual_data_list = run_id_qual_feat_dict.setdefault(run_info.run_id, [])

            if len(qual_data_list) == 0:
                run_id_qual_feat_list.append(
                    '{}: {}'.format(run_info.run_id, 'None'))
            else:
                run_id_qual_feat_list.append(
                    '{}: {}'.format(run_info.run_id, ';'.join(qual_data_list)))

            unqual_data_list = run_id_unqual_feat_dict.setdefault(run_info.run_id, [])
            if len(unqual_data_list) == 0:
                run_id_unqual_feat_list.append(
                    '{}: {}'.format(run_info.run_id, 'None'))
            else:
                run_id_unqual_feat_list.append(
                    '{}: {}'.format(run_info.run_id, ';'.join(unqual_data_list)))

            f6_data_list.append(
                '{}: {}'.format(run_info.run_id, self.format_data(run_data_seq_dict.get('{}_{}'.format(run_info.seq_id, '6')))))
            f7_data_list.append(
                '{}: {}'.format(run_info.run_id, self.format_data(run_data_seq_dict.get('{}_{}'.format(run_info.seq_id, '7')))))

            f8_data_list.append(
                '{}: {}'.format(run_info.run_id, self.format_data(run_data_seq_dict.get('{}_{}'.format(run_info.seq_id, '8')))))
            f10_data_list.append(
                '{}: {}'.format(run_info.run_id, self.format_data(run_data_seq_dict.get('{}_{}'.format(run_info.seq_id, '10')))))

            f11_data_list.append(
                '{}: {}'.format(run_info.run_id, self.format_data(run_data_seq_dict.get('{}_{}'.format(run_info.seq_id, '11')))))
            f13_data_list.append(
                '{}: {}'.format(run_info.run_id, self.format_int_data(run_data_seq_dict.get('{}_{}'.format(run_info.seq_id, '13')))))
            f14_data_list.append(
                '{}: {}'.format(run_info.run_id, self.format_int_data(run_data_seq_dict.get('{}_{}'.format(run_info.seq_id, '14')))))
            f17_data_list.append(
                '{}: {}'.format(run_info.run_id, self.format_data(run_data_seq_dict.get('{}_{}'.format(run_info.seq_id, '17')))))

        markdown_content0 = '# A Swift Glimpse at Metric Performance\n'
        markdown_content1 = '### Run_ID: {}'.format('\n- * #### '.join(run_id_name_list))
        markdown_content2 = '### LC and MS performance: {}'.format('\n- * #### '.join(run_id_name_pred_list))

        markdown_content3 = '### Qualified metrics: {}'.format('\n- * #### '.join(run_id_qual_feat_list))
        # if len()
        markdown_content4 = '### Unqualified metrics: {}'.format('\n- * #### '.join(run_id_unqual_feat_list))
        markdown_content5 = '## Metric performance:'

        markdown_content6 = '### F5 (Intensity variation of adjacent MS1 scan, %): {}'.format('\n- * #### '.join(f6_data_list))
        markdown_content7 = '### F6 (Median MS1 accuracy of identified precursors, ppm): {}'.format(
            '\n- * #### '.join(f7_data_list))
        markdown_content8 = '### F7 (TIC MS1 signal): {}'.format('\n- * #### '.join(f8_data_list))
        markdown_content9 = '### F8 (Median MS2 accuracy of identified precursors, ppm): {}'.format(
            '\n- * #### '.join(f10_data_list))
        markdown_content10 = '### F9 (TIC MS2 signal): {}'.format('\n- * #### '.join(f11_data_list))
        markdown_content11 = '### F11 (Number of identified peptides): {}'.format('\n- * #### '.join(f13_data_list))
        markdown_content12 = '### F12 (Number of identified proteins): {}'.format('\n- * #### '.join(f14_data_list))
        markdown_content13 = '### F15 (Ion mobility accuracy): {}'.format('\n- * #### '.join(f17_data_list))
        markdown_content14 = '## Only the metrics exhibiting unique values matching those of the raw file are presented here; for further metrics, kindly consult the email attachment (html file).'

        markdown_content_list = []
        markdown_content_list.append(markdown_content0)
        markdown_content_list.append(markdown_content1)
        markdown_content_list.append(markdown_content2)
        markdown_content_list.append(markdown_content3)
        markdown_content_list.append(markdown_content4)
        markdown_content_list.append(markdown_content5)
        markdown_content_list.append(markdown_content6)
        markdown_content_list.append(markdown_content7)
        markdown_content_list.append(markdown_content8)
        markdown_content_list.append(markdown_content9)
        markdown_content_list.append(markdown_content10)
        markdown_content_list.append(markdown_content11)
        markdown_content_list.append(markdown_content12)
        markdown_content_list.append(markdown_content13)
        markdown_content_list.append(markdown_content14)
        markdown_content = '\n'.join(markdown_content_list)
        return title, markdown_content

    def format_data(self, fn_data):
        if not fn_data:
            return None
        if type(fn_data) == str:
            fn_data = float(fn_data)
        if fn_data > 100000:
            return "{:,.2E}".format(fn_data)
        else:
            return "{:,.2f}".format(fn_data)

    def format_int_data(self, fn_data):
        if not fn_data:
            return None
        if type(fn_data) == str:
            fn_data = int(fn_data)
        if fn_data > 100000:
            return "{:,.3e}".format(fn_data)
        else:
            return "{:,}".format(fn_data)

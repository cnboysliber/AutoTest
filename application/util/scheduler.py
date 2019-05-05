# -*- coding:utf-8 -*-
import os
from datetime import datetime, timedelta

from application import app
from application import web_root
from application.api import run_log as logApi
from application.api import email as emailApi
from application.api import batch as batchApi
from application.util.execute_test import executor
from application.util import email_send as emailSendApi


def get_email_batch_report():
    email_to_batchs = emailApi.get_email_batch()
    email_dicts = emailApi.query_email_id_to_info()
    to_time = datetime.strftime(datetime.now() - timedelta(hours=8), '%Y-%m-%d %H:%M:%S.000')
    from_time = datetime.strftime((datetime.now() - timedelta(days=1)), '%Y-%m-%d 16:00:00.000')
    batch_logs = logApi.get_batch_run_log_info(from_time=from_time, to_time=to_time)
    id_to_batch_info = batchApi.get_batch_id_to_info()
    batch_id_to_logs = {}
    for batch_log in batch_logs:
        if batch_log['batch_id'] not in batch_id_to_logs.keys():
            batch_id_to_logs[batch_log['batch_id']] = {}
            batch_id_to_logs[batch_log['batch_id']]['run_count'] = 1
            batch_id_to_logs[batch_log['batch_id']]['batch_name'] = \
                id_to_batch_info[batch_log['batch_id']]['batch_name']
            batch_id_to_logs[batch_log['batch_id']]['use_case_num'] = batch_log['use_case_count']
            batch_id_to_logs[batch_log['batch_id']]['fail_count'] = 0
        else:
            batch_id_to_logs[batch_log['batch_id']]['run_count'] += 1
            if batch_log['pass_rate'] < 100:
                fail_count = logApi.get_use_case_run_log_count(batch_run_log_id=batch_log['id'],
                                                               is_pass='0', auto_run=1)
                batch_id_to_logs[batch_log['batch_id']]['fail_count'] += fail_count

    email_to_batch_report = {}
    for email_id, batch_ids in email_to_batchs.items():
        email_to_batch_report[email_dicts[email_id]['email_address']] = \
            {k: v for k, v in batch_id_to_logs.items() if k in batch_ids}

        if email_to_batch_report.get(email_dicts[email_id]['email_address'], None):
            email_to_batch_report[email_dicts[email_id]['email_address']]['name'] = email_dicts[email_id]['email_name']

    return email_to_batch_report


def get_send_message(batch_reports):
    now_time_point = datetime.now().strftime('%Y/%m/%d %H:%M')
    cur_wk_path = os.path.join(web_root, 'static', 'email_template.html')

    with open(cur_wk_path, 'r', encoding="utf-8") as fp:
        fp_data = fp.read()
        fp_data = fp_data.format(now_time_point)
        index = fp_data.find('<tbody>')
        before_insert_data = fp_data[:index]
        after_insert_data = fp_data[index:]
        for k, report in batch_reports.items():
            if k == 'name':
                continue
            report_td = get_table_tmp().format(report['batch_name'],
                                               report['use_case_num'],
                                               report['run_count'],
                                               report['fail_count'],
                                               round(float(report['run_count'] * report['use_case_num'] -
                                                     report['fail_count']) * 100
                                               / (report['run_count'] * report['use_case_num']), 1),
                                               datetime.now().strftime('%Y-%m-%d')
                                               )
            before_insert_data += report_td
        message = before_insert_data + after_insert_data
    return message


def get_table_tmp():
    return '<tr>' \
           '<td role="row">{0}</td>' \
           '<td role="row">{1}</td>' \
           '<td role="row">{2}</td>' \
           '<td role="row">{3}</td>' \
           '<td role="row">{4}%</td>' \
           '<td role="row">{5}</td>' \
           '</tr>'


def send_report_to_email():
    with app.app_context():
        try:
            email_batch_reports = get_email_batch_report()
            email_data = dict()
            email_data['str_url'] = 'http://push.huanjixia.com/email-interface'
            email_data['title'] = '自动化巡检报表'

            if not email_batch_reports:
                return
            for email_addr, report_data in email_batch_reports.items():
                email_data['address'] = dict()
                if not report_data:
                    continue
                email_data['body'] = get_send_message(report_data)
                email_data['address'][report_data['name']] = email_addr
                executor.submit(emailSendApi.email_send, **email_data)
            return True,
        except Exception as e:
            return False, e


if __name__ == '__main__':
    send_report_to_email()
    pass




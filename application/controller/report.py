# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask import request, jsonify
from application.api import report as ReportAPI
from application.api import run_log as RunLogAPI
from application.api import use_case as UseCaseAPI
from application.api import menutree as MenuTreeAPI
from application import app
from application.util.exception import try_except
from application.util import get_function_of_data, get_line_of_data
from application.controller import login_required, localhost_required, report_data_manager
from application.config.default import *


@app.route('/report/minutes_report/add', methods=['GET'])
@localhost_required
@try_except
def add_minutes_report():
    """
    :return:
    """
    now_time_point = datetime.utcnow()
    before_time_point = now_time_point - timedelta(minutes=MINUTE_TIME_LENGTH)
    to_time = now_time_point.strftime(MINUTE_TIME_FMT)
    from_time = before_time_point.strftime(MINUTE_TIME_FMT)

    use_case_run_log_list = RunLogAPI.get_use_case_run_log(from_time=from_time, to_time=to_time, auto_run=True)
    use_case_id_list = list(set([use_case_run_log.get('use_case_id') for use_case_run_log in use_case_run_log_list]))
    use_case_info_dict = UseCaseAPI.get_multi_use_case(use_case_id_list)

    all_report_data = {}
    single_report_data = {}
    for use_case_run_log in use_case_run_log_list:
        use_case_id = use_case_run_log.get('use_case_id')
        function_id = use_case_info_dict[use_case_id].get('function_id')
        if all_report_data.get(function_id, None):
            single_report_data = all_report_data[function_id]
            single_report_data['run_count'] += 1
            if use_case_run_log.get('is_pass'):
                single_report_data['success_count'] += 1
            else:
                single_report_data['fail_count'] += 1
            single_report_data['sum_time'] += use_case_run_log.get('cost_time')
            cost_time = use_case_run_log.get('cost_time')
            if single_report_data['max_time'] < cost_time:
                single_report_data['max_time'] = cost_time
        else:
            if single_report_data:
                single_report_data = {}

            single_report_data['function_id'] = function_id
            single_report_data['run_count'] = 1
            if use_case_run_log.get('is_pass'):
                single_report_data['success_count'] = 1
                single_report_data['fail_count'] = 0
            else:
                single_report_data['success_count'] = 0
                single_report_data['fail_count'] = 1
            single_report_data['sum_time'] = use_case_run_log.get('cost_time')
            single_report_data['max_time'] = use_case_run_log.get('cost_time')
            all_report_data[function_id] = single_report_data
    all_report_list = all_report_data.values()
    for report_data in all_report_list:
        average_time = report_data['sum_time'] / report_data['run_count']
        pass_rate = round(report_data['success_count'] / report_data['run_count'], 3)
        report_data['average_time'] = average_time
        report_data['pass_rate'] = pass_rate
        if report_data['function_id']:
            ReportAPI.add_minutes_report(**report_data)
    return jsonify({'success': True})


@app.route('/report/minutes_report/info', methods=['POST'])
@login_required
@try_except
def query_minutes_report_info():
    """
    查询分钟报表数据
    :param: 时间格式：%Y-%m-%d %H:%M:%S
    :return:
    """
    param_kwarg = request.get_json()
    now_time_point = datetime.now()
    to_time_point = now_time_point
    from_time_point = now_time_point
    if 'to_time' not in param_kwarg or not param_kwarg.get('to_time'):
        param_kwarg['to_time'] = to_time_point.strftime(MINUTE_TIME_FMT)
    else:
        to_time = param_kwarg['to_time']
        to_time = datetime.strptime(to_time, '%Y-%m-%d') + timedelta(days=1)
        to_time = to_time.strftime(MINUTE_TIME_FMT)
        param_kwarg.update({"to_time": to_time})

    if 'from_time' not in param_kwarg or not param_kwarg.get('from_time', None):
        param_kwarg['from_time'] = from_time_point.strftime(DAY_TIME_FMT)
    else:
        from_time = param_kwarg['from_time']
        from_time = datetime.strptime(from_time, '%Y-%m-%d')
        from_time = from_time.strftime(DAY_TIME_FMT)
        param_kwarg.update({"from_time": from_time})
    report_info_list = ReportAPI.get_minutes_report_info(**param_kwarg)
    menu_tree_info = MenuTreeAPI.query_line_relation()
    for report_info in report_info_list:
        function_id = report_info.get('function_id')
        if menu_tree_info.get(function_id, None):
            report_info.update(menu_tree_info[function_id])
    if param_kwarg.get('data_type', None):
        report_info_list = get_line_of_data(report_info_list, '%Y-%m-%d %H:%M')
        business_info_list = MenuTreeAPI.query_business_line()
        business_info_dict = {}
        for business_info in business_info_list:
            business_info_dict[business_info['id']] = business_info

        for report_info in report_info_list:
            business_line_id = report_info.get('business_line_id')
            report_info.update(business_info_dict[business_line_id])
        if report_info_list:
            chartist_data = report_data_manager(report_info_list, '%Y-%m-%d %H:%M')
        else:
            chartist_data = {}
        return jsonify({'success': True, 'res': chartist_data})
    return jsonify({'success': True, 'res': report_info_list})


@app.route('/report/day_report/add', methods=['GET'])
@try_except
@localhost_required
def add_day_report():
    """
    :return:
    """
    now_time_point = datetime.now()
    before_time_point = (now_time_point + timedelta(days=1)) - timedelta(days=DAY_TIME_LENGTH)
    to_time = (now_time_point + timedelta(days=1)).strftime(DAY_TIME_FMT)
    from_time = before_time_point.strftime(DAY_TIME_FMT)

    use_case_data_list = ReportAPI.get_minutes_report_info(from_time=from_time, to_time=to_time)
    report_info_list = ReportAPI.get_day_report_info(from_time=from_time, to_time=to_time)
    report_info_dict = {}
    for report_info in report_info_list:
        report_info_dict[report_info['function_id']] = report_info
    use_case_report_list = get_function_of_data(use_case_data_list)
    for report_data in use_case_report_list:
        function_id = report_data['function_id']
        if report_info_dict and report_info_dict.get(function_id, None):
            id = report_info_dict[function_id].get('id')
            report_data['id'] = id
            ReportAPI.modify_day_report(**report_data)
        else:
            ReportAPI.add_day_report(**report_data)
    return jsonify({'success': True})


@app.route('/report/day_report/info', methods=['POST'])
@login_required
@try_except
def query_day_report_info():
    """
    查询日报表数据
    :param: 时间格式：%Y-%m-%d
    :return:
    """
    param_kwarg = request.get_json()
    now_time_point = datetime.now()
    to_time_point = now_time_point + timedelta(days=1)
    from_time_point = now_time_point - relativedelta(months=1)
    if 'to_time' not in param_kwarg or not param_kwarg.get('to_time'):
        param_kwarg['to_time'] = to_time_point.strftime(DAY_TIME_FMT)
    else:
        to_time = param_kwarg['to_time']
        to_time = datetime.strptime(to_time, '%Y-%m-%d') + timedelta(days=1)
        to_time = to_time.strftime(DAY_TIME_FMT)
        param_kwarg.update({"to_time": to_time})

    if 'from_time' not in param_kwarg or not param_kwarg.get('from_time', None):
        param_kwarg['from_time'] = from_time_point.strftime(DAY_TIME_FMT)
    else:
        from_time = param_kwarg['from_time']
        from_time = datetime.strptime(from_time, '%Y-%m-%d')
        from_time = from_time.strftime(DAY_TIME_FMT)
        param_kwarg.update({"from_time": from_time})

    report_info_list = ReportAPI.get_day_report_info(**param_kwarg)
    menu_tree_info = MenuTreeAPI.query_line_relation()
    for report_info in report_info_list:
        function_id = report_info.get('function_id')
        report_info.update(menu_tree_info[function_id])
    if param_kwarg.get('data_type', None):
        report_info_list = get_line_of_data(report_info_list)
        business_info_list = MenuTreeAPI.query_business_line()
        business_info_dict = {}
        for business_info in business_info_list:
            business_info_dict[business_info['id']] = business_info

        for report_info in report_info_list:
            business_line_id = report_info.get('business_line_id')
            report_info.update(business_info_dict[business_line_id])
        if report_info_list:
            chartist_data = report_data_manager(report_info_list)
        else:
            chartist_data = {}
        return jsonify({'success': True, 'res': chartist_data})
    return jsonify({'success': True, 'res': report_info_list})


@app.route('/report/week_report/add', methods=['GET'])
@localhost_required
@try_except
def add_week_report():
    """
    添加周报表数据
    :return:
    """

    now_time_point = datetime.now()
    day_of_week_num = int(now_time_point.strftime('%u'))  # 每周的第几天（0~6）
    before_time_point = now_time_point - timedelta(days=day_of_week_num)
    to_time = (now_time_point + timedelta(days=1)).strftime(DAY_TIME_FMT)
    from_time = before_time_point.strftime(DAY_TIME_FMT)
    use_case_data_list = ReportAPI.get_day_report_info(from_time=from_time, to_time=to_time)
    report_info_list = ReportAPI.get_week_report_info(from_time=from_time, to_time=to_time)
    report_info_dict = {}
    for report_info in report_info_list:
        report_info_dict[report_info['function_id']] = report_info
    use_case_report_list = get_function_of_data(use_case_data_list)
    for report_data in use_case_report_list:
        function_id = report_data['function_id']
        if report_info_dict and report_info_dict.get(function_id, None):
            id = report_info_dict[function_id].get('id')
            report_data['id'] = id
            ReportAPI.modify_week_report(**report_data)
        else:
            ReportAPI.add_week_report(**report_data)
    return jsonify({'success': True})


@app.route('/report/week_report/info', methods=['POST'])
@login_required
@try_except
def query_week_report_info():
    """
    查询周报表数据，默认查询前4周数据
    :param: 时间格式：%Y-%m-%d
    :return:
    """
    param_kwarg = request.get_json()
    now_time_point = datetime.now()
    day_of_week_num = int(now_time_point.strftime('%w'))
    to_time_point = now_time_point + timedelta(days=7-day_of_week_num)
    from_time_point = now_time_point - timedelta(weeks=4)
    if not param_kwarg.get('to_time', None):
        param_kwarg['to_time'] = to_time_point.strftime(DAY_TIME_FMT)
    else:
        to_time = datetime.strptime(param_kwarg['to_time'], '%Y-%m-%d')
        day_of_week_num = to_time.isocalendar()[2]
        to_time = to_time + timedelta(days=(7 - (day_of_week_num - 1)))
        to_time = to_time.strftime(DAY_TIME_FMT)
        param_kwarg.update({"to_time": to_time})

    if not param_kwarg.get('from_time', None):
        param_kwarg['from_time'] = from_time_point.strftime(DAY_TIME_FMT)
    else:
        from_time = datetime.strptime(param_kwarg['from_time'], '%Y-%m-%d')
        day_of_week_num = from_time.isocalendar()[2]
        from_time = from_time - timedelta(days=day_of_week_num-1)
        from_time = from_time.strftime(DAY_TIME_FMT)
        param_kwarg.update({"from_time": from_time})
    report_info_list = ReportAPI.get_week_report_info(**param_kwarg)
    menu_tree_info = MenuTreeAPI.query_line_relation()

    for report_info in report_info_list:
        function_id = report_info.get('function_id')
        report_info.update(menu_tree_info[function_id])
    if param_kwarg.get('data_type', None):
        report_info_list = get_line_of_data(report_info_list, '%W')
        business_info_list = MenuTreeAPI.query_business_line()
        business_info_dict = {}
        for business_info in business_info_list:
            business_info_dict[business_info['id']] = business_info

        for report_info in report_info_list:
            business_line_id = report_info.get('business_line_id')
            report_info.update(business_info_dict[business_line_id])
        if report_info_list:
            chartist_data = report_data_manager(report_info_list, '%W')
        else:
            chartist_data = {}
        return jsonify({'success': True, 'res': chartist_data})
    return jsonify({'success': True, 'res': report_info_list})


@app.route('/report/month_report/add', methods=['GET'])
@localhost_required
@try_except
def add_month_report():
    """
    :return:
    """
    now_time_point = datetime.now()
    day_of_month_num = int(now_time_point.strftime('%m'))
    before_time_point = now_time_point - timedelta(days=(day_of_month_num - 1))
    to_time = (now_time_point + timedelta(days=1)).strftime(DAY_TIME_FMT)
    from_time = before_time_point.strftime(DAY_TIME_FMT)

    use_case_data_list = ReportAPI.get_day_report_info(from_time=from_time, to_time=to_time)
    report_info_list = ReportAPI.get_month_report_info(from_time=from_time, to_time=to_time)
    report_info_dict = {}
    for report_info in report_info_list:
        report_info_dict[report_info['function_id']] = report_info
    use_case_report_list = get_function_of_data(use_case_data_list)
    for report_data in use_case_report_list:
        function_id = report_data['function_id']
        if report_info_dict and report_info_dict.get(function_id, None):
            id = report_info_dict[function_id].get('id')
            report_data['id'] = id
            ReportAPI.modify_month_report(**report_data)
        else:
            ReportAPI.add_month_report(**report_data)
    return jsonify({'success': True})


@app.route('/report/month_report/info', methods=['POST'])
@login_required
@try_except
def query_month_report_info():
    """
    查询月报表数据，默认查询前1月数据
    :param: 时间格式：%Y-%m-%d
    :return:
    """
    param_kwarg = request.get_json()
    now_time_point = datetime.utcnow()
    to_time_point = datetime.utcnow() + timedelta(days=1)
    from_time_point = now_time_point - relativedelta(months=1)
    if not param_kwarg.get('to_time', None):
        param_kwarg['to_time'] = to_time_point.strftime(DAY_TIME_FMT)
    else:
        to_time = param_kwarg['to_time']
        to_time = datetime.strptime(to_time, '%Y-%m-%d') + timedelta(days=1)
        to_time = to_time.strftime(MONTH_TIME_FMT)
        param_kwarg.update({"to_time": to_time})

    if not param_kwarg.get('from_time', None):
        param_kwarg['from_time'] = from_time_point.strftime(DAY_TIME_FMT)
    else:
        from_time = param_kwarg['from_time']
        from_time = datetime.strptime(from_time, '%Y-%m-%d')
        from_time = from_time.strftime(MONTH_TIME_FMT)
        param_kwarg.update({"from_time": from_time})

    report_info_list = ReportAPI.get_month_report_info(**param_kwarg)
    menu_tree_info = MenuTreeAPI.query_line_relation()
    for report_info in report_info_list:
        function_id = report_info.get('function_id')
        report_info.update(menu_tree_info[function_id])
    if param_kwarg.get('data_type', None):
        report_info_list = get_line_of_data(report_info_list)
        business_info_list = MenuTreeAPI.query_business_line()
        business_info_dict = {}
        for business_info in business_info_list:
            business_info_dict[business_info['id']] = business_info

        for report_info in report_info_list:
            business_line_id = report_info.get('business_line_id')
            report_info.update(business_info_dict[business_line_id])
        if report_info_list:
            chartist_data = report_data_manager(report_info_list, '%Y/%m')
        else:
            chartist_data = {}
        return jsonify({'success': True, 'res': chartist_data})
    return jsonify({'success': True, 'res': report_info_list})




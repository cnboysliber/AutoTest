from flask import session
from application import app
from application.controller import login_required
from application.util.decorator import no_cache
from application.controller import cur_user
from application.util.exception import try_except


@app.route('/')
@login_required
@no_cache
def index():
    return app.send_static_file('index.html')


@app.route('/parameter/<page_num>')
@login_required
@no_cache
def parameter_page(page_num):
    return app.send_static_file('parameter.html')


@app.route('/parameter_detail/<parameter_id>')
@login_required
@no_cache
def parameter_detail_page(parameter_id):
    return app.send_static_file('parameter_detail.html')


@app.route('/interface/<page_num>')
@login_required
@no_cache
def interface_page(page_num):
    return app.send_static_file('interface.html')


@app.route('/interface_detail/<interface_id>')
@login_required
@no_cache
def interface_detail_page(interface_id):
    return app.send_static_file('interface_detail.html')


@app.route('/use_case/<page_num>')
@login_required
@no_cache
def use_case_page(page_num):
    return app.send_static_file('use_case_detail.html')


@app.route('/use_case_detail/<use_case_id>')
@login_required
@no_cache
def use_case_detail_page(use_case_id):
    return app.send_static_file('use_case_detail.html')


@app.route('/batch/<page_num>')
@login_required
@no_cache
def batch_page(page_num):
    return app.send_static_file('batch.html')


@app.route('/batch_detail/<batch_id>')
@login_required
@no_cache
def batch_detail_page(batch_id):
    return app.send_static_file('batch_detail.html')


@app.route('/use_case_run_log/<page_num>')
@login_required
@no_cache
def use_case_run_log_page(page_num):
    return app.send_static_file('use_case_run_log.html')


@app.route('/batch_run_log/<page_num>')
@login_required
@no_cache
def batch_run_log_page(page_num):
    return app.send_static_file('batch_run_log.html')


@app.route('/use_case_run_log/detail/<run_log_id>')
@login_required
@no_cache
def use_case_run_log_detail(run_log_id):
    return app.send_static_file('use_case_run_log_detail.html')


@app.route('/batch_run_log/detail/<run_log_id>/<page_num>')
@login_required
@no_cache
def batch_run_log_detail(run_log_id, page_num):
    return app.send_static_file('batch_run_log_detail.html')


@app.route('/environment/manage')
@login_required
@no_cache
def environment_mange():
    return app.send_static_file('environment.html')


@app.route('/environment/detail')
@login_required
@no_cache
def environment_detail():
    return app.send_static_file('environment_detail.html')


@app.route('/use_case/report')
@login_required
@no_cache
def use_case_report():
    return app.send_static_file('report.html')


@app.route('/email/manage')
@login_required
@no_cache
def email_manage():
    return app.send_static_file('email_manage.html')


@app.route('/logout')
@try_except
def logout():
    if cur_user():
        del session['user_id']
        del session['real_name']
        del session['timestamp']
    return app.send_static_file('logout.html')


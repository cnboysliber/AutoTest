# -*- coding:utf-8 -*-
import time
import requests


def email_send(**kwargs):
    """
    发送邮件
    发件人：attc@huishoubao.com.cn 密码：Att123456
    :param kwargs:    所需参数，包括收件人/邮件标题/邮件内容
    :return:          成功True， 失败False
    """
    json_data = {
        'head': {
            'version': '0.01',
            'msgtype': 'request',
            'interface': 'account7',
            'remark': ''
        },
        'params': {
            'system': 'HSB',
            'time': int(time.time()),
            'address': kwargs['address'],
            'subject': kwargs['title'],
            'body': kwargs['body']
        }
    }
    str_url = kwargs.get('str_url')
    proxies = kwargs.get('proxies', {'http': '119.29.141.207', 'https': '119.29.141.207'})
    try:
        r = requests.post(str_url, json=json_data, proxies=proxies)
        print(r.text)
    except Exception as e:
        print(e)
        return
    if r.status_code == 200:
        return 0
    else:
        return r.text


if __name__ == '__main__':
    kwargs = dict()
    kwargs['str_url'] = 'http://push.huanjixia.com/email-interface'
    kwargs['address'] = {'lichengbo': 'lichengbo@huishoubao.com.cn', 'hello': 'lichengbo@huishoubao.com.cn'}
    kwargs['title'] = '自动化巡检报表'
    kwargs['body'] = '测试'
    kwargs['proxies'] = {
        'http': '119.29.141.207'
    }
    email_send(**kwargs)






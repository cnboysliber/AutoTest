import hashlib
import time
import json
import requests


def key_value_sort_join(**kwargs):
    """
    根据传入的key value pair按ASCII升序排序并用&链接
    :param kwargs:      key value pair
    :return:            排序并链接过后的字符串
    """
    kwargs = {k: v for k, v in kwargs.items() if v and type(v) == str}
    keys = sorted(kwargs.keys())
    return '&'.join(['%s=%s' % (key, kwargs[key]) for key in keys])


def add_key(string_to_sign, key):
    """
    将key用&key=加入到给定字符串的最后
    :param string_to_sign:  给定字符串
    :param key:             key
    :return:                添加了key的字符串
    """
    return '{0}&key={1}'.format(string_to_sign, key)


def calc_md5(string_to_hash):
    """
    计算传入内容的md5
    :param string_to_hash:  传入内容
    :return:                传入内容的md5
    """
    return hashlib.md5(string_to_hash.encode('utf-8')).hexdigest()


def huan_ji_xia_encryption(json_payload):
    """
    换机侠的加密方式
    :param json_payload:    需要加密的json
    :return:                添加了签名的json
    """
    sec_key = 'm2cjgx46md5973n4ymeoxa4v195iwwmb'
    to_sign = {}
    for element in json_payload:
        to_sign.update(json_payload[element])
    to_sign = key_value_sort_join(**to_sign)
    to_sign = '{0}&key={1}'.format(to_sign, sec_key)
    sign = calc_md5(to_sign)
    if 'params' in json_payload:
        json_payload['params']['sign'] = sign
    elif '_param' in json_payload:
        json_payload['_param']['sign'] = sign
    return json_payload


def xian_yu_platform_encryption(url, json_payload):
    """
    闲鱼平台加密 图书加密，手机类加密方式不一样
    :param url: 请求url
           json_payload: 请求的json
    :return:
    """
    sec_key = 'fdcd2bdc3846fc6d5bb4967174758c38'
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    json_payload_str = json.dumps(json_payload, ensure_ascii=False)
    str_data = ''.join([sec_key, 'app_key24633185methodqimen.alibaba.idle.recycle.quote.gettimestamp', timestamp,
                        json_payload_str, sec_key])
    data_s = calc_md5(str_data)
    url += '?timestamp={}&sign={}&app_key=24633185&method=qimen.alibaba.idle.recycle.quote.get'.format(timestamp,
                                                                                                       data_s)
    return url


def boss_login_encryption(json_payload):
    """
    boss系统登陆账号加密
    :param json_payload:
    :return:
    """
    passwd = json_payload['psw']
    hash = 5381
    for i in range(0, len(passwd)):
        hash += (hash << 5) + ord(passwd[i])
    passwd = hash & 0x7fffffff
    json_payload.update({'psw': passwd})
    return json_payload


def hsb_public_service_encryption(json_payload, headers):
    """
    回收宝基础服务加密
    :param json_payload:
    :param headers:
    :return:
    """
    server_id = headers['HSB-OPENAPI-CALLERSERVICEID']
    secret_key = get_crypto_Key(server_id)
    str_json = str(json.dumps(json_payload))
    src = '_'.join([str_json, secret_key])
    headers['HSB-OPENAPI-SIGNATURE'] = calc_md5(src)
    return headers


def get_crypto_Key(ServerId):
    """
    回收宝基础服务加密key集合
    :param ServerId:
    :return:
    """
    key_dict = {
        '212006': 'dk26kmdasnph0voz69fj0jpv7t3ixev8',
        '212007': '34a4bda272f7facbda86d7e789c774ee',
        '216009': '7edcd52b48e6f709539cff9c726ca96e',
        '212013': '665CA5E5BB3CBDF76ADA25240F05AE54',
        '112006': 'gYt8YHmZVUtq9BxHzmNBQ0Eo7oGi8IKU',
        '260000': 'dk26kmdasnph0voz69fj0jpv7t3ixev8',
        '210007': '0liqvtHrIWLsqKqyDUK2jUt4AzdG4uo6'
    }
    return key_dict.get(ServerId)


def cola_you_pin_mall_encryption(json_payload, headers):
    """
    可乐优品加密方式
    :param json_payload:
    :param headers:
    :return:
    """
    if not headers:
        headers = dict()
    app_id = 'ColaYouPinMall'
    app_key = 'f423e9f274c392182236284a2bdd166b'
    src_str = ''.join([app_id, str(json.dumps(json_payload)), app_key])
    headers['sign'] = calc_md5(src_str)
    return headers


def xian_yu_app_encryption(url, json_payload):
    """
    闲鱼app签名加密, 请求url需要传method参数
    :param url:
    :param json_payload:
    :return:
    """
    app_key = 'fdcd2bdc3846fc6d5bb4967174758c38'
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    query_sting = 'app_key=24633185&' \
                  'timestamp={}'.format(timestamp)
    uri_param = url.split('?', 1)
    if len(uri_param) > 1:
        uri_str = '&'.join([query_sting, uri_param[-1]])
    else:
        uri_str = query_sting
    k_v_param = dict()
    for p in uri_str.split('&'):
        k, v = p.split('=')
        k_v_param[k] = v
    uri = key_value_sort_join(**k_v_param)
    keys = sorted(k_v_param.keys())
    kv_sort = ''.join(['%s%s' % (key, k_v_param[key]) for key in keys])
    json_payload = json.dumps(json_payload).replace(' ', '')
    encrypt_src = ''.join([app_key, kv_sort, json_payload, app_key])
    sign = calc_md5(encrypt_src).upper()

    return '?'.join([uri_param[0], '&sign='.join([uri, sign])]), json_payload


def xian_yu_rc4_encryption(json_payload):
    """
    闲鱼平台rc4加密
    :param json_payload:
    :return:
    """
    url = ' http://dev8123.huishoubao.com/getrc4'
    res = requests.post(url, data=json.dumps(json_payload))
    return res.content.decode()


def hsb_cooperation_channel_encryption(json_payload):
    """
    回收宝合作渠道加密
    :param json_payload:
    :return:
    """
    json_payload = json.loads(json_payload.strip('data='))
    key = 'HSB-sdfaaa_sdJHUGsdiJl'
    kwargs = {k: v for k, v in json_payload.items() if v.strip() and k != 'sign'}
    keys = sorted(kwargs.keys())
    sign_str = '&'.join(['%s=%s' % (key, kwargs[key]) for key in keys]) + '&key={}'.format(key)
    encry_times = sum([ord(str(ch)) for ch in sign_str]) % 3 + 3
    for _ in range(encry_times):
        sign_str = calc_md5(sign_str).upper()
    json_payload['sign'] = sign_str
    return 'data=' + json.dumps(json_payload)


if __name__ == '__main__':
    # url = 'http://openapi.huishoubao.com/xianyu_platform/eva_template?' \
    #       'source_appkey=24696122&target_appkey=24633185'
    # json_payload = {"channel": "p11", "spuid": 3361224, "userId": "2624823547"}
    # print(xian_yu_app_encryption(url, json_payload))
    data = {"key": "value"}
    print(xian_yu_rc4_encryption(data))

#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
from lazysdk import lazyrequests
from lazysdk import lazytime
from lazysdk import lazymd5
from urllib import parse
import requests
import showlog
import copy
import json


def make_sign(
        post_data: dict,
        cl_secret: str,
        email: str = None,
        timestamp: int = None
):
    """
    对数据签名，返回headers
    :param post_data:
    :param cl_secret:
    :param email:
    :param timestamp:
    :return:
    """
    if not timestamp:
        timestamp = lazytime.get_timestamp()
    temp_data = copy.deepcopy(post_data)
    temp_data['timestamp'] = timestamp
    data_keys = list(temp_data.keys())
    data_keys.sort()
    data_str = ''
    for each_key in data_keys:
        data_str += f'{each_key}={parse.quote(str(temp_data[each_key]))}&'
    data_str += f"cl_secret={cl_secret}"
    sign = lazymd5.md5_str(content=data_str).upper()  # MD5后转大写
    headers = {
        'timestamp': timestamp,
        'signature': sign,
        'email': email,
    }
    return headers


def login_inner(
        email: str,
        password: str,
        product_version: int = 0,
        cookie: str = None
):
    """
    第二层登录，进入子系统
    :param email:
    :param password:
    :param product_version:
    :param cookie:
    :return:
    """
    url = 'https://cli2.mobgi.com/User/AdminUser/login'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=utf-8",
        "Cookie": cookie,
        "Host": "cli2.mobgi.com",
        "Origin": "https://cl.mobgi.com",
        "Referer": "https://cl.mobgi.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0",
    }
    data = {
        'email': email,
        'password': lazymd5.md5_str(password),
        'product_version': product_version
    }
    return lazyrequests.lazy_requests(
        method='POST',
        url=url,
        json=data,
        headers=headers
    )


def login(
        email: str,
        password: str
):
    """
    登录并获取登录状态（有2层）
    :param email:
    :param password:
    :return:
    """
    url = 'https://cli2.mobgi.com/User/AdminUser/loginInfo'
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=utf-8",
        "Host": "cli2.mobgi.com",
        "Origin": "https://cl.mobgi.com",
        "Referer": "https://cl.mobgi.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0",
    }
    data = {
        'email': email,
        'password': lazymd5.md5_str(password)
    }
    response = lazyrequests.lazy_requests(
        method='POST',
        url=url,
        json=data,
        headers=headers,
        return_json=False
    )
    response_json = response.json()
    if response_json['code'] == 0:
        cookie_dict = requests.utils.dict_from_cookiejar(response.cookies)
        cookie_str = ''
        for cookie_key, cookie_value in cookie_dict.items():
            cookie_str += f'{cookie_key}={cookie_value}; '
        login_inner_response = login_inner(
            email=email,
            password=password,
            cookie=cookie_str
        )
        if login_inner_response.json()['code'] == 0:
            cookie_dict2 = requests.utils.dict_from_cookiejar(login_inner_response.cookies)
            cookie_str2 = ''
            for cookie_key, cookie_value in cookie_dict2.items():
                cookie_str2 += f'{cookie_key}={cookie_value}; '
            res = {
                'cookie': cookie_str2[:-2],
                'email': email
            }
            return res
    else:
        showlog.warning(f'登录失败：{response.json()}')
        return


def get_material_creative_users_options(
        cookie
):
    """
    获取素材报表页面设计师列表
    :param cookie:
    :return:
    """
    url = 'https://cli2.mobgi.com/Material/Manage/getMaterialCretiveUsersOptions'
    params = {
        'is_lock': ''
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "cli2.mobgi.com",
        "Origin": "https://cl.mobgi.com",
        "Referer": "https://cl.mobgi.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0",
    }
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        headers=headers
    )


def get_material_report_sum(
        cookie: str,
        start_date: str = None,
        end_date: str = None,
        make_user_list: list = None,
        material_type: str = ''
):
    """
    获取素材报表 的合计数据
    :param cookie:
    :param start_date: 数据开始日期，默认前1日
    :param end_date: 数据结束日期，默认前1日
    :param make_user_list: 设计师id列表
    :param material_type: 素材类型
    :return:
    """
    if not start_date:
        start_date = lazytime.get_date_string(days=-1)
    if not end_date:
        end_date = lazytime.get_date_string(days=-1)
    if not make_user_list:
        make_user = ""
    else:
        make_user = ','.join(make_user_list)
    url = 'https://cli2.mobgi.com/Report/MaterialReport/getSum'
    conditions = {
        "keyword": "",
        "material_special": "",
        "material_group": "",
        "make_user": make_user,
        "media_account": "",
        "product": "",
        "material_type": material_type,
        "label_ids": "",
        "app": "",
        "creative_user": "",
        "shoot_user_id": "",
        "performer_user_id": "",
        "dub_user_id": "",
        "screencap_user_id": "",
        "time_line": "REQUEST_TIME"
    }
    data = {
        "time_dim": "sum",
        "media_type": "",
        "data_dim": "material",
        "conditions": json.dumps(conditions),
        "sort_field": "cost",
        "sort_direction": "desc",
        "page": 1,
        "page_size": 20,
        "kpis": [
            "cost",
            "show_count",
            "cpm",
            "click",
            "ctr",
            "cpc",
            "active",
            "active_cost",
            "active_rate",
            "conversion_num"
        ],
        "start_date": start_date,
        "end_date": end_date,
        "relate_dims": [
            "media_account",
            "material_create_time",
            "make_user",
            "label_ids"
        ]
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=utf-8",
        "Cookie": cookie,
        "Host": "cli2.mobgi.com",
        "Origin": "https://cl.mobgi.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0",
    }
    return lazyrequests.lazy_requests(
        method='POST',
        url=url,
        json=data,
        headers=headers
    )


def get_sub_user_list(
        cookie: str,
        page: int = 1,
        page_size: int = 10,
        keyword: str = None,
        is_lock: str = None,
        parent_id: str = None,
        main_user_id: str = None,
        total_count: int = None
):
    """
    获取用户列表
    :param cookie:
    :param page:
    :param page_size:
    :param keyword:
    :param is_lock:
    :param parent_id:
    :param main_user_id:
    :param total_count:

    :return:
    """
    url = 'https://cli2.mobgi.com/User/AdminUser/getSubUserList'
    params = {
        'is_under': 1,
        'page': page,
        'page_size': page_size
    }
    if keyword:
        params['keyword'] = keyword
    if is_lock:
        params['is_lock'] = is_lock
    if parent_id:
        params['parent_id'] = parent_id
    if main_user_id:
        params['main_user_id'] = main_user_id
    if total_count:
        params['total_count'] = total_count

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "cli2.mobgi.com",
        "Origin": "https://cl.mobgi.com",
        "Referer": "https://cl.mobgi.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0"
    }
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=params,
        headers=headers
    )


def get_material_manage_list(
        cookie: str,
        page: int = 1,
        page_size: int = 20,
        keyword: str = "",
        total_count: int = None,
        start_date: str = None,
        end_date: str = None
):
    """
    获取 本地素材-素材管理
    :param cookie:
    :param page:
    :param page_size:
    :param keyword:
    :param total_count:
    :param start_date:
    :param end_date:

    :return:
    """
    if not start_date:
        start_date = lazytime.get_date_string(days=0)
    if not end_date:
        end_date = lazytime.get_date_string(days=0)
    url = 'https://cli2.mobgi.com/Material/Manage/lists'
    data = {
        "audit_status": "",
        "keyword": keyword,
        "special_id": "",
        "group_id": "",
        "source": "",
        "material_type": "",
        "file_direction": "",
        "creative_user": "",
        "make_user": "",
        "toutiao_reject": "",
        "qianchuan_reject": "",
        "gdt_reject": "",
        "kuaishou_reject": "",
        "manage_status": "",
        "shoot_user_id": [],
        "performer_user_id": [],
        "dub_user_id": [],
        "screencap_user_id": [],
        "label_ids": [],
        "ad_rel": {},
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "start_date": start_date,
        "end_date": end_date
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "cli2.mobgi.com",
        "Origin": "https://cl.mobgi.com",
        "Referer": "https://cl.mobgi.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0"
    }
    return lazyrequests.lazy_requests(
        method='POST',
        url=url,
        json=data,
        headers=headers
    )


def material_edit(
        cookie: str,
        material_id: int,
        material_name: str
):
    """
    修改素材信息，这里是改名
    :param cookie:
    :param material_id: 素材id
    :param material_name: 修改后的素材名称

    :return:
    """
    url = 'https://cli2.mobgi.com/Material/Manage/edit'
    data = {
        "material_id": material_id,
        "material_name": material_name,
        "type": 1
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=utf-8",
        "Cookie": cookie,
        "Host": "cli2.mobgi.com",
        "Origin": "https://cl.mobgi.com",
        "Pragma": "no-cache",
        "Referer": "https://cl.mobgi.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0",
    }
    return lazyrequests.lazy_requests(
        method='POST',
        url=url,
        json=data,
        headers=headers
    )


def material_detail(
        cookie: str,
        material_id: int
):
    """
    获取素材信息
    :param cookie:
    :param material_id: 素材id
    :param material_name: 修改后的素材名称

    :return:
    """
    url = 'https://cli2.mobgi.com/Material/Manage/detail'
    data = {
        "material_id": material_id
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "cli2.mobgi.com",
        "Origin": "https://cl.mobgi.com",
        "Referer": "https://cl.mobgi.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0"
    }
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=data,
        headers=headers
    )


def material_group_child_list(
        cookie: str,
        special_id: int = 0,
        group_id: int = None
):
    """
    获取专辑目录
    :param cookie:
    :param special_id: 专辑id
    :param group_id:

    :return:
    """
    url = 'https://cli2.mobgi.com/Material/Group/childList'
    data = {
        "special_id": special_id
    }
    if group_id:
        data['group_id'] = group_id

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Host": "cli2.mobgi.com",
        "Origin": "https://cl.mobgi.com",
        "Pragma": "no-cache",
        "Referer": "https://cl.mobgi.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0"
    }
    return lazyrequests.lazy_requests(
        method='GET',
        url=url,
        params=data,
        headers=headers
    )


def material_move(
        cookie: str,
        material_ids: list,
        special_id: int = 0,
        group_id: int = None
):
    """
    移动素材
    :param cookie:
    :param material_ids:
    :param special_id: 目标专辑id
    :param group_id: 目标文件夹id

    :return:
    """
    url = 'https://cli2.mobgi.com/Material/Manage/batchMove'
    data = {
        "special_id": str(special_id),
        "group_id": str(group_id),
        "material_ids": material_ids
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=utf-8",
        "Cookie": cookie,
        "Host": "cli2.mobgi.com",
        "Origin": "https://cl.mobgi.com",
        "Pragma": "no-cache",
        "Referer": "https://cl.mobgi.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0"
    }
    return lazyrequests.lazy_requests(
        method='POST',
        url=url,
        json=data,
        headers=headers
    )

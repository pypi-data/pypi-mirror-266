#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import ipaddress
import os
import random
from datetime import datetime
import sys
import requests
from tqdm import tqdm


def is_ip_address(ip_str: str):
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip is not None
    except ValueError:
        return False


def is_ip_network(net_str: str):
    try:
        net = ipaddress.ip_network(net_str, strict=False)
        return net is not None
    except ValueError:
        return False


def get_ip_version(ip_str: str):
    ip = ipaddress.ip_address(ip_str)
    return ip.version


def gen_ip_form_network(ip_str):
    from ipcheck.app.ip_info import IpInfo
    net = ipaddress.ip_network(ip_str, strict=False)
    hosts = list(net.hosts())
    all_ips = [IpInfo(str(ip)) for ip in hosts]
    return all_ips

def is_valid_port(port_str):
    try:
        port = int(port_str)
        return 0 < port <= 65535
    except ValueError:
        return False

def parse_ip_info_from_str(expr_str : str):
    from ipcheck.app.ip_info import IpInfo
    try:
        index = expr_str.rindex(':')
        ip_str = expr_str[:index]
        port_str = expr_str[index + 1:]
        if not is_valid_port(port_str):
            return None
        if ip_str.startswith('[') and ip_str.endswith(']'):
            ip_str = ip_str[1: -1]
            if is_ip_address(ip_str) and get_ip_version(ip_str) == 6:
                return IpInfo(ip_str, int(port_str))
        else:
            if is_ip_address(ip_str) and get_ip_version(ip_str) == 4:
                return IpInfo(ip_str, int(port_str))
    except:
        pass
    return None


def find_txt_in_dir(dir):
    L = []
    if os.path.isdir(dir):
        for f in os.listdir(dir):
            file = os.path.join(dir, f)
            if os.path.isfile(file) and file.endswith('.txt'):
                L.append(file)
    return L


# 通过指定目标list 大小，从src_list 生成新的list
def adjust_list_by_size(src_list: list, target_size):
    if (target_size > len(src_list)):
        return src_list
    return random.sample(src_list, target_size)


def gen_time_desc():
    current_time = datetime.now()
    # 格式化时间为字符串，精确到秒
    return '{}: {}'.format('生成时间为', current_time.strftime("%Y-%m-%d %H:%M:%S"))

def show_freshable_content(content: str):
    print(content, end='\r')
    sys.stdout.flush()

def write_file(content: str, path: str):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def download_file(url, path, proxy):
    # 发起请求并获取响应对象
    print('下载代理为: {}'.format(proxy))
    proxies = {}
    if proxy:
        proxies = {
            'http': proxy,
            'https': proxy
        }
    try:
        response = requests.get(url, stream=True, timeout=15, proxies=proxies)
        total_size = int(response.headers.get('content-length', 0))  # 获取文件总大小

        # 使用 tqdm 来显示进度条
        with open(path, 'wb') as file, tqdm(
            desc=path,
            total=total_size,
            unit='K',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                # 写入文件并更新进度条
                file.write(data)
                bar.update(len(data))
            return True
    except Exception:
        return False
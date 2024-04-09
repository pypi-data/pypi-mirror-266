#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import List
from ipcheck.app.utils import is_ip_address, is_ip_network, gen_ip_form_network, find_txt_in_dir, parse_ip_info_from_str
from ipcheck.app.ip_info import IpInfo


def gen_ip_list_by_arg(source, port=443) -> List[IpInfo]:
    ip_list = []
    if os.path.exists(source):
        ip_list = read_all_ips_form_path(source, port)
    elif is_ip_network(source):
        ip_list = gen_ip_form_network(source)
    elif is_ip_address(source):
        ip_list.append(IpInfo(source, port))
    else:
        ip_info = parse_ip_info_from_str(source)
        if ip_info:
            ip_list.append(ip_info)
    # fixed_ips = [f'[{item}]' if get_ip_version(item) == 6 else item for item in ip_list]
    return ip_list

def read_all_ips_form_path(path, port=443):
    all_ip_files = []
    all_ips = []
    if os.path.isdir(os.path.abspath(path)):
        all_ip_files = find_txt_in_dir(path)
    else:
        all_ip_files.append(path)
    for file in all_ip_files:
        all_ips += read_all_ips_form_file(file, port)
    all_ips = list(dict.fromkeys(all_ips))
    return all_ips


def read_all_ips_form_file(file, port=443) -> List[IpInfo]:
    all_ips = []
    ip_networks = []
    with open(file, 'r') as f:
        for line in f.readlines():
            if is_ip_address(line.strip()):
                all_ips.append(IpInfo(line.strip(), port))
            elif is_ip_network(line.strip()):
                ip_networks.append(line.strip())
            else:
                ip_info = parse_ip_info_from_str(line.strip())
                if ip_info:
                    all_ips.append(ip_info)
    ip_networks = list(dict.fromkeys(ip_networks))
    for ip_network in ip_networks:
        all_ips += gen_ip_form_network(ip_network)
    all_ips = list(dict.fromkeys(all_ips))
    return all_ips


def filter_ip_list_by_white_list(ip_list, white_list):
    fixed_list = []
    for pref_str in white_list:
        fixed_list += [ip_info for ip_info in ip_list if ip_info.ip.startswith(pref_str)]
    return fixed_list

def filter_ip_list_by_block_list(ip_list, block_list):
    fixed_list = []
    for block_str in block_list:
        fixed_list = [ip_info for ip_info in ip_list if not ip_info.ip.startswith(block_str)]
    return fixed_list
#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import List
from ipcheck.app.ip_info import IpInfo
from ipcheck.app.ipparser.ip_dir_parser import IpDirParser
from ipcheck.app.ipparser.ip_file_parser import IpFileParser
from ipcheck.app.ipparser.ip_cidr_parser import IpCidrParser
from ipcheck.app.ipparser.ip_parser import IpParser
from ipcheck.app.ipparser.ip_port_parser import IpPortParser


def gen_ip_list_by_arg(source, port=443) -> List[IpInfo]:
    ip_list = []
    parsers = [IpDirParser(source, port), IpFileParser(source, port), IpCidrParser(source, port), IpParser(source, port), IpPortParser(source, port)]
    for parser in parsers:
        if parser.is_valid:
            ips = parser.parse()
            ip_list.extend(ips)
            break
    return ip_list

def filter_ip_list_by_white_list(ip_list, white_list):
    fixed_list = []
    for pref_str in white_list:
        fixed_list = [ip_info for ip_info in ip_list if ip_info.ip.startswith(pref_str)]
    return fixed_list

def filter_ip_list_by_block_list(ip_list, block_list):
    fixed_list = []
    for block_str in block_list:
        fixed_list = [ip_info for ip_info in ip_list if not ip_info.ip.startswith(block_str)]
    return fixed_list
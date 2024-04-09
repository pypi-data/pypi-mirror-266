#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
from ipcheck.app.ip_info import IpInfo
from ipcheck.app.ipparser.base_parser import BaseParser
from ipcheck.app.utils import is_ip_network
import ipaddress

class IpCidrParser(BaseParser):
    '''
    解析ip cidr 格式
    '''

    @property
    def is_valid(self) -> bool:
        return is_ip_network(self.source)

    def parse(self) -> List[IpInfo]:
        if not self.is_valid:
            return []
        net = ipaddress.ip_network(self.source, strict=False)
        hosts = list(net.hosts())
        all_ips = [IpInfo(str(ip), self.port) for ip in hosts]
        return all_ips
        
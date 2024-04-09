#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
from ipcheck.app.ip_info import IpInfo
from ipcheck.app.ipparser.base_parser import BaseParser
from ipcheck.app.utils import is_valid_port, is_ip_address

class IpPortParser(BaseParser):
    '''
    解析ip:port 格式
    '''

    def __init__(self, source: str, port: int) -> None:
        self.ip = None
        super().__init__(source, port)

    @property
    def is_valid(self) -> bool:
        try:
            index = self.source.rindex(':')
            ip_str = self.source[:index]
            if ip_str.startswith('[') and ip_str.endswith(']'):
                ip_str = ip_str[1: -1]
            port_str = self.source[index + 1:]
            if is_ip_address(ip_str) and is_valid_port(port_str):
                self.ip = ip_str
                self.port = int(port_str)
                return True
        except:
            pass
        return False


    def parse(self) -> List[IpInfo]:
        if not self.is_valid:
            return []
        return [IpInfo(self.ip, self.port)]
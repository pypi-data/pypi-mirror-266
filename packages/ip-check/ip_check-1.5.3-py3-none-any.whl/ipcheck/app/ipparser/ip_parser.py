#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
from ipcheck.app.ip_info import IpInfo
from ipcheck.app.ipparser.base_parser import BaseParser
from ipcheck.app.utils import is_ip_address

class IpParser(BaseParser):
    '''
    解析ip 格式
    '''

    @property
    def is_valid(self) -> bool:
        return is_ip_address(self.source)

    def parse(self) -> List[IpInfo]:
        if not self.is_valid:
            return []
        return [IpInfo(self.source, self.port)]
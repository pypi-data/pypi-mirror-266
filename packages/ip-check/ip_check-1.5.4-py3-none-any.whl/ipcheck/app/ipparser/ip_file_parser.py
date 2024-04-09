#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
from ipcheck.app.ip_info import IpInfo
from ipcheck.app.ipparser.base_parser import BaseParser
from os import path
from ipcheck.app.ipparser.ip_cidr_parser import IpCidrParser
from ipcheck.app.ipparser.ip_parser import IpParser
from ipcheck.app.ipparser.ip_port_parser import IpPortParser

class IpFileParser(BaseParser):
    '''
    从文本中解析ip
    '''

    @property
    def is_valid(self) -> bool:
        return path.exists(self.source) and path.isfile(self.source)

    def parse(self) -> List[IpInfo]:
        if not self.is_valid:
            return []
        ip_list = []
        with open(self.source, 'r') as f:
            sources = [line.strip() for line in f.readlines()]
            for source in sources:
                parsers = [IpCidrParser(source, self.port), IpParser(source, self.port), IpPortParser(source, self.port)]
                for parser in parsers:
                    if parser.is_valid:
                        ip_list.extend(parser.parse())
                        break
        return ip_list
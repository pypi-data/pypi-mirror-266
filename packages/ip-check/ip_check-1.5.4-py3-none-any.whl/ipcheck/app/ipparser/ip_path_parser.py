#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
from ipcheck.app.ip_info import IpInfo
from ipcheck.app.ipparser.base_parser import BaseParser
from os import path
from ipcheck.app.ipparser.ip_file_parser import IpFileParser
from ipcheck.app.utils import find_txt_in_dir

class IpPathParser(BaseParser):
    '''
    从文本中解析ip
    '''

    @property
    def is_valid(self) -> bool:
        return path.exists(self.source) and path.isdir(self.source)

    def parse(self) -> List[IpInfo]:
        ip_list = []
        sources = find_txt_in_dir(self.source)
        for source in sources:
            parser = IpFileParser(source, self.port)
            ip_list.extend(parser.parse())
        return ip_list
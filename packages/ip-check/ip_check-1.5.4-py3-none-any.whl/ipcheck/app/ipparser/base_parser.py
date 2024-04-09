#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
from ipcheck.app.ip_info import IpInfo

class BaseParser:

    def __init__(self, source: str, port: int) -> None:
        self.source = source
        self.port = port

    @property
    def is_valid(self) -> bool:
        return False

    def parse(self) -> List[IpInfo]:
        return []
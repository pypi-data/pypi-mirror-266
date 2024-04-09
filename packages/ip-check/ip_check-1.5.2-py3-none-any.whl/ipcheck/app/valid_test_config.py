#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ipcheck.app.base_config import BaseConfig

CONFIG_PREFIX = 'vt_'

class ValidTestConfig(BaseConfig):

    def get_config_prefix(self) -> str:
        return CONFIG_PREFIX

    def gen_cf_extra_part(self, config):
        self.ip_port = config.ip_port
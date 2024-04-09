#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
from ipcheck.app.valid_test_config import ValidTestConfig
from ipcheck.app.utils import adjust_list_by_size, show_freshable_content
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3
from ipcheck.app.ip_info import IpInfo
urllib3.disable_warnings()

from ipcheck import USER_AGENTS
import random


class ValidTest:

    def __init__(self, ip_list: List[IpInfo], config: ValidTestConfig) -> None:
        self.ip_list = ip_list
        self.config = config

    def run(self) -> List[IpInfo]:
        if not self.config.enabled:
            print('跳过可用性测试')
            return [IpInfo(ip, self.config.ip_port) for ip in self.ip_list]
        print('准备测试可用性 ... ...')
        print('可用性域名为: {}'.format(self.config.host_name))
        print('是否使用user-agent: {}'.format(self.config.user_agent))
        if len(self.ip_list) > self.config.ip_limit_count:
            print('待测试ip 过多，当前最大限制数量为{} 个，压缩中... ...'.format(self.config.ip_limit_count))
            self.ip_list = adjust_list_by_size(self.ip_list, self.config.ip_limit_count)
        total_count = len(self.ip_list)
        print('正在测试ip可用性, 总数为{}'.format(total_count))
        passed_ips = []
        thread_pool_executor = ThreadPoolExecutor(
            max_workers=self.config.thread_num, thread_name_prefix="valid_")
        all_task = [thread_pool_executor.submit(
            self.__test, ip_info) for ip_info in self.ip_list]
        test_count = 0
        for future in as_completed(all_task):
            test_count += 1
            content = '  当前进度为: {}/{}'.format(test_count, total_count)
            show_freshable_content(content)
            ret = future.result()
            if ret:
                passed_ips.append(ret)
        thread_pool_executor.shutdown(wait=True)
        print('可用性结果为: 总数{}, {} pass'.format(len(self.ip_list), len(passed_ips)))
        return passed_ips

    def __test(self, ip_info) -> None:
        check_key = self.config.check_key
        ip, port = ip_info.ip, ip_info.port
        pool = urllib3.HTTPSConnectionPool(
                ip, assert_hostname=self.config.host_name,
                server_hostname=self.config.host_name,
                port=port, cert_reqs='CERT_NONE')
        res = None
        headers = {
            'Host': self.config.host_name,
        }
        if self.config.user_agent:
            headers.update({'User-Agent': random.choice(USER_AGENTS)})
        try:
            r: urllib3.response = pool.urlopen('GET', self.config.path,
                                               retries=urllib3.util.Retry(self.config.max_retry),
                                               headers=headers,
                                               assert_same_host=False,
                                               timeout=self.config.timeout,
                                               preload_content=False,
                                               redirect=True)
            if self.config.get_loc:
                req_dict = {}
                for line in r.readlines():
                    line = line.decode('utf-8')
                    kv = line.strip().split('=')
                    req_dict.update({kv[0]: kv[1]})
                if req_dict.get(check_key, None) == self.config.host_name:
                    loc = req_dict.get('loc', None)
                    colo = req_dict.get('colo', None)
                    res = IpInfo(ip, port, loc=loc, colo=colo)
            elif r.status == 200:
                res = IpInfo(ip, port)
            r.release_conn()
        except:
            pass
        return res

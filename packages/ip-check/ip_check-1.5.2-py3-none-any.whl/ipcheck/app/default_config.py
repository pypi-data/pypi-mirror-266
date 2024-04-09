#!/usr/bin/env python3
# -*- coding: utf-8 -*-

DEFAULT_CONFIG = '''# 通用配置
[common]
# 测试端口
ip_port = 443
# 是否存储结果到文件
no_save = False

# 可用性检查配置
[valid test]
# 是否测试可用性
enabled = True
# 限制参与valid 测试的ip 数量
ip_limit_count = 1500
# 可用性检测域名
host_name = cloudflare.com
# 使用user-agent
user_agent = False
# 可用性检测路径, 固定的，取决于cloudflare
path = /cdn-cgi/trace
# 可用性测试多线程数量
thread_num = 64
# 可用性测试时的网络请求重试次数
max_retry = 4
# 可用性测试的网络请求timeout, 单位 s
timeout = 3.5
# 可用性测试检测的key
check_key = h
# 是否检测地区信息
get_loc = True

# rtt 测试配置
[rtt test]
enabled = True
# 限制参与rtt 测试的ip 数量
ip_limit_count = 1000
# rtt tcpping 间隔
interval = 1
# rtt 测试多线程数量
thread_num = 8
# rtt 测试的网络请求timeout, 单位 s
timeout = 3
# rtt 测试网络请求重试次数
max_retry = 6
# rtt 测试的延时及格值，单位 ms
max_rtt = 300
# rtt 测试次数
test_count = 13
# 最大丢包率控制， 单位 百分比
max_loss = 100

# 下载速度测试配置
[speed test]
# 是否开启速度测试
enabled = True
# 限制参与速度测试的ip 数量
ip_limit_count = 1000
# 测试下载文件的域名
host_name = cloudflaremirrors.com
# 使用user-agent
user_agent = False
# 测试下载文件的路径
file_path = /archlinux/iso/latest/archlinux-x86_64.iso
# 测试下载文件的重试次数
max_retry = 10
# 下载测试网络请求timeout, 单位 s
timeout = 5
# 下载时长限制, 单位 s
download_time = 10
# 最小达标速度, 单位 kB/s
download_speed = 5000
# 是否执行快速测速开关
fast_check = False'''
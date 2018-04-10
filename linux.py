# -*- coding: utf-8 -*-

'''
linux下的一些基本命令

1.安装编译工具以及库文件
yum -y install make zlib zlib-devel gcc-c++ libtool  openssl openssl-devel

2.生成安装文件并制定目录
./configure --prefix=目录

3.添加白名单到防火墙
-A INPUT -p tcp -m state -- state NEW -m tcp --dport 80 -j ACCEPT
'''
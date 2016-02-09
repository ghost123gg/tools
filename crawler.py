#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''

'''

__author__ = 'Alex'

import requests
from bs4 import BeautifulSoup


# Crawler class
class Browser():
    def __init__(self, headers = {}, use_proxy = False, proxies = {}):
        self.__s = requests.Session()
        self.__use_proxy = use_proxy
        self.__proxies = proxies
        self.__headers = headers
        
    def enable_proxy(self):
        self.__use_proxy = True

    def disable_proxy(self):
        self.__use_proxy = False

    def add_proxy(self, proxy_type, proxy_ip):
        self.__proxies[proxy_type] = proxy_ip

    def delete_proxy(self, proxy_type):
        self.__proxies.pop(proxy_type)

    def get_page(self, url, timeout = 3):
        if self.__use_proxy:
            r = self.__s.get(url, headers = self.__headers, proxies = self.__proxies)
        else:
            r = self.__s.get(url, headers = self.__headers)
        return r.content


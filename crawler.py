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
        
    def enableProxy(self):
        self.__use_proxy = True

    def disableProxy(self):
        self.__use_proxy = False

    def addProxy(self, proxy_type, proxy_ip):
        self.__proxies[proxy_type] = proxy_ip

    def deleteProxy(self, proxy_type):
        self.__proxies.pop(proxy_type)

    def getPage(self, url, timeout = 3):
        if self.__use_proxy:
            r = self.__s.get(url, headers = self.__headers, proxies = self.__proxies)
        else:
            r = self.__s.get(url, headers = self.__headers)
        return r.content


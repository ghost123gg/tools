#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'Alex'

import requests
import re
import codecs
import urllib
import time
import random
from bs4 import BeautifulSoup
from url_extract import UrlExtract

http_header = {
        'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding' : 'gzip, deflate, sdch',
        'Accept-Language' : 'zh-CN,zh;q=0.8,en;q=0.6',
        'Connection' : 'keep-alive'
        }

extract = UrlExtract()
p_list = []

def init_list_from_file(filename):
    l = []
    f = open(filename)
    for line in f:
        line = line.strip()
        if line:
            l.append(line)
    f.close()
    return l

def sleep_function(lower, upper):
    print "Sleeping..."
    time.sleep(random.uniform(lower, upper))
    print "Finished...\n"

def get_https_proxy_list():
    global http_header

    print "--------------------\nGeting proxy..."
    proxy_list = []
    entry_url = "http://proxy.moo.jp"
    target_url = "http://proxy.moo.jp/zh/"

    crawler = requests.Session()
    html = crawler.get(entry_url, headers = http_header).content
    sleep_function(1, 3)

    for i in range(2)[1:]:
        payload = {'pr' : 'HTTPS', 'page' : str(i)}        
        r = crawler.get(target_url, headers = http_header, params = payload)
        html = r.text

        with codecs.open("proxy.html", "w", encoding = r.encoding) as f:
            f.write(html)

        soup = BeautifulSoup(html)
        tr_list = []
        odd_list = soup.find_all("tr", class_ = "Odd")
        even_list = soup.find_all("tr", class_ = "Even")

        for ele in odd_list:
            tr_list.append(ele)
        for ele in even_list:
            tr_list.append(ele)

        for ele in tr_list:
            if ele.find("ins", class_ = "adsbygoogle"):
                continue
            else:
                td_list = ele.find_all("td")
                country = td_list[4].text
                ipdecode = td_list[0].text
                ipdecode = td_list[0].text
                st = ipdecode.find("(")
                ed = ipdecode.find(")")
                proxy_ip = urllib.unquote(ipdecode[st+2 : ed-1]) + ":" + td_list[1].text
                proxy_list.append(proxy_ip)
    print "Find %d proxy\n--------------------" % len(proxy_list)
    return proxy_list

def crawl_google(crawler, keyword, num, start, proxies = {}):
    global http_header

    google_url = "https://www.google.co.jp/search"
    payload = {'q' : keyword, 'num' : num, 'start' : start}

    if proxies:
        r = crawler.get(google_url, params = payload, proxies = proxies, timeout = 10)
    else:
        r = crawler.get(google_url, params = payload, timeout = 10)
    html = r.text

    with codecs.open("google.html", "w", encoding = 'UTF-8') as f:
        f.write(html)

    return html

def contain_chinese(s):
    for ch in s:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

def extract_domain(fqdn):
    global extract
    extracted = extract.extract(fqdn)
    return str(extracted.getDomain()) + "." + str(extracted.getTld()) if extracted.valid() else ""

def extract_cite_list_from_html(soup):
    return soup.find_all('cite')

def extract_h3_list_from_html(soup):
    return soup.find_all('h3', class_ = 'r')

def has_cheme(url):
    return True if url.startswith("http://") or url.startswith("https://") else False

def extract_domain_list_from_cite_list(cite_list):
    domain_list = set()
    for cite in cite_list:
        url = cite.text
        if not contain_chinese(url):
            ed = len(url)
            if not has_cheme(url):
                for i in range(ed):
                    if url[i] == '/' or url[i] == '?':
                        ed = i
                        break
                link = url[:ed]
                domain = extract_domain(link)
                if domain:
                    print "Find domain : %s" % domain
                    domain_list.add(domain)
    return domain_list

def is_spider_pool_url(url):
    if contain_chinese(url):
        return False
    if url.count('/') > 1:
        return False
    if url.count('?') > 0:
        return False
    pos = url.find('/')
    if pos != -1:
        url = url[:pos]
    if url.count('.') >= 3:
        return True
    if url.count('.') <= 1:
        return False

    pos = url.find('.') 

    if url[:pos].isalpha() and len(url[:pos]) >= 5:
        return True

    has_digit = False
    has_ch = False
    for i in range(pos):
        if url[i].isalpha():
            has_ch = True
        if url[i].isdigit():
            has_digit = True

    if has_digit and has_ch:
        return True
    return False

def select_random_number_from_list(l):
    return random.randint(0, len(l) - 1)

def detect(keyword):
    global p_list

    num = -1
    html = ""
    p_list = get_https_proxy_list()
    num = select_random_number_from_list(p_list)
    crawler = requests.Session()

    print "====================\nDetect keyword:",
    print keyword
    while True:
        try:
            print "Select proxy : %s" % p_list[num]
            html = crawl_google(crawler, keyword, 10, 0, {"https" : p_list[num]})
            #html = crawl_google(crawler, keyword, 10, 0)
            soup = BeautifulSoup(html)
            cite_list = extract_cite_list_from_html(soup)
            if len(cite_list) == 0:
                print "cite list is empty",
                raise Exception
        except KeyboardInterrupt:
            break
        except Exception, e:
            print e
            print "Error! delete proxy %s" % p_list[num]
            crawler = requests.Session()
            del p_list[num]
            print "%d remained\n" % len(p_list)
            if len(p_list) == 0:
                p_list = get_https_proxy_list()
            num = select_random_number_from_list(p_list)
            continue
        break

    soup = BeautifulSoup(html)
    cite_list = extract_cite_list_from_html(soup)
    print "cite list length %d" % len(cite_list)
    domain_list = extract_domain_list_from_cite_list(cite_list)

    sleep_function(5, 10)

    for ele in domain_list:
        while True:
            try:
                print "Select proxy : %s" % p_list[num]
                html = crawl_google(crawler, "site:" + ele, 15, 0, {"https" : p_list[num]})
                #html = crawl_google(crawler, "site:" + ele, 10, 0)
                soup = BeautifulSoup(html)
                cite_list = extract_cite_list_from_html(soup)
                if len(cite_list) == 0:
                    print "cite list is empty",
                    raise Exception
            except KeyboardInterrupt:
                break
            except Exception, e:
                print e
                print "Error! delete proxy %s" % p_list[num]
                del p_list[num]
                print "%d remained\n" % len(p_list)
                crawler = requests.Session()
                if len(p_list) == 0:
                    p_list = get_https_proxy_list()
                num = select_random_number_from_list(p_list)
                continue
            break

        soup = BeautifulSoup(html)
        cite_list = extract_cite_list_from_html(soup)
        cnt = 0
        for cite in cite_list:
            url = cite.text
            if is_spider_pool_url(url):
                print "check url : %s : yes" % url
                cnt += 1
            else:
                print "check url : %s : no" % url
        if cnt >= 4:
            print keyword + " " + ele
            with codecs.open("result2.txt", "a") as f:
                f.write(keyword + " " + ele + "\n")
        else:
            print ele + " is not a spider pool"
        sleep_function(7, 13)

    with open("visited2.txt", "a") as f:
        f.write(keyword + "\n")
    print "Finished\n===================="

def run():
    keyword_list = []
    f = open("medicine.txt")
    for line in f:
        keyword_list.append(line.strip())
    f.close()

    for keyword in keyword_list:
        detect(keyword)


if __name__ == '__main__':
    run()

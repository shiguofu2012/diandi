# coding=utf-8

import re
import time
from lxml.html import fromstring
from weixin.utils.httpclient import HttpClient
from weixin.settings import LOG_CRAWLER as LOG


def get_detail_url(detail_url, author_id):
    client = HttpClient()
    page_content = client.get(detail_url)
    if page_content:
        dom = fromstring(page_content)
        cont_xpath = '//div[@class="main3"]/div[@class="left"]/'\
            'div[@class="sons"][1]'
        title = dom.xpath("//h1/text()")
        dynasty = dom.xpath(cont_xpath + '/div[@class="cont"]/p/a[1]/text()')
        author = dom.xpath(cont_xpath + '/div[@class="cont"]/p/a[2]/text()')
        content = dom.xpath(
                cont_xpath +
                '/div[@class="cont"]/div[@class="contson"]')
        content = split_content(content[0])
        keywords = dom.xpath(cont_xpath + '/div[@class="tag"]/a/text()')
        keywords = '&'.join(keywords)
        likes = dom.xpath(cont_xpath + '//div[@class="good"]/a/span/text()')
        if len(likes) >= 1:
            likes = match_number(likes[0])
        else:
            likes = 0
        fanyi = dom.xpath("//div[starts-with(@id, 'fanyi')][1]/@id")
        if fanyi:
            fanyi_id = match_number(fanyi[0])
            fanyi_con = get_fanyi_content(fanyi_id)
        else:
            fanyi_xpath = "//div[@class='left']/div[@class='sons'][2]/div[@class='contyishang']/p/text()"
            fanyi_con = dom.xpath(fanyi_xpath)
            if fanyi_con:
                fanyi_con = '\n'.join(fanyi_con)
            else:
                fanyi_con = ''
        shangxi = dom.xpath("//div[starts-with(@id, 'shangxi')][1]/@id")
        if shangxi:
            shangxi_id = match_number(shangxi[0])
            shangxi_con = get_shangxi_content(shangxi_id)
        else:
            shangxi_con = ''

        if not shangxi_con:
            LOG.info("url: %s no shangxi", detail_url)
        if not fanyi_con:
            LOG.info("url: %s no fanyi", detail_url)

        poetry_data = {
                'title': title[0],
                'dynasty': dynasty[0],
                'author': author[0],
                'content': content,
                'tags': keywords,
                'likes': likes,
                'author_id': author_id,
                'translate': fanyi_con,
                'shangxi': shangxi_con,
                'plink': detail_url
                }
        # print(poetry_data)
        return poetry_data
    else:
        LOG.error("download url: %s, error", detail_url)
        return {}


def split_content(content_xpath):
    poetry_con = ''
    start = content_xpath.text
    start = start.replace("\n", '')
    start = start.strip()
    if start:
        poetry_con += start
        poetry_con += '\n'
    for juzi in content_xpath:
        tmp = ''
        if juzi.text:
            tmp = juzi.text
        elif juzi.tail:
            tmp = juzi.tail
        tmp = tmp.replace("\n", '')
        tmp = tmp.strip()
        if tmp:
            poetry_con += tmp
            poetry_con += '\n'
        children = juzi.getchildren()
        for child in children:
            if child.text:
                tmp = child.text
            elif child.tail:
                tmp = child.tail
            else:
                tmp = ''
            tmp = tmp.replace("\n", '')
            tmp = tmp.strip()
            if not tmp:
                continue
            poetry_con += tmp
            poetry_con += '\n'
    return poetry_con[:-1]


def get_fanyi_content(fanyi_id):
    url = 'https://so.gushiwen.org/shiwen2017/ajaxfanyi.aspx'
    params = {'id': fanyi_id}
    time.sleep(10)
    client = HttpClient()
    page_content = client.get(url, params=params)
    # page_content = open("fanyi.html").read()
    fanyi = ''
    if page_content:
        page_content = unicode(page_content, 'utf-8')
        dom = fromstring(page_content)
        elements = dom.xpath("//div[@class='contyishang']/p")
        for element in elements:
            for sub in element:
                tag = sub.tag
                if tag == 'strong':
                    continue
                elif tag == 'a':
                    fanyi = fanyi[:-1]
                    tmp = sub.text
                elif tag == 'br':
                    tmp = sub.tail
                    if tmp is None:
                        continue
                    tmp += '\n'
                if tmp:
                    tmp = tmp.replace(u"▲", "")
                    fanyi += tmp
    else:
        LOG.info("down page error: %s, params: %s", url, params)
    return fanyi


def get_shangxi_content(shangxi_id):
    url = 'https://so.gushiwen.org/shiwen2017/ajaxshangxi.aspx'
    params = {'id': shangxi_id}
    time.sleep(10)
    client = HttpClient()
    page_content = client.get(url, params=params)
    shangxi = ''
    if page_content:
        page_content = unicode(page_content, 'utf-8')
        dom = fromstring(page_content)
        elements = dom.xpath("//div[@class='contyishang']/p")
        for element in elements:
            tmp = element.xpath("string(.)")
            tmp = tmp.replace(u"▲", "")
            shangxi += tmp
            shangxi += '\n'
    else:
        LOG.debug("down page error: %s, params: %s", url, params)
    return shangxi


def match_number(source):
    pattern = re.compile(r'\d+')
    ret = pattern.search(source)
    num = 0
    if ret:
        num = int(ret.group())
    return num


if __name__ == '__main__':
    data = get_detail_url('https://so.gushiwen.org/shiwenv_5dfc1bd59fed.aspx', 3)
    print data.get('content')
    # print data
    # print get_fanyi_content("1")

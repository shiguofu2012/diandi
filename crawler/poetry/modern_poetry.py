# coding=utf-8

import re
import time
from urlparse import urljoin
from lxml.html import fromstring
from crawler.poetry.poetry_crawler import download_page
from crawler.poetry.crawler_model import check_save_author, save_crawled_poetry
from crawler.poetry.poetry_detail import split_content
from weixin.settings import LOGGER as LOG


def _split_desc(desc):
    if not isinstance(desc, list):
        desc = [desc]
    result = ''
    for _desc in desc:
        tmp = _desc.strip()
        if not tmp.replace("\n", ''):
            continue
        result += tmp
    return result


def _split_total(text):
    if isinstance(text, list):
        if len(text) >= 1:
            text = text[0]
        else:
            return 0
    pattern = u'(?P<total>\d+)首'
    pattern = re.compile(pattern)
    match = pattern.search(text)
    if match:
        count = match.group("total")
        try:
            count = int(count)
        except Exception:
            count = 0
    else:
        count = 0
    return count


def should_crawler_author(link):
    name = link.split("/")[-1]
    name_list = name.split("_")
    if len(name_list) == 2:
        return False
    return True


def _crawler_author(content, poetry_links=''):
    author_area = "//div[@class='zuozhe-header www-shadow-card']"
    author_dom = fromstring(content).xpath(author_area)
    if not author_dom:
        return {}
    author_dom = author_dom[0]
    name = author_dom.xpath("./h2")
    if not name:
        name = ''
    else:
        name = name[0].xpath("string()")
    author_info = author_dom.xpath("./div")
    avatar = author_dom.xpath("./div[@class='summary']/img/@src")
    dynasty = u'现代'
    desc = ''
    head_img = ''
    total = 0
    if author_info:
        dynasty = author_info[1].xpath("text()")
        dynasty = dynasty[0]
        total = author_info[2].xpath("text()")
        total = _split_total(total)
        desc = author_info[3].xpath("text()")
        desc = _split_desc(desc)
    if avatar and isinstance(avatar, list):
        head_img = avatar[0]
    author_data = {
            'name': name,
            'headimg': head_img,
            'description': desc,
            'total': total,
            'created': int(time.time() * 1000),
            'poetry_link': '',
            'dynasty': dynasty}
    return author_data


def crawler_one_author(link):
    print(link)
    content = download_page(link)
    if not content:
        return -1
    # if should_crawler_author(link):
    # link = 'http://www.shicimingju.com/chaxun/zuozhe/13.html'
    author_data = _crawler_author(content)
    author_data = check_save_author(author_data)
    dom = fromstring(content)
    detail_list = dom.xpath("//h3/a/@href")
    for url in detail_list:
        detail_url = urljoin(link, url)
        try:
            poetry_data = crawler_one_poetry(detail_url, author_data)
            print save_crawled_poetry(poetry_data)
        except Exception as ex:
            LOG.info("url: %s, ex: %s", detail_url, ex)


def crawler_one_poetry(url, author_data):
    author_id = author_data['id']
    author_name = author_data['name']
    dynasty = author_data['dynasty']
    content = download_page(url)
    if not content:
        return -1
    dom = fromstring(content)
    title_xpath = '//h1[@class="shici-title"]'
    content_xpath = '//div[@class="shici-content"]'
    shangxi_xpath = '//div[@class="shangxi-container"]'
    title = split_content(dom.xpath(title_xpath)[0])
    content = split_content(dom.xpath(content_xpath)[0])
    shangxi = ''
    if dom.xpath(shangxi_xpath):
        shangxi = split_content(dom.xpath(shangxi_xpath)[0])
    poetry_data = {
            "title": title.strip(),
            "content": content.strip(),
            "created": int(time.time() * 1000),
            "banner": '',
            'tags': '',
            'author_id': author_id,
            'dynasty': dynasty,
            'author': author_name,
            'translate': shangxi.strip(),
            'shangxin': '',
            'plink': url,
            'likes': 0
            }
    return poetry_data


if __name__ == '__main__':
    # f = open("test.html")
    # content = f.read()
    # f.close()
    # _crawler_author(content)
    crawler_one_author('http://www.shicimingju.com/chaxun/zuozhe/13_2.html')

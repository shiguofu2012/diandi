# coding=utf-8
# !/usr/bin/python
'''crawler'''

import re
from urlparse import urljoin
from lxml.html import fromstring
from weixin.utils.httpclient import HttpClient
from weixin.settings import LOGGER as LOG
from crawler.poetry.crawler_model import save_crawled_author


tang_start_url = 'https://so.gushiwen.org/authors/Default.aspx'


def download_page(url, **kwargs):
    '''down page by requests session'''
    client = HttpClient()
    content = client.get(url, **kwargs)
    if not content:
        return None
    if content.find("404 Not Found") != -1:
        return None
    return content


def get_poetry_count(count_desc):
    pattern = re.compile(r'\w+')
    ret = pattern.search(count_desc)
    count = 0
    if ret:
        count = int(ret.group())
    return count


def get_tag_value(tags):
    tags_list = []
    if tags:
        for tag in tags:
            tags_list.append(tag.text)
    return tags_list


def gen_url(path, base_url):
    return urljoin(base_url, path)


def link_crawler(content, base_url):
    xpath = "//div[@class='sonspic']/div[@class='cont']"
    head_img_xpath = "./div[@class='divimg']/a/img/@src"
    name_xpath = "./p[1]/a/b/text()"
    desc_xpath = "./p[2]/text()"
    detail_xpath = "./p[2]/a/@href"
    poetry_count_xpath = "./p[2]/a/text()"

    dom = fromstring(content)
    conts = dom.xpath(xpath)
    result = []
    for cont in conts:
        head_img = cont.xpath(head_img_xpath)
        name = cont.xpath(name_xpath)
        desc = cont.xpath(desc_xpath)
        detail_link = cont.xpath(detail_xpath)
        poetry_count = cont.xpath(poetry_count_xpath)
        if not all([name, desc, detail_link, poetry_count]):
            continue
        if len(head_img) > 1:
            head_img = gen_url(head_img[0], base_url)
        else:
            head_img = ''
        name = name[0]
        desc = desc[0]
        detail_link = gen_url(detail_link[0], base_url)
        poetry_count = get_poetry_count(poetry_count[0])
        LOG.debug(
            "name: %s, link: %s, count: %s, head: %s",
            name, detail_link, poetry_count, head_img)
        poetry_summary = {
            'name': name,
            'headimg': head_img,
            'description': desc,
            'poetry_link': detail_link,
            'total': poetry_count,
            'dynasty': u'清代'}
        author_id = save_crawled_author(poetry_summary)
        if author_id:
            poetry_summary.update({'author_id': author_id})
            result.append(poetry_summary)
    return result


def detail_crawler(detail_url):
    '''
    return value:
    -1 --- download error
    '''
    content = download_page(detail_url)
    if not content:
        return -1
    dom = fromstring(content)
    xpath = "//div[@class='sons']"
    # title_xpath = "./div[@class='cont']/p[1]/a/b/text()"
    title_link = './div[@class="cont"]/p[1]/a/@href'
    next_page = "//div[@class='pagesright']/a[@class='amore']/@href"
    # dynasty_xpath = "./div[@class='cont']/p[@class='source']/a[1]/text()"
    # author_xpath = "./div[@class='cont']/p[@class='source']/a[2]/text()"
    # content_xpath = "./div[@class='cont']/div[@class='contson']"
    # tag_xpath = "./div[@class='tag']/a"
    ret_urls = []
    conts = dom.xpath(xpath)
    for cont in conts:
        detail_link = cont.xpath(title_link)
        detail_link = detail_link[0]
        detail_link = gen_url(detail_link, detail_url)
        ret_urls.append(detail_link)
    next_page = dom.xpath(next_page)
    if next_page:
        next_page = gen_url(next_page[0], detail_url)
    else:
        next_page = ''
    return ret_urls, next_page


if __name__ == '__main__':
    page = 51
    params = {'p': page, 'c': u'清代'.encode('utf-8')}
    while page <= 51:
        cont = download_page(tang_start_url, params=params)
        ret = link_crawler(cont, tang_start_url)
        print("page: %s, save: %s" % (page, len(ret)))
        page += 1
        params.update({'p': page})
    # urls, next_url = detail_crawler(
    #         "https://so.gushiwen.org/authors/authorvsw_85097dd0c645A31.aspx")
    # print urls, len(urls)
    # CACHE.save_string("a", "123", 60)

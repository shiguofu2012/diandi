# coding=utf-8

from urlparse import urljoin
from lxml.html import fromstring
from weixin.utils.httpclient import HttpClient


HOME = 'http://www.chengyugushi.net/'
DETAIL = 'http://www.chengyugushi.net/sizichengyu/wangyangbulao.html'


def down_page(url):
    client = HttpClient()
    try_times = 3
    while try_times > 0:
        res = client.get(url)
        if res:
            return res
        try_times -= 1
    return ''


def extract_detail_url(content):
    dom = fromstring(content)
    xpath = "//div[@class='si']/ul/li"
    detail_urls = dom.xpath(xpath)
    for url_xpath in detail_urls:
        url = url_xpath.xpath("./a[1]/@href")
        if url:
            detail_url = urljoin(HOME, url[0])
            yield detail_url


def extract_detail(detail_url):
    pass


if __name__ == "__main__":
    # content = down_page(HOME)
    # for detail in extract_detail_url(content):
    #     print detail

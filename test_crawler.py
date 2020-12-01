# coding=utf-8

from urlparse import urljoin
from lxml.html import fromstring
from crawler.poetry.modern_poetry import _crawler_author, crawler_one_author, \
        download_page

IGNORE_LIST = ['13.html', '103.html', '114.html', '270.html', '743.html',
        '744.html', '4297.html', '4575.html', '4577.html', '4681.html',
        '4672.html', '4660.html', '4659.html', '4684.html', '4705.html',
        '4750.html', '310.html', '309.html', '200.html', '91.html', '49.html',
        '5041.html', '4760.html', '4761.html', '5017.html', '5048.html',
        '203.html', '4753.html', '4770.html']


def crawler_author_list():
    # url = 'http://www.shicimingju.com/category/jindaishiren'
    # url = 'http://www.shicimingju.com/category/jindaishiren__2'
    # url = 'http://www.shicimingju.com/category/xiandaishiren'
    # url = 'http://www.shicimingju.com/category/xiandaishiren__2'
    url = 'http://www.shicimingju.com/category/dangdaishiren'
    content = download_page(url)
    dom = fromstring(content)
    urls = dom.xpath("//h3/a/@href")
    page = 1
    for path in urls:
        ignore_flag = False
        for ignore in IGNORE_LIST:
            if path.find(ignore) != -1:
                ignore_flag = True
                break
        if ignore_flag:
            continue
        author_url = urljoin(url, path)
        page_url = author_url.rsplit('.')[-2]
        ret = None
        while ret is None:
            print(author_url)
            ret = crawler_one_author(author_url)
            url_list = author_url.rsplit(".")
            url_list[-2] = page_url + "_{}".format(page + 1)
            author_url = '.'.join(url_list)
            page += 1


if __name__ == '__main__':
    crawler_author_list()
    # print download_page("http://www.shicimingju.com/chaxun/zuozhe/13_3.html")

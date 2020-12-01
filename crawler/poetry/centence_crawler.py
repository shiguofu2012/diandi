# coding=utf-8

from urllib import quote
from lxml.html import fromstring
from weixin.utils.httpclient import HttpClient
from crawler.poetry.crawler_model import save_centence
from crawler.poetry.crawler_model import update_sentence


START_URL = 'https://so.gushiwen.org/mingju/Default.aspx'
C_LIST = [
        u"抒情", u"四季", u"山水", u"天气", u"人物", u"人生", u"生活", u"节日",
        u"动物", u"植物", u"食物", u"古籍"]
T_LIST = [
        u"爱情", u"友情", u"离别", u"思念", u"思乡", u"伤感", u"孤独", u"闺怨",
        u"悼亡", u"怀古", u"爱国", u"感恩"]


def download_page(c, t=None):
    client = HttpClient()
    params = {
            'p': 1,
            "c": quote(c.encode('utf-8')),
            }
    if t:
        params.update({'t': quote(t.encode("utf-8"))})
    res = client.get(START_URL, params=params)
    return res


def extract_centence(page_content, c, t_text):
    centense_xpath = "//div[@class='left']/div[@class='sons']/div[@class='cont']"
    dom = fromstring(page_content)
    centences = dom.xpath(centense_xpath)
    for centence in centences:
        cent = centence.xpath("./a[1]/text()")
        source = centence.xpath("./a[2]/text()")
        if cent and source:
            cent = cent[0]
            source = source[0]
            cent = cent.replace('\'', '')
            source = source.replace('\'', '')
            save_centence(cent, source, c, t_text)
        else:
            print cent, source


def crawler_centense(c):
    page_content = download_page(c)
    # page_content = open("test.html").read()
    sub_type_xpath = "//div[@class='titletype']/div[@class='son2'][2]//a"
    dom = fromstring(page_content)
    style = dom.xpath(sub_type_xpath)
    for t in style:
        t_text = t.text
        page_content = download_page(c, t_text)
        extract_centence(page_content, c, t_text)


if __name__ == '__main__':
    # update_sentence()
    # for c in C_LIST:
    #     if c not in [u"抒情", u"四季"]:
    #         crawler_centense(c)
    # page_content = open("first.html", 'r').read()
    # extract_centence(page_content, u"抒情", u"爱情")
    crawler_centense(u"古籍")

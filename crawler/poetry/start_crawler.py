# coding=utf-8

from weixin.models.author_model import Author
from weixin.models.poetry_model import Poetry
from weixin.settings import LOG_CRAWLER as LOGGER
from crawler.poetry.poetry_crawler import detail_crawler
from crawler.poetry.poetry_detail import get_detail_url
from crawler.poetry.crawler_model import save_crawled_poetry


def check():
    page = 1
    count = 100
    author_obj = Author()
    while True:
        authors = author_obj.find_authors(
                {}, page, count)
        LOGGER.info("type: %s, len: %s", type(authors), len(authors))
        if not authors:
            break
        for author in authors:
            _id = author['id']
            ps = Poetry(author_id=_id)
            ret = ps.find_poetry_by_author_id(1, 1)
            if len(ret) == 0:
                # print("_id: %s not found" % _id)
                crawler_author_poetry(_id)
        page += 1


def crawler_author_poetry(author_id=None):
    page = 1
    count = 100
    author_obj = Author()
    while True:
        if author_id is None:
            authors = author_obj.find_authors(
                    {"id": {">": 1229}}, page, count)
        else:
            authors = author_obj.find_authors(
                    {'id': {'=': author_id}}, page, count)
        LOGGER.info("type: %s, len: %s", type(authors), len(authors))
        if not authors:
            break
        for author in authors:
            try:
                LOGGER.info("start crawler author: %s", author['name'])
                crawler_author_record(author)
                LOGGER.info(author)
            except Exception as ex:
                LOGGER.error(
                        "author: %s, ex: %s", author['name'], ex,
                        exc_info=True)
            # time.sleep(60)
        page += 1


def crawler_author_record(author):
    next_page = author['poetry_link']
    author_id = author['id']
    count = 0
    while next_page:
        detail_links, next_page = detail_crawler(next_page)
        for poetry_link in detail_links:
            try:
                poetry_data = get_detail_url(poetry_link, author_id)
                poetry_id = save_crawled_poetry(poetry_data)
                if poetry_id:
                    count += 1
                LOGGER.debug(
                        "save poetry: %s, authorid: %s", poetry_id, author_id)
            except Exception as ex:
                LOGGER.error(
                        "link: %s, ex: %s", poetry_link, ex, exc_info=True)
            # time.sleep(random.randint(6, 10))
        LOGGER.info("page: %s, save: %s", next_page, count)
        count = 0


def crawler_poetry_record(link, author_id):
    try:
        poetry_data = get_detail_url(link, author_id)
        poetry_id = save_crawled_poetry(poetry_data)
        if poetry_id:
            LOGGER.info("link: %s, author: %s ok", link, author_id)
        else:
            LOGGER.info("link: %s, not save")
    except Exception as ex:
        LOGGER.error("link: %s, ex: %s", link, ex, exc_info=True)


if __name__ == '__main__':
    check()
    # crawler_author_poetry()
    # crawler_poetry_record("https://so.gushiwen.org/shiwenv_77901dbd6a8c.aspx", 3)

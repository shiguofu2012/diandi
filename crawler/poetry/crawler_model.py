# coding=utf-8

import re
from weixin.models.author_model import Author
from weixin.models.poetry_model import Poetry, Sentence
from weixin.settings import LOG_CRAWLER as LOG


def save_crawled_author(author_data):
    author_obj = Author(**author_data)
    author_record = author_obj.find_author_by_name()
    if author_record:
        return None
    author_id = author_obj.save_author()
    return author_id


def check_save_author(author_data):
    author_obj = Author(**author_data)
    author_record = author_obj.find_author_by_name()
    if not author_record:
        author_obj.save_author()
        author_record = author_obj.find_author_by_name()
    return author_record


def save_crawled_poetry(poetry_data):
    for key, value in poetry_data.items():
        if isinstance(value, unicode):
            poetry_data[key] = value.encode('utf-8')
    poetry_obj = Poetry(**poetry_data)
    if poetry_obj.check_duplicate():
        return None
    ret = poetry_obj.save()
    return ret


def save_centence(centence, source, c, t):
    pattern = re.compile(u"(?P<author>.*)《(?P<title>.*)》")
    match = pattern.search(source)
    if not match:
        LOG.info("cent: %s, source: %s error", centence, source)
        return
    author = match.group("author")
    title = match.group("title")
    poetry_obj = Poetry(title=title, author=author)
    poetry = poetry_obj.find_poetry_by_title()
    if not poetry:
        LOG.error("title: %s, author: %s found error", title, author)
        poetry = {}
    centence_data = {
            "title": title,
            "content": centence,
            "tags": '&'.join([c, t]),
            "author_id": poetry.get('author_id', 0),
            "author": author,
            "poetry_id": poetry.get('id', 0)
            }
    sentence_obj = Sentence(**centence_data)
    sentence_obj.save()


def update_sentence():
    sentence_instance = Sentence()
    page = 1
    count = 100
    while True:
        sentences = sentence_instance.find_sentence_by_cond({}, page, count)
        if not sentences:
            break
        for sentence in sentences:
            poetry_id = sentence['poetry_id']
            if poetry_id == 0:
                poetry = {}
            else:
                poetry_obj = Poetry(id=poetry_id)
                poetry = poetry_obj.find_poetry_by_id()
            sentence_obj = Sentence(**sentence)
            sentence_obj.update_sentence_by_id(
                    {'likes': poetry.get('likes', 0), 'type': 0})
        page += 1

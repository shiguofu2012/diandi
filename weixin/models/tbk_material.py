# coding=utf-8


from weixin.models import MONGO_DB as db


def get_material_by_id(mat_id):
    return db.find_one("material", {'_id': mat_id})


def get_project_by_id(pro_id):
    return db.find_one("projects", {'_id': pro_id})


def get_links(page, count):
    skip = (page - 1) * count
    cond = {}
    return db.find("links", cond).skip(skip).limit(count)


def get_table_by_mid(mid):
    cond = {'mid': int(mid)}
    record = db.find_one('links', cond)
    table = ''
    if record:
        table = record.get('table', '')
    return table

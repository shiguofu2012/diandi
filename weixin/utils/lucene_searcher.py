# coding=utf8


import jnius

LUCENE_DIR = "/var/app/weixin/data/lucene"
LUCENE_API = jnius.autoclass("cn.shiguofu.lucene.LuceneAPI")
GOODS_BEANS = jnius.autoclass("cn.shiguofu.beans.Goods")
SEARCH_PARAMS = jnius.autoclass("cn.shiguofu.beans.SearchParams")


class LuceneSearcher(object):

    lucene_instance = None

    def __init__(self, path):
        self.lucene_instance = LUCENE_API(path)

    def create_index(self, goods_data):
        goods_instance = convert_goods_instance(goods_data)
        index_ret = self.lucene_instance.indexData(goods_instance)
        if not index_ret:
            return {'errcode': -1, 'errmsg': "failed"}
        return {'errcode': 0}

    def update_index(self, goods_data):
        num_id = goods_data['num_id']
        update_ret = self.lucene_instance.updateData(
            str(num_id), "id", convert_goods_instance(goods_data))
        if not update_ret:
            return {'errcode': -1}
        return {'errcode': 0}

    def delete_index(self, num_id):
        del_ret = self.lucene_instance.deleteData(str(num_id), "id")
        if not del_ret:
            return {'errcode': -1}
        return {'errcode': 0}

    def total_docs(self):
        return self.lucene_instance.totalDocs()

    def search(self, keyword, sort_dict, page=1, count=20):
        sp = SEARCH_PARAMS()
        sp.setWord(keyword)
        sp.setWordToken(True)
        sp.setMinSales(100)
        if sort_dict and isinstance(sort_dict, dict):
            sort = sp.getSort()
            Boolean = jnius.autoclass("java.lang.Boolean")
            for sort_field, reverse in sort_dict.items():
                sort_reverse = Boolean('true') if reverse < 0 else \
                    Boolean("false")
                sort.put(sort_field, sort_reverse)
        goods_list = self.lucene_instance.search(sp, page, count)
        result = []
        for i in range(goods_list.size()):
            goods_data = goods_list.get(i)
            iterator = goods_data.entrySet().iterator()
            tmp = {}
            while(iterator.hasNext()):
                data = iterator.next()
                tmp[data.getKey()] = data.getValue()
            result.append(tmp)
        return result


def convert_goods_instance(goods_data):
    goods_instance = GOODS_BEANS()
    title = goods_data['title']
    title = title.encode("utf-8")
    goods_instance.setId(str(goods_data['num_id']))
    goods_instance.setFee(goods_data['coupon_fee'])
    goods_instance.setSales(goods_data['sales'])
    goods_instance.setTitle(title)
    goods_instance.setCouponAmount(goods_data['coupon_amount'])
    goods_instance.setCreated(goods_data['created'] / 1000)
    goods_instance.setCommssionMoney(0)
    goods_instance.setTable(goods_data.get("table", ''))
    return goods_instance


SEARCHER_LUCENE = LuceneSearcher(LUCENE_DIR)

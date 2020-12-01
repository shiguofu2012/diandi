#!/usr/bin/python
# coding=utf-8

import os
import uuid
import imghdr
import re
import random
from urlparse import urlparse
from datetime import datetime
from StringIO import StringIO
from PIL import Image, ImageDraw, ImageFont
from weixin.utils.lunar_date import OPEN_API_CLIENT as open_api_client
from weixin.utils.qiniu_storage import QINIU_STORAGE as qiniu_storage
from weixin.utils.constants import STATIC_PATH, STATIC_URI, WEEKDAY_MAP, \
        FONT_DIR, SHARE_PATH, UPLOAD_PATH, BANNER_SAMP,\
        FONT_DIR as FONT_BASE_PATH, PIC_DIR as PIC_BASE_PATH, TBK_PATH
from weixin.utils.decorator import perf_logging
from weixin.utils.httpclient import HttpClient
from weixin.settings import QINIU_DOMAIN, LOGGER


def random_choose_banner(sample_dir=None):
    if not sample_dir:
        sample_dir = BANNER_SAMP
    sample_files = os.listdir(sample_dir)
    file_ = random.choice(sample_files)
    abpath = os.path.join(sample_dir, file_)
    if os.path.isdir(abpath):
        return random_choose_banner(abpath)
    return abpath


def upload_file_to_server(file_content, suffix=None):
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    name = uuid.uuid4().hex
    if suffix:
        name = name + '.' + suffix
    else:
        sio = StringIO(file_content)
        suffix = imghdr.what(sio)
        sio.close()
        if suffix:
            name = name + '.' + suffix
    file_dir = os.path.join(UPLOAD_PATH, date_str)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    abpath = os.path.join(file_dir, name)
    file_ = open(abpath, 'w')
    file_.write(file_content)
    file_.close()
    return get_url_from_path(abpath)


def get_local_path_from_url(url):
    '''maybe we should download this picture'''
    if url.find(QINIU_DOMAIN) != -1:
        parse_result = urlparse(url)
        path = parse_result.path
    else:
        domain_list = url.split("static")
        path = domain_list[1]
    path = path.lstrip("/")
    return os.path.join(STATIC_PATH, path)


def get_url_from_path(local_path):
    '''maybe we should upload this picture'''
    # remote_path = local_path.split('static')[-1]
    # remote_path = remote_path.lstrip('/')
    # ret, url = qiniu_storage.upload_file(local_path, remote_path)
    # if ret:
    #     return url
    path_list = local_path.split('static')
    return STATIC_URI + path_list[1]


def upload_qiniu_storage(url):
    _http = HttpClient()
    res = None
    try:
        res = _http.get(url)
    except Exception as ex:
        LOGGER.error("url: %s, ex: %s", url, ex, exc_info=True)
        return ''
    if not res:
        return ''
    return upload_image_qiniu(res)


@perf_logging
def upload_image_qiniu(image_data):
    tmp_path = '/tmp/images'
    date_str = datetime.now().strftime("%Y-%m-%d")
    tmp_path = os.path.join(tmp_path, date_str)
    suffix = get_image_suffix(image_data)
    filename = uuid.uuid4().hex
    if suffix:
        filename += "." + suffix
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)
    abpath = os.path.join(tmp_path, filename)
    with open(abpath, 'w') as _file:
        _file.write(image_data)
    ret, url = qiniu_storage.upload_file(abpath, 'images')
    if ret:
        return url
    return ''


def get_lunar_msg():
    today = datetime.now()
    date_str = "{0}-{1}-{2}".format(today.year, today.month, today.day)
    lunar_date_str = open_api_client.get_lunar(date_str)
    lunar_date_info = ''
    if lunar_date_str:
        lunar_date_info = lunar_date_str.split("\n")
        lunar_date_info = lunar_date_info[:2]
        lunar_date_info = ' '.join(lunar_date_info)
        if not isinstance(lunar_date_info, unicode):
            lunar_date_info = unicode(lunar_date_info, 'utf-8')
    return lunar_date_info


def get_image_suffix(image_content):
    sio = StringIO(image_content)
    suffix = imghdr.what(sio)
    if suffix is None:
        return ''
    return suffix


def circle_pic(filename, quality=90):
    ori_img = Image.open(filename)
    size = ori_img.size
    new_size = min(size[0], size[1])
    if size[0] != size[1]:
        ori_img = ori_img.resize((new_size, new_size), Image.ANTIALIAS)
    new_img = Image.new("RGBA", (new_size, new_size), (255, 255, 255, 0))
    ori_img_pix = ori_img.load()
    new_img_pix = new_img.load()
    radius = float(new_size / 2)
    for x_index in range(new_size):
        for y_index in range(new_size):
            dis = pow(x_index - radius, 2) + pow(y_index - radius, 2)
            if dis <= pow(radius, 2):
                new_img_pix[x_index, y_index] = ori_img_pix[x_index, y_index]
    ori_img.close()
    file_dir = filename.split('/')[:-1]
    file_name = filename.split('/')[-1]
    new_file_name = file_name.split('.')[0] + '_cricle.png'
    new_path = os.path.join('/'.join(file_dir), new_file_name)
    new_img.save(new_path, quality=quality)
    return new_path


def re_construct_content(content, count_per_row=23):
    if not isinstance(content, unicode):
        content = unicode(content, 'utf-8')
    pattern = re.compile(u"[(（].*[)）]")
    content = pattern.sub("", content)
    content_list = []
    content = content.split("\n")
    for juzi in content:
        if len(juzi) > count_per_row:
            rows = len(juzi) / count_per_row + 1
            for row in range(rows):
                start = row * count_per_row
                content_list.append(juzi[start: start + count_per_row])
                if len(content_list) >= 4:
                    break
        else:
            content_list.append(juzi)
        if len(content_list) >= 4:
            break
    return '\n'.join(content_list)


def draw_poetry_share(
        user_name,
        headimg_path,
        qrcode_path,
        banner_path,
        title,
        content,
        dynasty='',
        author_name=''):

    if not isinstance(title, unicode):
        title = unicode(title, 'utf-8')
    if not isinstance(content, unicode):
        content = unicode(content, 'utf-8')
    if not isinstance(user_name, unicode):
        user_name = unicode(user_name, 'utf-8')
    if not isinstance(dynasty, unicode):
        dynasty = unicode(dynasty, 'utf-8')
    if not isinstance(author_name, unicode):
        author_name = unicode(author_name, 'utf-8')
    content = re_construct_content(content)
    nickname = user_name if len(user_name) <= 4 else user_name[:4] + u'..'
    author_info = ''
    if dynasty:
        author_info += dynasty
    if author_name:
        author_info += (u":" + author_name)
    today = datetime.now()
    date = today.strftime("%m-%d")

    base_img = Image.new('RGBA', (600, 1000), (230, 230, 230))
    font_title = ImageFont.truetype(
            os.path.join(FONT_DIR, "PingFang_Bold.ttf"), 35)
    font_content = ImageFont.truetype(
            os.path.join(FONT_DIR, "PingFang_Regular.ttf"), 25)
    font_hide = ImageFont.truetype(
            os.path.join(FONT_DIR, "PingFang_Medium.ttf"), 18)
    font_date = ImageFont.truetype(
            os.path.join(FONT_DIR, "PingFang_Bold.ttf"), 30)
    font_year = ImageFont.truetype(
            os.path.join(FONT_DIR, "PingFang_Medium.ttf"), 15)
    draw = ImageDraw.Draw(base_img)
    draw.text((20, 620), title, fill='#333', font=font_title)
    author_info_pos = 20 + 35 * len(title) + 10
    if author_info_pos < 520:
        draw.text(
                (author_info_pos, 640),
                author_info, fill='#aaa', font=font_hide)
    draw.text((10, 680), content, fill='#333', font=font_content)
    draw.text((40, 845), u"====长按识别====", fill='#AAAAAA', font=font_hide)
    draw.text((400, 845), u"====赏析诗文====", fill='#AAAAAA', font=font_hide)
    draw.text((30, 920), date, fill="#000", font=font_date)
    draw.text(
            (125, 920),
            u"%s年 星期%s" % (today.year, WEEKDAY_MAP[today.weekday()]),
            fill="#000",
            font=font_year)
    lunar_msg = get_lunar_msg()
    draw.text((125, 940), lunar_msg, fill="#000", font=font_year)
    draw.text((460, 960), u"%s" % nickname, fill="#000", font=font_year)
    pic_img = Image.open(banner_path)
    pic_img = pic_img.resize((600, 600), Image.ANTIALIAS)
    base_img.paste(pic_img, (0, 0))
    pic_img.close()

    qr_img = Image.open(qrcode_path)
    qr_img = qr_img.resize((100, 100), Image.ANTIALIAS)
    qr_rgba = qr_img.split()
    base_img.paste(qr_img, (250, 820), mask=qr_rgba[-1])
    qr_img.close()

    headimg_path = circle_pic(headimg_path)
    headimg = Image.open(headimg_path)
    headimg = headimg.resize((50, 50), Image.ANTIALIAS)
    headimg_rgba = headimg.split()
    base_img.paste(headimg, (460, 905), mask=headimg_rgba[-1])
    headimg.close()

    share_file_name = uuid.uuid4().hex + '.png'
    file_dir = os.path.join(SHARE_PATH, today.strftime("%Y-%m-%d"))
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    abpath = os.path.join(
            file_dir,
            share_file_name)
    base_img.save(abpath)
    return abpath


def new_date_image():
    today = datetime.now()
    share_path = os.path.join(SHARE_PATH, today.strftime("%Y-%m-%d"))
    if not os.path.exists(share_path):
        os.makedirs(share_path)
    abpath = os.path.join(share_path, "date_image.png")
    if os.path.exists(abpath):
        return abpath
    lunar_msg = get_lunar_msg()
    year_msg = u"%s年" % today.strftime("%Y")
    month_msg = u"%s月 " % today.strftime("%m")
    day_msg = today.strftime("%d")
    if not isinstance(day_msg, unicode):
        day_msg = unicode(day_msg)
    weekday_msg = u"星期%s" % WEEKDAY_MAP[today.weekday()]
    font_month = ImageFont.truetype(
            os.path.join(FONT_DIR, "PingFang_Bold.ttf"), 40)
    font_year = ImageFont.truetype(
            os.path.join(FONT_DIR, "PingFang_Medium.ttf"), 20)
    font_day = ImageFont.truetype(
            os.path.join(FONT_DIR, "PingFang_Bold.ttf"), 100)
    font_weekday = ImageFont.truetype(
            os.path.join(FONT_DIR, "PingFang_Medium.ttf"), 25)
    font_lunar = ImageFont.truetype(
            os.path.join(FONT_DIR, "PingFang_Medium.ttf"), 15)
    font_an = ImageFont.truetype(
            os.path.join(FONT_DIR, "PingFang_Medium.ttf"), 40)
    date_image = Image.new("RGBA", (160, 400), (255, 255, 255, 80))
    draw = ImageDraw.Draw(date_image)
    draw.text((50, 30), year_msg, fill="#000", font=font_year)
    draw.text((40, 50), month_msg, fill="#000", font=font_month)
    draw.text((20, 90), day_msg, fill="#000", font=font_day)
    draw.text((42, 220), weekday_msg, fill="#000", font=font_weekday)
    lunar_horize = (160 - len(lunar_msg) * 15) / 2
    draw.text((lunar_horize, 260), lunar_msg, fill="#000", font=font_lunar)
    draw.text((40, 290), u"早安", fill="#000", font=font_an)
    date_image.save(abpath)
    return abpath


def draw_morning_image(
        banner_path, qrcode_path, author, title, message, count_per_line=16):
    if not isinstance(message, unicode):
        message = unicode(message, 'utf-8')
    if not isinstance(author, unicode):
        author = unicode(author, 'utf-8')
    if not isinstance(title, unicode):
        title = unicode(title, 'utf-8')
    base_img = Image.new('RGBA', (600, 600), (255, 255, 255, 255))
    banner_image = Image.open(banner_path)
    banner_image = banner_image.resize((580, 400), Image.ANTIALIAS)
    base_img.paste(banner_image, (10, 10))

    date_image_path = new_date_image()
    date_image = Image.open(date_image_path)
    date_image_rgba = date_image.split()
    base_img.paste(date_image, (430, 10), mask=date_image_rgba[-1])

    if qrcode_path:
        qr_image = Image.open(qrcode_path)
        qr_image = qr_image.resize((150, 150), Image.ANTIALIAS)
        qr_rgba = qr_image.split()
        base_img.paste(qr_image, (430, 430), qr_rgba[-1])

    font_content = ImageFont.truetype(
            os.path.join(FONT_DIR, "PingFang_Regular.ttf"), 25)
    font_hide = ImageFont.truetype(
            os.path.join(FONT_DIR, "PingFang_Medium.ttf"), 18)
    draw = ImageDraw.Draw(base_img)
    vertical_pos = 430
    if message.find("\n") == -1:
        lines = len(message) / count_per_line + 1
        for line in range(lines):
            start = line * count_per_line
            if line <= 2:
                write_msg = message[start: start + count_per_line]
            elif lines > 3 and len(write_msg) >= count_per_line:
                write_msg = message[start: start + 14] + '...'
            draw.text(
                    (20, vertical_pos),
                    write_msg, fill="#000", font=font_content)
            vertical_pos = vertical_pos + 40
            if line >= 4:
                break
    else:
        draw.text(
                (20, vertical_pos), message, fill="#000", font=font_content)
    if author:
        author_start_pos = 340 - (len(author) - 2) * 25
        draw.text(
                (author_start_pos, vertical_pos),
                u"--%s" % author, fill="#000", font=font_content)
    draw.text((480, 560), u"by 点滴诗词", fill="#aaa", font=font_hide)
    today = datetime.now()
    share_path = os.path.join(SHARE_PATH, today.strftime("%Y-%m-%d"))
    abpath = os.path.join(share_path, uuid.uuid4().hex + '.png')
    base_img.save(abpath)
    return abpath


def draw_tbk_share(qrcode_path, pic_path, title, price, coupon_fee, sales):
    coupon_amount = price - coupon_fee
    if coupon_amount < 0:
        coupon_amount = 0

    base_img = Image.open(os.path.join(PIC_BASE_PATH, 'base.jpg'))
    font_title = ImageFont.truetype(
            os.path.join(FONT_BASE_PATH, "PingFang_Regular.ttf"), 28)
    font_coupon_fee = ImageFont.truetype(
            os.path.join(FONT_BASE_PATH, "PingFang_Bold.ttf"),
            36)
    font_price = ImageFont.truetype(
            os.path.join(FONT_BASE_PATH, "PingFang_Regular.ttf"), 24)
    font_youhui = ImageFont.truetype(
            os.path.join(FONT_BASE_PATH, "PingFang_Medium.ttf"), 46)
    font_sales = ImageFont.truetype(
            os.path.join(FONT_BASE_PATH, "PingFang_Bold.ttf"), 24)
    draw = ImageDraw.Draw(base_img)
    titles = split_title(title)
    vec_pos = 620
    count = 0
    for t in titles:
        draw.text((20, vec_pos), t, fill='#333', font=font_title)
        vec_pos += 38
        count += 1
        if count == 2:
            break

    coupon_fee_msg = u"￥%s" % coupon_fee
    price_msg = u"原价:￥%s" % price
    draw.text((20, 709), coupon_fee_msg, fill='#ff5000', font=font_coupon_fee)
    quanhou_her_pos = len(coupon_fee_msg) * 36
    price_msg_pos = 290
    sales_pos = 450
    draw.text((price_msg_pos, 721),  price_msg, fill='#aaa', font=font_price)
    draw.text((sales_pos, 720), u'已售', fill='#aaa', font=font_price)
    draw.text(
            (sales_pos + 48, 720), sales, fill='#ff5000', font=font_sales)
    draw.text(
            (sales_pos + 40 + len(sales) * 17, 720),
            u'件',
            fill='#aaa',
            font=font_price)
    draw.text(
            (65, 825),
            u'%s元优惠券' % int(coupon_amount),
            fill='#fff', font=font_youhui)

    quanhou_img = Image.open(os.path.join(PIC_BASE_PATH, 'quanhou.jpg'))
    pic_img = Image.open(pic_path)
    pic_img = pic_img.resize((600, 600))
    qr_img = Image.open(qrcode_path)
    qr_img = qr_img.resize((170, 170))
    a = None
    try:
        r, g, b, a = qr_img.split()
    except Exception:
        pass
    line_img = Image.open(os.path.join(PIC_BASE_PATH, 'line.png'))
    base_img.paste(pic_img, (0, 0))
    if a:
        base_img.paste(qr_img, (395, 795), mask=a)
    else:
        base_img.paste(qr_img, (395, 795))
    base_img.paste(quanhou_img, (quanhou_her_pos, 716))
    base_img.paste(line_img, (360, 737))
    pic_img.close()
    qr_img.close()
    quanhou_img.close()
    line_img.close()
    today = datetime.now()
    filepath = os.path.join(TBK_PATH, today.strftime("%Y-%m-%d"))
    abpath = os.path.join(filepath, uuid.uuid4().hex + '.png')
    base_img.save(abpath)
    return abpath


def split_title(title):
    ret = []
    for i in range(len(title) / 20 + 1):
        start = i * 20
        end = (i + 1) * 20
        title_part = title[start: end]
        ret.append(title_part)
    return ret


if __name__ == "__main__":
    # from weixin.models.poetry_model import Poetry
    # poetry_obj = Poetry(id=2)
    # poetry = poetry_obj.find_poetry_by_id()
    # title = poetry['title']
    # content = poetry['content']
    # author = poetry['author']
    # dynasty = poetry['dynasty']
    # title = unicode(title, 'utf-8')
    # content = unicode(content, 'utf-8')
    # draw_img('qrcode.png', "pic.jpg", title, content)
    # print circle_pic('pic.jpg')
    # print get_image_suffix('dfdf')
    # banner_path = random_choose_banner(MORNING_SAMP)
    # print draw_morning_image(
    #         banner_path,
    #         "/opt/front/shiguofu.cn/static/qrcode/2018-11-06/50074797bcf04da4ae72fd2c856fda0c.png",
    #         u"莫扎比特", u"将进酒",
    #         u"一个人至少拥有一个梦想，有一个理由去坚强。心若没有栖息的地方，到哪里都是在流浪。心若没有栖息的地方，到哪里都是在流浪。")
    print new_date_image()

# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LxwcItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class LxwcAudioItem(scrapy.Item):
    #audio
    cate_title_l1 = scrapy.Field()
    cate_url_l1 = scrapy.Field()
    #yw
    cate_title_l2 = scrapy.Field()
    cate_url_l2 = scrapy.Field()
    #egty
    cate_title_l3 = scrapy.Field()
    cate_url_l3 = scrapy.Field()

    album_url = scrapy.Field()
    album_title = scrapy.Field()

    album_desc = scrapy.Field()
    album_sound_list_str = scrapy.Field()

class LxwcVideoItem(scrapy.Item):
    #audio
    cate_title_l1 = scrapy.Field()
    cate_url_l1 = scrapy.Field()
    #yw
    cate_title_l2 = scrapy.Field()
    cate_url_l2 = scrapy.Field()
    #egty
    cate_title_l3 = scrapy.Field()
    cate_url_l3 = scrapy.Field()

    album_url = scrapy.Field()
    album_title = scrapy.Field()

    #album_desc = scrapy.Field()
    #album_sound_list_str = scrapy.Field()
    album_info_img = scrapy.Field()
    album_info_baseinfo = scrapy.Field()
    album_info_desc = scrapy.Field()
    album_src_title = scrapy.Field()
    album_src_url = scrapy.Field()

    album_src_iframe = scrapy.Field()

class LxwcBookItem(scrapy.Item):
    #audio
    cate_title_l1 = scrapy.Field()
    cate_url_l1 = scrapy.Field()
    #yw
    cate_title_l2 = scrapy.Field()
    cate_url_l2 = scrapy.Field()
    #egty
    cate_title_l3 = scrapy.Field()
    cate_url_l3 = scrapy.Field()

    album_url = scrapy.Field()
    album_title = scrapy.Field()

    book_cover_img = scrapy.Field()
    book_base_info = scrapy.Field()
    book_introduction = scrapy.Field()
    book_detail_url = scrapy.Field()

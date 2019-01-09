
# -*-coding: utf-8 -*-
__author__ = "liushan"

import sys, os
from scrapy.spiders import Spider

from scrapy.http import Request

from scrapy.selector import Selector
from lxwc.items import LxwcAudioItem

import logging
logger = logging.getLogger(__name__)

album_url_base = "http://www.lxwc.com.cn/"

#method 1: os.environ["http_proxy"] = "http://1**.***.**.**:80"
#method 2: modify code: middlewares.py

class LxwcAudioSpider(Spider):
    name = "LxwcAudio"
    allowed_domains = ["lxwc.com.cn"]
    start_urls = [
        "http://www.lxwc.com.cn/audio/"
    ]

    def parse(self,response):
        items = []
        sel = Selector(response)

        cate_url_l1 = "http://www.lxwc.com.cn/audio/"
        cate_title_l1 = "音频"

        try:
            cate_urls_l2 = sel.xpath("//div[@class='bm']/div[@class='bm_c bbs']/a/@href").extract()
            cate_titles_l2 = sel.xpath("//div[@class='bm']/div[@class='bm_c bbs']/a/text()").extract()

            if len(cate_urls_l2) == 0:
                logger.warning("!!EXCEPT in <parse>: cate_urls_l2 is NULL")
                return
            for i in range(0,len(cate_urls_l2)):
                item = LxwcAudioItem()
                item['cate_title_l1'] = cate_title_l1
                item['cate_url_l1'] = cate_url_l1

                if_belong = cate_urls_l2[i].startswith(cate_url_l1)
                if (if_belong):
                    item['cate_title_l2'] = cate_titles_l2[i]
                    item['cate_url_l2'] = cate_urls_l2[i]
                    items.append(item)

            for item in items:
                yield Request(url=item['cate_url_l2'],meta={'item_1':item},callback=self.parse_url_l2)

        except Exception as e:
            logger.error("!!EXCEPT in <parse>: err:{0}".format(e))

    def parse_url_l2(self,response):
        sel = Selector(response)
        item_1 = response.meta["item_1"]
        items = []

        try:
            cate_urls_l3 = sel.xpath("//div[@class='bm']/div[@class='bm_c bbs']/a/@href").extract()
            cate_titles_l3 = sel.xpath("//div[@class='bm']/div[@class='bm_c bbs']/a/text()").extract()

            if len(cate_urls_l3) == 0:
                logger.warning("!!EXCEPT in <parse_url_l2>: cate_urls_l3 is NULL")
                return
            for i in range(0,len(cate_urls_l3)):
                if_belong = cate_urls_l3[i].startswith(item_1['cate_url_l2'])
                if (if_belong):
                    item = LxwcAudioItem()
                    item['cate_title_l1'] = item_1['cate_title_l1']
                    item['cate_url_l1'] = item_1['cate_url_l1']
                    item['cate_title_l2'] = item_1['cate_title_l2']
                    item['cate_url_l2'] = item_1['cate_url_l2']
                    item['cate_title_l3'] = cate_titles_l3[i]
                    item['cate_url_l3'] = cate_urls_l3[i]

                    items.append(item)

            for item in items:
                yield Request(url=item['cate_url_l3'], meta={'url':item['cate_url_l3'],'item_2':item},callback=self.parse_url_l3)

        except Exception as e:
            logger.error("!!EXCEPT in <parse_url_l2>: err:{0}|item:{1}".format(e,item_1))

    def parse_url_l3(self,response):
        sel = Selector(response)
        item_2 = response.meta["item_2"]
        items = []

        try:
            album_urls = sel.xpath("//dt[@class='xs2']/a/@href").extract()
            album_titles = sel.xpath("//dt[@class='xs2']/a/text()").extract()

            if len(album_urls) == 0:
                logger.warning("!!EXCEPT in <parse_url_l3>: album_urls is NULL")
                return
            for i in range(0,len(album_urls)):
                if_belong = album_urls[i].endswith('html')
                if (if_belong):
                    item = LxwcAudioItem()
                    item['cate_title_l1'] = item_2['cate_title_l1']
                    item['cate_url_l1'] = item_2['cate_url_l1']
                    item['cate_title_l2'] = item_2['cate_title_l2']
                    item['cate_url_l2'] = item_2['cate_url_l2']
                    item['cate_title_l3'] = item_2['cate_title_l3']
                    item['cate_url_l3'] = item_2['cate_url_l3']
                    item['album_url'] = album_url_base + album_urls[i]
                    item['album_title'] = album_titles[i]

                    items.append(item)

            for item in items:
                yield Request(url=item['album_url'],meta={'item_3':item},callback=self.parse_album)

        except Exception as e:
            logger.error("!!EXCEPT in <parse_url_l3>: err:{0}|item:{1}".format(e,item_2))

        album_remain_pages_urls = []
        try:
            album_remain_pages_urls = sel.xpath("//div[@class='pg']/a/@href").extract()
            if len(album_remain_pages_urls) != 0:
                for album_page_url in album_remain_pages_urls:
                    yield Request(url=album_page_url,meta={'item_2':item_2},callback=self.parse_url_l3)

        except Exception as e:
            logger.error("!! EXCEPT in <parse_url_l3>,handle remain pages: err:{0}".format(e))

    def parse_album(self,response):
        sel = Selector(response)
        item = response.meta["item_3"]
        try:
           tmp_album_desc = sel.xpath("//div[@class='m-music-list-desc']/text()").extract()
           if len(tmp_album_desc) == 0:
               logger.warning("<parse_album>, item:{0}".format(item))
           else:
               item['album_desc'] = tmp_album_desc[0]

           tmp_album_soundlist_str = sel.xpath("//script[contains(text(),'eval')]/text()").extract()
           if len(tmp_album_soundlist_str) == 0:
               logger.error("<parse_album>, item:{0}".format(item))
               return  # this is mandatory
           else:
               item['album_sound_list_str'] = tmp_album_soundlist_str[0]
           yield item
        except Exception as e:
            logger.error("!! EXCEPT in <parse_album>, err:{0}| item:{1}".format(e,item))


# -*-coding: utf-8 -*-
__author__ = "liushan"

import sys, os
from scrapy.spiders import Spider

from scrapy.http import Request

from scrapy.selector import Selector
from lxwc.items import LxwcVideoItem

import re

import logging
logger = logging.getLogger(__name__)

album_url_base = "http://www.lxwc.com.cn/"

#method 1: os.environ["http_proxy"] = "http://1**.***.**.**:80"
#method 2: modify code: middlewares.py

class LxwcVideoSpider(Spider):
    name = "LxwcVideo"
    allowed_domains = ["lxwc.com.cn"]
    start_urls = [
        "http://www.lxwc.com.cn/tv/"
    ]

    def parse(self,response):
        items = []
        sel = Selector(response)

        cate_url_l1 = "http://www.lxwc.com.cn/tv/"
        cate_title_l1 = "视频"

        try:
            cate_urls_l2 = sel.xpath("//div[@class='nav']/ul/li/a/@href").extract()
            cate_titles_l2 = sel.xpath("//div[@class='nav']/ul/li/a/text()").extract()
            cate_urls_l2 = cate_urls_l2[1:]
            cate_titles_l2 = cate_titles_l2[1:]
            cate_urls_l2 = [ album_url_base+x for x in cate_urls_l2 ]

            if len(cate_urls_l2) == 0:
                logger.warning("!!EXCEPT in <parse>: cate_urls_l2 is NULL")
                return
            for i in range(0,len(cate_urls_l2)):
                item = LxwcVideoItem()
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
                    item = LxwcVideoItem()
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
            album_urls = sel.xpath("//li[@class='tvlist1']/h3/a/@href").extract()
            album_titles = sel.xpath("//li[@class='tvlist1']/h3/a/text()").extract()
            if len(album_urls) == 0:
                logger.warning("!!EXCEPT in <parse_url_l3>: album_urls is NULL")
                return
            for i in range(0,len(album_urls)):
                if_belong = album_urls[i].endswith('html')
                if (if_belong):
                    item = LxwcVideoItem()
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

    def get_iframe(self,sel,item):
        """
        <case>: youku
        <url>: http://www.lxwc.com.cn/wucai-1235159-1.html
        <content>:
          <div id="video_content">
<iframe width=900 height=680 src="misc.php?mod=play&amp;id=XODQ1NTIwMzIw" frameborder=0 scrolling="no" allowfullscreen style="background: #1f1f1f;"></iframe>
         </div>
        <target>: to get: id=XODQ1NTIwMzIw
        ======================
        <case>: iqiyi
        <url>: http://www.lxwc.com.cn/wucai-1235272-1.html
        <content>:
             videoc.innerHTML = '<iframe width=900 height=680 src="http://dispatcher.video.qiyi.com/common/shareplayer.html?vid=008a35aeef2ac9ca473d0006c4d9f746&amp;tvId=363850000&amp;coop=coop_179_lxwc&amp;cid=qc_105129_300586&amp;bd=1&amp;autoPlay=1&amp;fullscreen=1" frameborder=0 allowfullscreen style="background: #1f1f1f;"></iframe>';
        <target>: to get <iframe></iframe>
        """

        try:
            myiframe = None
            ykFixed = "<iframe height=250 width=250 src='http://player.youku.com/embed/{0}' frameborder=0 'allowfullscreen'></iframe>"
            iqiyiFixed = "<iframe width=250 height=250 src=\"http://dispatcher.video.qiyi.com/common/shareplayer.html?vid={0}&tvId={1}\" allowfullscreen=\"True\"></iframe>"

            video_content = sel.xpath("//div[@id='video_content']").extract()
            logger.debug("video_content is:{0} | item:{1}".format(video_content,item))

            if len(video_content) != 0:
                iframeStr = video_content[0]

                matchObj = re.search("iframe",iframeStr)
                if matchObj is not None:
                    vsource = "youku"
                    iframeStr_new = iframeStr[matchObj.span()[0]:]

                    matchObj = re.search("id=",iframeStr_new)
                    startPos = matchObj.span()[1]
                    matchObj2 = re.search("\"",iframeStr_new[startPos:])
                    endPos = matchObj2.span()[0] + startPos
                    ykID = iframeStr_new[startPos:endPos]
                    myiframe = ykFixed.format(ykID)
                else:
                    vsource = "iqiyi"
                    video_content = sel.xpath("//script[not(@type or @src)]/text()").extract()
                    logger.debug("video_content is:{0} | item:{1}".format(video_content,item))
                    if len(video_content) != 0:
                        for each in video_content:
                            matchObj = re.search("iframe",each)
                            if matchObj is not None:
                                logger.debug("each:{0}".format(each))
                                tmpStr = each[matchObj.span()[1]:]
                                #vid=92492de11589fc6a95f7fe688de32cb8&amp;tvId=683682800&amp
                                matchObj = re.search("vid=",tmpStr)
                                startPos4vid = matchObj.span()[1]

                                matchObj = re.search("&amp",tmpStr[startPos4vid:])
                                endPos4vid = matchObj.span()[0] + startPos4vid
                                vid = tmpStr[startPos4vid:endPos4vid]

                                matchObj = re.search("tvId=",tmpStr)
                                startPos4tvId = matchObj.span()[1]
                                matchObj = re.search("&amp",tmpStr[startPos4tvId:])
                                endPos4tvId = matchObj.span()[0] + startPos4tvId
                                tvId = tmpStr[startPos4tvId:endPos4tvId]

                                myiframe = iqiyiFixed.format(vid,tvId)
                                break

        except Exception as e:
            logger.error("!! EXCEPT in <get_iframe>,err:{0}| item:{1}".format(e,item))
        finally:
            if myiframe is None:
                logger.warning("!! myiframe is None. item:{0}".format(item))
            return myiframe

    def parse_album(self,response):
        sel = Selector(response)
        item_3 = response.meta["item_3"]
        items = []

        #print("! sliu parse_album ! {0}".format(item_3['cate_title_l2']))
        #NOTE: there are at least 3 cases for this level page:
        # <case1>: item_3['album_url'] is already a final link
        #   ex: http://www.lxwc.com.cn/wucai-1235520-1.html
        #       http://www.lxwc.com.cn/wucai-1235484-1.html
        # <case2>: 播放列表，无翻页TAB
        #   ex: http://www.lxwc.com.cn/wucai-1235650-1.html
        #       http://www.lxwc.com.cn/wucai-1238412-1.html
        # <case3>: 播放列表， 有TAB
        #   ex: http://www.lxwc.com.cn/wucai-1233407-1.html
        #       http://www.lxwc.com.cn/wucai-1237975-1.html
        # <case X?>

        ####!!!!DEBUG !!!!!
        #if item_3['cate_title_l2'] != "法语视频":
        #    return
        #### DEBUG DONE ###

        try:
            tmplist = sel.xpath("//div[@class='videoposter']").extract()
            album_info_img = tmplist[0] if len(tmplist)!=0 else None
            tmplist = sel.xpath("//div[@class='videobaseinfo']").extract()
            album_info_baseinfo = tmplist[0] if len(tmplist)!=0 else None
            tmplist = sel.xpath("//div[@class='videodesc']").extract()
            album_info_desc = tmplist[0] if len(tmplist)!=0 else None
#            album_src_titles = sel.xpath("//div[@class='episode-box']/ul/li/a/text()").extract()
#            album_src_urls = sel.xpath("//div[@class='episode-box']/ul/li/a/@href").extract()
            album_src_titles = sel.xpath("//ul[@class='xl episoden e3 cl']/li/a/text()").extract()
            album_src_urls = sel.xpath("//ul[@class='xl episoden e3 cl']/li/a/@href").extract()

            bflbStr = sel.xpath("//h3[@class='episode-list-title']").extract()
            if len(bflbStr) == 0:  #case1: no bflb
                album_info_iframe = self.get_iframe(sel,item_3)
                item_3['album_src_title'] = item_3['album_title']
                item_3['album_info_img'] = album_info_img
                item_3['album_info_baseinfo'] = album_info_baseinfo
                item_3['album_info_desc'] = album_info_desc
                item_3['album_src_iframe'] = album_info_iframe
                yield item_3
            else:
                if len(album_src_urls) == 0:
                    logger.error("!! ERROR in <parse_album>,err:{0}| item:{1}".format(e,item_3))
                    return
                #case2 & case3
                for i in range(0,len(album_src_urls)):
                    item = LxwcVideoItem()
                    item['cate_title_l1'] = item_3['cate_title_l1']
                    item['cate_url_l1'] = item_3['cate_url_l1']
                    item['cate_title_l2'] = item_3['cate_title_l2']
                    item['cate_url_l2'] = item_3['cate_url_l2']
                    item['cate_title_l3'] = item_3['cate_title_l3']
                    item['cate_url_l3'] = item_3['cate_url_l3']
                    item['album_url'] = item_3['album_url']
                    item['album_title'] = item_3['album_title']
                    item['album_info_img'] = album_info_img
                    item['album_info_baseinfo'] = album_info_baseinfo
                    item['album_info_desc'] = album_info_desc
                    item['album_src_title'] = album_src_titles[i]
                    item['album_src_url'] = album_url_base + album_src_urls[i]
                    items.append(item)

                for item in items:
                    yield Request(url=item['album_src_url'],meta={'item_4':item},callback=self.parse_album_src)
        except Exception as e:
            logger.error("!! EXCEPT in <parse_album>,err:{0}| item:{1}".format(e,item_3))

    def parse_album_src(self,response):
        sel = Selector(response)
        item = response.meta["item_4"]
        try:
            item['album_src_iframe'] = self.get_iframe(sel,item)
        except Exception as e:
            logger.error("!! EXCEPT in <parse_album_src>,err:{0}| item:{1}".format(e,item))
        finally:
            yield item


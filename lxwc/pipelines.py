# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2
import os
import shutil

from lxwc.dbhandler import LxwcThread,LxwcAudioAlbum,LxwcPost,LxwcCategory
from lxwc.items import LxwcVideoItem,LxwcAudioItem,LxwcBookItem
import logging
logger = logging.getLogger(__name__)

class LxwcPipeline(object):
    def process_item(self, item, spider):
        return item

class LxwcPsqlPipeline(object):
    def __init__(self):
        self.categoryInstance = LxwcCategory()
    def process_item(self,item,spider):
        pass
    def getCategoryInfo(self,item):
        cateInfo = None
        try:
            my_cate_slug = self.categoryInstance.getCategorySlug(item)
            my_cate_id = self.categoryInstance.getCategoryId(item)
            my_cate_moderator = self.categoryInstance.getCategoryModerator(item)
            my_cate_moderatorid = self.categoryInstance.getCategoryModeratorId(item)
            cateInfo = {}
            cateInfo['slug'] = my_cate_slug
            cateInfo['id'] = my_cate_id
            cateInfo['moderator'] = my_cate_moderator
            cateInfo['moderatorid'] = my_cate_moderatorid
            for each in cateInfo:
                if cateInfo[each] is None:
                    logger.warning("getCategoryInfo,item:{0}|each:{1}".format(item,each))
                    return None
        except Exception as e:
            logger.error("EXCEPT in getCategoryInfo,err:{0}|item:{1}".format(e,item))
        finally:
            return cateInfo
    def close_spider(self,spider):
        pass

class LxwcAudioPsqlPipeline(LxwcPsqlPipeline):
    def __init__(self):
        super(LxwcAudioPsqlPipeline,self).__init__()
        self.albumInstance = LxwcAudioAlbum()
        self.threadInstance = LxwcThread(L1="AUDIO")
        self.postInstance = LxwcPost(L1="AUDIO")

    def process_item(self,item,spider):
        """insert thread or/and post and album"""
        if item['cate_url_l1'] != "http://www.lxwc.com.cn/audio/":
            return item
        try:
            logger.info("start to process_item for audio item")
            cateInfo = self.getCategoryInfo(item)
            if cateInfo is None:
                logger.warning("cateInfo is none. item:{0}".format(item))
                return item
            threadExistedFlag = self.threadInstance.checkExist(item,cateInfo)
            if threadExistedFlag:
                logger.warning("thread already existed. item:{0}".format(item))
                return item
            flag = self.threadInstance.insert(item,cateInfo)
            if not flag:
                logger.error("insert Thread failure. item:{0}".format(item))
                return item
            else:
                logger.info("insert Thread success. item:{0}".format(item))

            threadId = self.threadInstance.getThreadId(item,cateInfo)
            flag = self.postInstance.insertFirst(item,threadId,cateInfo)
            if not flag:
                logger.error("insert Post failure. item:{0}".format(item))
                return item
            else:
                logger.info("insert Post success. item:{0}".format(item))

            flag = self.albumInstance.insert(item,threadId)
            if not flag:
                logger.error("insert Album failure. item:{0}".format(item))
                return item
            else:
                logger.info("insert Album success. item:{0}".format(item))

        except Exception as e:
            logger.error("!! EXCEPT in audio process_item: {0} |item:{1}".format(e,item))
        finally:
            return item

class LxwcVideoPsqlPipeline(LxwcPsqlPipeline):
    def __init__(self):
        super(LxwcVideoPsqlPipeline,self).__init__()
        self.threadInstance = LxwcThread(L1="VIDEO")
        self.postInstance = LxwcPost(L1="VIDEO")
        self.ThreadAlreadyQueryMap = {}

    def process_item(self,item,spider):
        """insert thread or/and post """
        if item['cate_url_l1'] != "http://www.lxwc.com.cn/tv/":
            return item
        try:
            logger.info("start to process_item for video item")
            cateInfo = self.getCategoryInfo(item)
            if cateInfo is None:
                logger.warning("cateInfo is none. item:{0}".format(item))
                return item

            fingerprint = item['cate_title_l3'] + item['album_title']
            if fingerprint not in self.ThreadAlreadyQueryMap:
                self.ThreadAlreadyQueryMap[fingerprint] = None
                threadId = self.threadInstance.getThreadId(item,cateInfo)
                if threadId is not None:  # by previous spider
                    logger.info("thread already existed, item:{0}".format(item))
                    return item
                else:
                    # insert Thread, insertFirstPost,
                    flag = self.threadInstance.insert(item,cateInfo)
                    if not flag:
                        logger.error("insert Thread failure. item:{0}".format(item))
                        return item
                    else:
                        logger.debug("insert Thread success. item:{0}".format(item))
                        threadId = self.threadInstance.getThreadId(item,cateInfo)
                        self.ThreadAlreadyQueryMap[fingerprint] = threadId
                        flag = self.postInstance.insertFirst(item,threadId,cateInfo)
                        if not flag:
                            logger.error("insert first Post failure. item:{0}".format(item))
                            return item
                        else:
                            logger.info("insert first Post success. item:{0}".format(item))

            else: # fingerprint is in the list
                threadId = self.ThreadAlreadyQueryMap[fingerprint]
                if threadId is not None:
                    flag = self.postInstance.insertReply(item,threadId,cateInfo)
                    if not flag:
                        logger.error("insert reply Post failure. item:{0}".format(item))
                    else:
                        logger.info("insert reply Post success. item:{0}".format(item))
        except Exception as e:
            logger.error("!! EXCEPT in process_item: {0} |item:{1}".format(e,item))
        finally:
            return item

class LxwcBookPsqlPipeline(LxwcPsqlPipeline):
    def __init__(self):
        super(LxwcBookPsqlPipeline,self).__init__()
        self.threadInstance = LxwcThread(L1="BOOK")
        self.postInstance = LxwcPost(L1="BOOK")
    def process_item(self,item,spider):
        if item['cate_url_l1'] != "http://www.lxwc.com.cn/book/":
            return item
        try:
            logger.info("start to process_item for book item")
            cateInfo = self.getCategoryInfo(item)
            if cateInfo is None:
                logger.warning("cateInfo is none. item:{0}".format(item))
                return item
            threadExistedFlag = self.threadInstance.checkExist(item,cateInfo)
            if threadExistedFlag:
                logger.warning("thread already existed. item:{0}".format(item))
                return item
            flag = self.threadInstance.insert(item,cateInfo)
            if not flag:
                logger.error("insert Thread failure. item:{0}".format(item))
                return item
            else:
                logger.info("insert Thread success. item:{0}".format(item))

            threadId = self.threadInstance.getThreadId(item,cateInfo)
            flag = self.postInstance.insertFirst(item,threadId,cateInfo)
            if not flag:
                logger.error("insert Post failure. item:{0}".format(item))
                return item
            else:
                logger.info("insert Post success. item:{0}".format(item))

        except Exception as e:
            logger.error("!! EXCEPT in book process_item: {0} |item:{1}".format(e,item))
        finally:
            return item

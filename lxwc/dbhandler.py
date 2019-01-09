# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2
import os
import random

import logging
logger = logging.getLogger(__name__)

from lxwc.conf import db_conf,DEFAULT_CATE_SLUG,DEFAULT_CATE_MODERATOR,DEFAULT_CATE_SLUG_MAPPING,category_mapping,category_moderators

class PostGreSql(object):
    def __init__(self):
        self.dataBaseName = db_conf['dbName']
        self.userName = db_conf['userName']
        self.password = db_conf['password']
        self.host = db_conf['host']
        self.port = db_conf['port']

        self._conn = self.GetConnect()
        if self._conn:
            self._cur = self._conn.cursor()

    def GetConnect(self):
        conn = False
        try:
            conn = psycopg2.connect(
               database=self.dataBaseName,
               user=self.userName,
               password=self.password,
               host=self.host,
               port=self.port
            )
        except Exception as err:
            logger.error("EXCEPT in GetConnect:{0}".format(e))
        finally:
            return conn

    def ExecQuery(self,sql):
        res = []
        try:
            self._cur.execute(sql)
            res = self._cur.fetchall()
        except Exception as e:
            logger.error("EXCEPT in ExecQuery, err:{0} |sql:{1}".format(e,sql))
        finally:
            logger.info("ExecQuery,sql:{0}".format(sql))
            return res

    def ExecNonQuery(self,sql):
        flag = False
        try:
            self._cur.execute(sql)
            self._conn.commit()
            flag = True
        except Exception as e:
            flag = False
            self._conn.rollback()
            logger.error("EXCEPT in ExecNonQuery, err:{0} |sql:{1}".format(e,sql))
        finally:
            logger.info("ExecNonQuery,sql:{0}".format(sql))
            return flag

    def ExecNonQueryBundle(self,sql_list):
        flag = False
        try:
            for sql in sql_list:
                self._cur.execute(sql)
            self._conn.commit()
            flag = True
        except Exception as e:
            flag = False
            self._conn.rollback()
            logger.error("EXCEPT in ExecNonQueryBundle, err:{0} |sql:{1}".format(e,sql))
        finally:
            logger.info("ExecNonQueryBundle,sql_list:{0}".format(sql_list))
            return flag


class LxwcCategory(object):
    def __init__(self):
        self.dbinst = PostGreSql()

    def getCategorySlug(self,item):
        my_cate_slug = DEFAULT_CATE_SLUG
        try:
            lxwc_url_p = item['cate_url_l3'].split("/")
            if lxwc_url_p[-4] in ["audio","tv","book"]:
                lxwc_cate_slug_l3 = '/'.join([lxwc_url_p[-4],lxwc_url_p[-3],lxwc_url_p[-2]])
                if lxwc_cate_slug_l3 in category_mapping:
                    my_cate_slug = category_mapping[lxwc_cate_slug_l3]
                else:
                    my_cate_slug = DEFAULT_CATE_SLUG_MAPPING[lxwc_url_p[-4]]
        except Exception as e:
            logger.error("EXCEPT in getCategorySlug,err:{0}| item:{1}".format(e,item))
        finally:
            logger.info("getCategorySlug,item:{0}".format(item))
        return my_cate_slug

    def getCategoryId(self,item):
        id = None
        try:
            my_cate_slug = self.getCategorySlug(item)
            sql = "select id from misago_categories_category where slug='{slug}'".format(slug=my_cate_slug)
            res = self.dbinst.ExecQuery(sql)
            id = res[0][0]
        except Exception as e:
            logger.error("EXCEPT in getCategoryId,err:{0} |item:{1}".format(e,item))
        finally:
            logger.info("getCategoryId,item:{0}".format(item))
        return id

    def getCategoryModerator(self,item):
        my_cate_moderator = DEFAULT_CATE_MODERATOR
        try:
            my_cate_slug = self.getCategorySlug(item)
            if my_cate_slug in category_moderators:
                my_cate_moderator = category_moderators[my_cate_slug]
            lxwc_url_p = item['cate_url_l3'].split("/")
            if lxwc_url_p[-4] in ["audio","tv","book"]:
                my_cate_moderator = category_moderators[lxwc_url_p[-4]]
        except Exception as e:
            logger.error("EXCEPT in getCategoryModerator,err:{0}| item:{1}".format(e,item))
        finally:
            logger.info("getCategoryModerator,item:{0}".format(item))
        return my_cate_moderator

    def getCategoryModeratorId(self,item):
        id = None
        try:
            my_cate_moderator = self.getCategoryModerator(item)
            sql = "select id from misago_users_user where username='{username}'".format(username=my_cate_moderator)
            res = self.dbinst.ExecQuery(sql)
            id = res[0][0]
        except Exception as e:
            logger.error("EXCEPT in getCategoryModeratorId,err:{0}| item:{1}".format(e,item))
        finally:
            logger.info("getCategoryModeratorId,item:{0}".format(item))
        return id




sql_thread_part1 = "insert into misago_threads_thread(title,\
slug,\
replies,\
has_events,\
has_poll,\
has_reported_posts,\
has_open_reports,\
has_unapproved_posts,\
has_hidden_posts,\
started_on,\
starter_name,\
starter_slug,\
last_post_is_event,\
last_post_on,\
last_poster_name,\
last_poster_slug,\
weight,\
is_unapproved,\
is_hidden,\
is_closed,\
category_id,\
starter_id,\
last_poster_id,\
best_answer_is_protected,\
viewcount)"

sql_thread_part2 = "values('{thread_name}',\
'{slug}',\
0,\
'f',\
'f',\
'f',\
'f',\
'f',\
'f',\
current_timestamp,\
'{user}',\
'{user}',\
'f',\
current_timestamp,\
'{user}',\
'{user}',\
0,\
'f',\
'f',\
'f',\
{cate_id},\
{user_id},\
{user_id},\
'f',\
0)"


class LxwcThread(object):
    def __init__(self,*args,**kwargs):
        self.dbinst = PostGreSql()

    def checkExist(self,item,cateInfo):
        flag = False
        try:
            title = item['album_title']
            title = title.replace("'","''")
            cate_slug = cateInfo['slug']
            cate_id = cateInfo['id']
            moderator = cateInfo['moderator']
            moderatorid = cateInfo['moderatorid']

            sql = "select count(*) from misago_threads_thread where title='{title}' \
                and starter_name='{user}' and category_id={category_id}".format(title=\
                title,user=moderator,category_id=cate_id)

            reslist = self.dbinst.ExecQuery(sql)

            # reslist is like: [(0,)]
            if len(reslist) != 0 and reslist[0][0] != 0:
                flag = True

        except Exception as e:
            logger.error("Except in LxwcThread.checkExist, err:{0}".format(e))
        finally:
            return flag


    def getThreadId(self,item,cateInfo):
        #title = '英美经典儿歌分级唱（一）'
        id = None
        try:
            title = item['album_title']
            title = title.replace("'","''")
            sql = "select id from misago_threads_thread where title='{title}'".format(title=title)

            reslist = self.dbinst.ExecQuery(sql)
            if len(reslist) != 0:
                id = reslist[0][0]
        except Exception as e:
            logger.error("Except in LxwcThread.getThreadId, err:{0}".format(e))
        finally:
            return id

    def insert(self,item,cateInfo):
        flag = False
        try:
            title = item['album_title']
            title = title.replace("'","''")
            cate_slug = cateInfo['slug']
            cate_id = cateInfo['id']
            moderator = cateInfo['moderator']
            moderatorid = cateInfo['moderatorid']

            sql = sql_thread_part1 + " " + sql_thread_part2.format(thread_name=title,
                                                               slug=cate_slug,
                                                               cate_id=cate_id,
                                                               user=moderator,
                                                               user_id=moderatorid)

            flag = self.dbinst.ExecNonQuery(sql)
        except Exception as e:
            logger.error("Except in LxwcThread.insert, err:{0}".format(e))
        finally:
            return flag


sql_album_part1 = "insert into splayer_album(name,description,sound_from,sound_list,dloadlink,dloadkey,thread_id)"

sql_album_part2 = "values('{name}','{desc}',0,'{sound_list}','{dloadlink}','{dloadkey}',{thread_id})"

class LxwcAudioAlbum(object):
    def __init__(self):
        self.dbinst = PostGreSql()

    def checkExist(self, item, threadId):
        #title = '英美经典儿歌分级唱（一）'
        flag = False
        try:
            title = item['album_title']
            title = title.replace("'","''")
            sql = "select count(*) from splayer_album where name='{title}'".format(title=title)
            reslist = self.dbinst.ExecQuery(sql)
            if len(reslist) != 0 and reslist[0][0] != 0:
                flag = True
        except Exception as e:
            logger.error("Except in LxwcAudioAlbum.checkExist, err:{0}".format(e))
        finally:
            return flag


    def insert(self,item,threadId):
        flag = False
        try:
            name = item['album_title']
            name = name.replace("'","''")
            desc = item['album_desc']
            desc = desc.replace("'","''")
            sound_list = item['album_sound_list_str']
            sound_list = sound_list.replace("'","''")
            #dloadlink = item['dloadlink']
            #dloadkey = item['dloadkey']
            dloadlink = 'http://192.168.1.118/dloadlink'
            dloadkey = '1234'
            sql = sql_album_part1 + " " + sql_album_part2.format(name=name,desc=desc,sound_list=sound_list,dloadlink=dloadlink,dloadkey=dloadkey,thread_id=threadId)
            #print("album insert sql is:",sql)
            flag = self.dbinst.ExecNonQuery(sql)
        except Exception as e:
            logger.error("Except in LxwcAudioAlbum.insert, err:{0}".format(e))
        finally:
            return flag


sql_post_part1 = "insert into misago_threads_post(poster_name,\
original,\
parsed,\
posted_on,\
updated_on,\
has_reports,\
has_open_reports,\
is_unapproved,\
is_hidden,\
is_protected,\
category_id,\
poster_id,\
is_event,\
likes,\
thread_id,\
checksum,\
edits,\
hidden_on,\
search_vector)"

sql_post_part2 = "values('{poster_name}','{original}','{parsed}',current_timestamp,current_timestamp,'f','f','f','f','f',{cate_id},{poster_id},'f',0,{thread_id},'{checksum}',0,current_timestamp,'{search_vector}')"

class LxwcPost(object):
    def __init__(self,*args,**kwargs):
        self.L1 = kwargs.get("L1")  # L1 is: AUDIO | VIDEO
        self.dbinst = PostGreSql()

    def checkExist(self,item,threadId):
        flag = False
        try:
            title = item['album_title']
            title = title.replace("'","''")
            sql = "select count(*) from misago_threads_post where original='{title}'".format(title=title)
            reslist = self.dbinst.ExecQuery(sql)
            if len(reslist) != 0 and reslist[0][0] != 0:
                flag = True
        except Exception as e:
            logger.error("Except in LxwcPost.checkExist, err:{0}".format(e))
        finally:
            return flag

    def getPostId(self,item,threadId):
        id = None
        try:
            title = item['album_title']
            title = title.replace("'","''")
            sql = "select id from misago_threads_post where original='{title}'".format(title=title)
            #print("sql is:",sql)
            reslist = self.dbinst.ExecQuery(sql)
            #print("res is:",res)
            if len(reslist) != 0:
                id = reslist[0][0]
        except Exception as e:
            logger.error("Except in LxwcPost.getPostId, err:{0}".format(e))
        finally:
            return id

    def insert(self,needList,item,threadId,cateInfo):
        flag = False
        try:
            title = ""
            for each in needList:
                if item.get(each) is not None:
                    if each == 'album_src_iframe':
                        title = title + "<br>"
                    title = title + item[each]
            title = title.replace("'","''")  # psql rule for ''
            if title == "":
                title = "正在更新中..."
            cate_id = cateInfo['id']
            moderator = cateInfo['moderator']
            moderatorid = cateInfo['moderatorid']
            # HD for the moment, exec python manage.py <updatep**> in shell cmd later
            checksum = '2d4274219532a661511ad78ee96843627a3a6db99d92e8c24c99cd0eb0e4a1ce'
            search_vector = 'abcd'
            sql = sql_post_part1 + " " + sql_post_part2.format(poster_name=moderator,original=title,parsed=title,cate_id=cate_id,poster_id=moderatorid,thread_id=threadId,checksum=checksum,search_vector=search_vector)
            flag = self.dbinst.ExecNonQuery(sql)
        except Exception as e:
            logger.error("Except in LxwcPost.insert, err:{0}".format(e))
        finally:
            return flag

    def insertFirst(self,item,threadId,cateInfo):
        """
        insert First Post for a thread.
        handle different for AUDIO and VIDEO
        """
        needList = []
        if self.L1 == "VIDEO":
            needList = ['album_info_img','album_info_baseinfo','album_info_desc']
            flag = self.insert(needList,item,threadId,cateInfo)
            if flag:
                return self.insertReply(item,threadId,cateInfo)
            else:
                return False
        elif self.L1 == "AUDIO":
            needList = ['album_title','album_desc']
        elif self.L1 == "BOOK":
            needList = ['book_cover_img','book_base_info','book_introduction','book_detail_url']
        else:
            pass
        return self.insert(needList,item,threadId,cateInfo)

    def insertReply(self,item,threadId,cateInfo):
        needList = ['album_src_title','album_src_iframe']
        return self.insert(needList,item,threadId,cateInfo)

    def sort_thread(self,thread_id,log=False):
        """per threadId"""
        try:
            sql = "select count(*) from misago_threads_post where thread_id={0}".format(thread_id)
            reslist = self.dbinst.ExecQuery(sql)
            num = reslist[0][0]
            if num > 2:
                if log == True:
                    print("thread_id:{0}, post num:{1}".format(thread_id,num))
                sql = "select original from misago_threads_post where thread_id={0} order by original".format(thread_id)
                original_list_tmp = self.dbinst.ExecQuery(sql)
                original_list = []
                for original in original_list_tmp:
                    if original[0].strip().startswith("<div"):
                        original_list.insert(0,original)
                    else:
                        original_list.append(original)                

                sql = "select id from misago_threads_post where thread_id={0} order by id".format(thread_id)
                postid_list = self.dbinst.ExecQuery(sql)
             
                #print("original_list is:\n {0}".format(original_list))
                #print("postid_list is:\n {0}".format(postid_list))

                sql_list = []
                for index,elem in enumerate(original_list):
                    tmpint = 1000000
                    id = postid_list[index][0] + tmpint
                    original = elem[0]
                    original = original.replace("'","''")
                    sql = "update misago_threads_post set id={0} where original='{1}' and thread_id={2}".format(id,original,thread_id)
                    sql_list.append(sql)
                for index,elem in enumerate(original_list):
                    tmpint = 0
                    id = postid_list[index][0] + tmpint
                    original = elem[0]
                    original = original.replace("'","''")
                    sql = "update misago_threads_post set id={0} where original='{1}' and thread_id={2}".format(id,original,thread_id)
                    sql_list.append(sql)
                flag = self.dbinst.ExecNonQueryBundle(sql_list)
                if not flag:
                    #logger.error("Error in LxwcPost.sort_thread,thread_id:{0}".format(thread_id))
                    print("Error in LxwcPost.sort_thread,thread_id:{0}".format(thread_id))
        except Exception as e:
            logger.error("Except in LxwcPost.sort_thread,thread_id:{0}|err:{1}".format(thread_id,e))
            print("Except in LxwcPost.sort_thread,thread_id:{0}|err:{1}".format(thread_id,e))


    def sort(self):
        """for each threadID,sort the post under it, executed at the end of the LxwcVideoSpider"""
        # get all thread_ids from post
        count = 0
        sql = "select distinct thread_id from misago_threads_post order by thread_id"
        reslist = self.dbinst.ExecQuery(sql)
        if len(reslist) !=0 and reslist[0][0] !=0: 
            #print("reslist:{0}".format(reslist))
            for thread in reslist:
                count += 1
                if count%20 == 0:
                    print("{0} treads are sorted.".format(count))
                thread_id = thread[0]
                self.sort_thread(thread_id)

    def updtimestamp(self):
        """update timestamp for all posts"""
        count = 0
        sql = "select distinct thread_id from misago_threads_post order by thread_id"
        reslist = self.dbinst.ExecQuery(sql)
        if len(reslist) !=0 and reslist[0][0] !=0:
            #print("reslist:{0}".format(reslist))
            for thread in reslist:
                count += 1
                if count%20 == 0:
                    print("{0} treads are done.".format(count))
                thread_id = thread[0]
                self.updtimestamp_thread(thread_id,"PERTHREADID")        

    def updtimestamp_backday(self,thread_id,strategy):
        """ back go days"""
        days = 10 # hard-code
        if strategy == "PERTHREADID":
            days = thread_id%100
        sql_list = []
        upd_sql_tmp_thread = "update misago_threads_thread set last_post_on=(last_post_on- interval '{day} D') where id={threadid};"
        upd_sql_tmp_post = "update misago_threads_post set posted_on=(posted_on- interval '{day} D') where thread_id={threadid};"
        try:
            sql = upd_sql_tmp_thread.format(threadid=thread_id,day=days)
            sql_list.append(sql)
            sql = upd_sql_tmp_post.format(threadid=thread_id,day=days)
            sql_list.append(sql)
            flag = self.dbinst.ExecNonQueryBundle(sql_list)
        except Exception as e:
            logger.error("Except in LxwcPost.updtimestamp_backday,thread_id:{0}|err:{1}".format(thread_id,e))

    def updtimestamp_backmin(self,thread_id):
        """adjust mins for post of the thread"""
        sql_list = []
        upd_sql_tmp_min = "update misago_threads_post set posted_on=(posted_on+ interval '{min} M') where id={postid};"
        try:
            sql = "select id,posted_on from misago_threads_post where thread_id={0}".format(thread_id)
            reslist = self.dbinst.ExecQuery(sql)
            posts = len(reslist)
            if posts > 2:
                #p0_posted_on = reslist[0][1]
                interval = 0
                for index in range(1,posts):
                    post_id = reslist[index][0]
                    min = random.randint(1,2)
                    interval = interval + min
                    sql = upd_sql_tmp_min.format(min=interval,postid=post_id)
                    sql_list.append(sql)
                flag = self.dbinst.ExecNonQueryBundle(sql_list)
        except Exception as e:
            logger.error("Except in LxwcPost.updtimestamp_backmin,thread_id:{0}|err:{1}".format(thread_id,e))

    def updtimestamp_thread(self,thread_id,strategy="HARD_CODE"):
        self.updtimestamp_backday(thread_id,strategy)
        self.updtimestamp_backmin(thread_id)        

    def updtimestamp_thread_1(self,thread_id):
        sql_list = []
        upd_sql_tmp_thread = "update misago_threads_thread set last_post_on=(last_post_on- interval '{day} D') where id={threadid};"
        upd_sql_tmp_day = "update misago_threads_post set posted_on=(posted_on- interval '{day} D') where thread_id={threadid};"
        upd_sql_tmp_min = "update misago_threads_post set posted_on=(posted_on+ interval '{min} M') where id={postid};"
        try:
            sql = "select id from misago_threads_post where thread_id={0}".format(thread_id)
            reslist = self.dbinst.ExecQuery(sql)
            #print(reslist)
            days = thread_id%100
            sql = upd_sql_tmp_day.format(day=days,threadid=thread_id)
            sql_list.append(sql)
            sql = upd_sql_tmp_thread.format(day=days,threadid=thread_id)
            sql_list.append(sql)
            for each in reslist:
                postid = each[0]
                mins = postid%1000
                sql = upd_sql_tmp_min.format(min=mins,postid=postid)
                sql_list.append(sql)    
                #print(postid)
            flag = self.dbinst.ExecNonQueryBundle(sql_list)
        except Exception as e:
            logger.error("Except in LxwcPost.sort_thread,thread_id:{0}|err:{1}".format(thread_id,e))


if __name__ == '__main__':
    LOG_FILE = "mySpider.log"
    LOG_LEVEL = "WARNING"
    import sys
    if len(sys.argv) < 3:
        print("!!format: python dbtools.py dbsort <all|threadid>")
        print(" <all for all threadid>")
        print("************")
        print(" python dbtools.py updtimestamp <all|threadid>")
        print(" python dbtools.py backday threadid")
        print(" python dbtools.py backmin threadid") 
        print("  strategy: for each thread: back_day=threadid/100 dack_min=postid/1000")
        sys.exit()

    if sys.argv[1] == "dbsort": 
        if sys.argv[2] != "all" and sys.argv[2].isdigit() != True:
            sys.exit()
        myobj = LxwcPost("VIDEO")
        if sys.argv[2] == "all":
            print("start to sort:(takes long to be done...)")
            myobj.sort()
        else:
            tid = int(sys.argv[2])
            print("start to handle threadid:",tid)
            myobj.sort_thread(tid,True)
        print("sort finished")

    if sys.argv[1] == "updtimestamp":
        if sys.argv[2] != "all" and sys.argv[2].isdigit() != True:
            sys.exit()
        myobj = LxwcPost("VIDEO")
        if sys.argv[2] == "all":
            print("start to updtimestamp...")
            myobj.updtimestamp()
        else:
            tid = int(sys.argv[2])
            print("start to handle threadid:",tid)
            myobj.updtimestamp_thread(tid)
        print("updtimestamp finished")
    if sys.argv[1] == "backday":
        if sys.argv[2].isdigit() != True:
            sys.exit()
        myobj = LxwcPost("VIDEO")
        tid = int(sys.argv[2])
        print("start to handle threadid:",tid)
        myobj.updtimestamp_backday(tid,"HARD_CODE")
    if sys.argv[1] == "backmin":
        if sys.argv[2].isdigit() != True:
            sys.exit()
        myobj = LxwcPost("VIDEO")
        tid = int(sys.argv[2])
        print("start to handle threadid:",tid)
        myobj.updtimestamp_backmin(tid)


    print("please run below command:\n")
    print("  python manage.py updatepostschecksums")
    print("  python manage.py rebuildpostssearch")

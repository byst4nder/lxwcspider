#project configuration here

proxy = "http://***.***.***.***:80"
db_conf = {
    "dbName": "db0000",
    "userName": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}
DEFAULT_CATE_SLUG = "first-category"
DEFAULT_CATE_MODERATOR = "admin"
category_moderators = {
    "audio":"xiaoyin",
    "tv":"xiaoshi",
    "book":"xiaoyue",
    "download":"xiaoxia",
    "chat":"xiaoliao"
}
DEFAULT_CATE_SLUG_MAPPING = {
    "audio":"audio",
    "tv":"video",
    "book":"book"
}
lxwc_categories = {
    "audio":[
                "audio/yw/egty",
                "audio/yw/hb",
                "audio/yw/qlsh",
                "audio/yw/chzh",
                "audio/yw/ywzhzh",
                "audio/yw/thgsh",
                "audio/yw/fjdw",
                "audio/yw/0to6",
                "audio/yw/6up",
                "audio/yw/etdy",
                "audio/yw/zrpd",
                "audio/yw/ybjc",
                "audio/yw/bbcetgb",
                "audio/zhw/gjhj",
                "audio/zhw/thgsh",
                "audio/zhw/guoxue",
                "audio/zhw/lsh",
                "audio/zhw/zrkx",
                "audio/zhw/xiaoxue",
                "audio/zhw/jkxl",
                "audio/fy/fyeg",
                "audio/fy/fygsh",
                "audio/fy/fydh"
        ],
    "tv":[
                "tv/en/yyqm",
                "tv/en/ensong",
                "tv/en/cartoon_6",
                "tv/en/carton",
                "tv/en/film",
                "tv/en/etyydsj",
                "tv/en/ybyyjx",
                "tv/en/phonics",
                "tv/en/gpch",
                "tv/en/huiben",
                "tv/cn/zhfilm",
                "tv/cn/zhcartoon",
                "tv/cn/chsong",
                "tv/cn/guoxue",
                "tv/cn/jiaoyu",
                "tv/cn/sqgsh",
                "tv/cn/etj",
                "tv/cn/etcy",
                "tv/cn/jlp",
                "tv/cn/shgjy",
                "tv/fysp/erge",
                "tv/fysp/gushi",
                "tv/fysp/dhp",
                "tv/fysp/dy"
          ],
        "book":[
                "book/yw/ssfk",
                "book/yw/pictbook",
                "book/yw/zjs",
                "book/yw/meiwen",
                "book/yw/yuanzhu",
                "book/yw/qlsh",
                "book/zhw/zhwgsh",
                "book/fawen/fygsh"
          ],
        "download":[],
        "chat":[]
}

category_mapping = {
		    "audio/yw/egty":"yyerge",
                    "audio/yw/hb":"yyhuiben",
                    "audio/yw/qlsh":"yyqlshu",
                    "audio/yw/chzh":"yychuzhang",
                    "audio/yw/ywzhzh":"yyzhongzhang",
                    "audio/yw/thgsh":"yythgs",
                    "audio/yw/fjdw":"yyfjdw",
                    "audio/yw/0to6":"2to6cartoon",
                    "audio/yw/6up":"6upcartoon",
                    "audio/yw/etdy":"yydianying",
                    "audio/yw/zrpd":"yyphonics",
                    "audio/yw/ybjc":"yyybjc",
                    "audio/yw/bbcetgb":"bbcbroadcast",
                    "audio/zhw/gjhj":"zhwgwetgs",
                    "audio/zhw/thgsh":"zhwgnycgs",
                    "audio/zhw/guoxue":"zhwjdgx",
                    "audio/zhw/lsh":"zhwlsdl",
                    "audio/zhw/zrkx":"zhwzrkx",
                    "audio/zhw/xiaoxue":"zhwxiaoxue",
                    "audio/zhw/jkxl":"zhwxgxl",
                    "audio/fy/fyeg":"frerge",
                    "audio/fy/fygsh":"frgushi",
                    "audio/fy/fydh":"frdonghua",

                    "tv/en/yyqm":"yyvqimeng",
                    "tv/en/ensong":"yyverge",
                    "tv/en/cartoon_6":"yyvcartoonup",
                    "tv/en/carton":"yyvcartoon",
                    "tv/en/film":"yyvfilm",
                    "tv/en/etyydsj":"yyvdsj",
                    "tv/en/ybyyjx":"yyvjx",
                    "tv/en/phonics":"yyvphonics",
                    "tv/en/gpch":"yyvfrequency",
                    "tv/en/huiben":"yyvhuiben",
                    "tv/cn/zhfilm":"cnvmovie",
                    "tv/cn/zhcartoon":"cnvcartoon",
                    "tv/cn/chsong":"cnverge",
                    "tv/cn/guoxue":"cnvguoxue",
                    "tv/cn/jiaoyu":"cnvjiaoyu",
                    "tv/cn/sqgsh":"cnvgushi",
                    "tv/cn/etj":"cnvertj",
                    "tv/cn/etcy":"cnvcaiyi",
                    "tv/cn/jlp":"cnvxiaoxue",
                    "tv/cn/shgjy":"cnvzjjz",
                    "tv/fysp/erge":"frvsongs",
                    "tv/fysp/gushi":"frvstory",
                    "tv/fysp/dhp":"frvcartoon",
                    "tv/fysp/dy":"frvmovie",

                    "book/yw/ssfk":"yybstory",
                    "book/yw/pictbook":"yybhuiben",
                    "book/yw/zjs":"yybchuzh",
                    "book/yw/meiwen":"yybzhongzh",
                    "book/yw/yuanzhu":"yybyuanzhu",
                    "book/yw/qlsh":"yybqlshu",
                    "book/zhw/zhwgsh":"cnbgushi",
                    "book/fawen/fygsh":"xyzbgushi"
}

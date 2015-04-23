#coding=utf-8

import urllib2
import re
import time
import json
import sys 
from spider_conf import SpiderConf
from parseHtml import ParseHtml
from pyquery import PyQuery as pq
import MySQLdb
import hashlib
reload(sys)
sys.setdefaultencoding('utf-8')


def create_lvyou_url(web_type,web_base):
    url_map = []
    if web_type == 'jkcf':
        web_select = spiderConf.getUrlBase(web_type)
        web_from = web_select['from'] 
        for from_id,from_name in web_from.items():
            web_to = web_select['to']
            for to_id,to_name in web_to.items():
                for i in range(1,4):
                    temp_url = web_base['url']+'tours-listing-'+from_id+'-'+to_id+'-'+'%e5%85%a8%e9%83%a8-0-p-'+str(i)+'.html'
                    detail = {}
                    detail['url'] = temp_url
                    detail['from'] = from_name
                    detail['to'] = to_name
                    detail['type'] = web_type 
                    url_map.append(detail)

    if web_type == "qy":
        web_select = spiderConf.getUrlBase(web_type)
        web_from = web_select['from'] 
        for from_id,from_name in web_from.items():
            web_to = web_select['to']
            for to_id,to_name in web_to.items():
                for i in range(1,4):
                    temp_url = web_base['url']+"/"+from_id+'_0_'+to_id+'/page'+str(i)
                    detail = {}
                    detail['url'] = temp_url
                    detail['from'] = from_name
                    detail['to'] = to_name
                    detail['type'] = web_type
                    url_map.append(detail)
    if web_type == "qn":
        web_select = spiderConf.getUrlBase(web_type)
        web_from = web_select['from'] 
        for from_id,from_name in web_from.items():
            web_to = web_select['to']
            for to_id,to_name in web_to.items():
                for i in range(1,2):
                    temp_url = web_base['url']+"?page=0&displaynum=60&type=%E8%87%AA%E7%94%B1%E8%A1%8C&dep="+from_id+'&arr='+to_id
                    detail = {}
                    detail['url'] = temp_url
                    detail['from'] = from_name
                    detail['to'] = to_name
                    detail['type'] = web_type
                    url_map.append(detail)
    if web_type == "alx":
        web_select = spiderConf.getUrlBase(web_type)
        web_from = web_select['from'] 
        for from_id,from_name in web_from.items():
            web_to = web_select['to']
            for to_id,to_name in web_to.items():
                for i in range(1,4):
                    temp_url = web_base['url']+"/list?ptype=1&wtype=1&tdate=a0&price_range=0&city="+from_id+'&place='+to_id+'&p='+str(i)
                    detail = {}
                    detail['url'] = temp_url
                    detail['from'] = from_name
                    detail['to'] = to_name
                    detail['type'] = web_type
                    url_map.append(detail)
    if web_type == "llh":
        web_select = spiderConf.getUrlBase(web_type)
        web_from = web_select['from'] 
        for from_id,from_name in web_from.items():
            web_to = web_select['to']
            for to_id,to_name in web_to.items():
                for i in range(1,4):
                    temp_url = web_base['url']+"Search?/?type=6&GoCity="+from_id+'&target='+to_id+'&pageNumber='+str(i)
                    detail = {}
                    detail['url'] = temp_url
                    detail['from'] = from_name
                    detail['to'] = to_name
                    detail['type'] = web_type
                    url_map.append(detail)
            
    return url_map

#main() is here
#TODO: get seed url list
spiderConf = SpiderConf()
parseHtml  = ParseHtml()
run = sys.argv[1]
print run
web_site = spiderConf.get_web_site_conf()
for web in web_site:
    if web != run:
        continue
    urls = create_lvyou_url(web,web_site[web])
    for item in urls:
        parseHtml.requestUrlAndInertDb(item);
exit()


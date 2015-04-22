#encoding:utf-8

import urllib2
import time
import json
import MySQLdb
from MySQLdb import escape_string
import urlparse
import hashlib
import re
from pyquery import PyQuery as pq
class ParseHtml:

    DB_CONN = MySQLdb.connect(host="10.121.95.81",user="root",passwd="qihoo@360@qihoo",db="lvyou",charset='utf8')
    website_list = {'qy':'穷游','jkcf':'即刻出发','qn':'去哪网','alx':'爱旅游','llh':'来来会'}

    def requestUrlAndInertDb(self,item):
        type = item['type']
        text = self.request_url(item['url']) 

        if type == "jkcf":
            self.parseJkcf(text,item)
        if type == "qy":
            self.parseQy(text,item)
        if type == "qn":
            self.parseQn(text,item)
        if type == "alx":
            self.parseAlx(text,item)
        if type == "llh":
            self.parseLlh(text,item)
        return ''

    #from_type 为出发大分类，供自己用
    #wfrom 为产品出发城市
    def insertToDb(self,url,h5_url,day,wfrom,from_type,wto,type,price,price_range,title,sub_title,fly_company,hotal,go_date,base_img,product_recommend,product_know,product_price_detail='',product_cancel_detail='',special_detail='',date_detail=''):
       # print "a:"+product_recommend
       # print "b:"+product_price_detail
       # print "c:"+product_know
       # print "d:"+product_cancel_detail 
       # print "e:"+special_detail
       # print "f:"+date_detail
       # print "g:"+fly_company
       # print "h:"+hotal
       # print "i:"+base_img
       # print "j:"+sub_title
       # print "k:"+title
       # print "m:"+price
       # print "n:"+price_range

        conn = self.connectDb()
        web_name = self.website_list[type]
        cursor =conn.cursor()
        m = hashlib.md5()
        m.update(url)
        md5_url = m.hexdigest()
        sql ="select * from baicai_content where md5_url = '"+ md5_url+"'"
        cursor.execute(sql)
        row=cursor.fetchone()
        t = time.localtime()
        time_now = time.strftime("%Y-%m-%d %H:%M:%S",t)
        if row == None:
            #params = (web_name,type,url,md5_url,h5_url,price,price_range,day,wfrom,from_type,wto,title,sub_title,escape_string(fly_company),escape_string(hotal),escape_string(go_date),escape_string(date_detail),escape_string(base_img),escape_string(product_recommend),escape_string(product_know),'',escape_string(product_price_detail),escape_string(product_cancel_detail),escape_string(special_detail),time_now,time_now)
            #sql = "insert into baicai_content (web_name,web_type,url,md5_url,h5_url,price,price_range,day,wfrom,from_type,wto,title,sub_title,fly_company,hotal,go_date,date_detail,base_img,hot_recommend,product_know,product_content,product_price_detail,product_cancel_detail,special_detail,create_time,update_time) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
            sql = "insert into baicai_content (web_name,web_type,url,md5_url,h5_url,price,price_range,day,wfrom,from_type,wto,title,sub_title,fly_company,hotal,go_date,date_detail,base_img,hot_recommend,product_know,product_content,product_price_detail,product_cancel_detail,special_detail,create_time,update_time) values ('"+web_name+"','"+type+"','"+url+"','"+md5_url+"','"+h5_url+"','"+price+"','"+price_range+"','"+day+"','"+wfrom+"','"+from_type+"','"+wto+"','"+title+"','"+sub_title+"','"+escape_string(fly_company)+"','"+escape_string(hotal)+"','"+escape_string(go_date)+"','"+escape_string(date_detail)+"','"+base_img+"','"+escape_string(product_recommend)+"','"+escape_string(product_know)+"','','"+escape_string(product_price_detail)+"','"+escape_string(product_cancel_detail)+"','"+escape_string(special_detail)+"','"+time_now+"','"+time_now+"')"
        else:
            sql = "update baicai_content set h5_url = '"+h5_url+"',price = '"+price+"',price_range='"+price_range+"',day = '"+day+"',title = '" + title + "',sub_title = '" + sub_title +"',fly_company = '" + escape_string(fly_company) + "',hotal = '" + escape_string(hotal) + "',go_date = '" + escape_string(go_date) + "',base_img = '" + base_img + "',hot_recommend='"+escape_string(product_recommend)+"',product_know='"+escape_string(product_know)+"',product_price_detail='"+escape_string(product_price_detail)+"',product_cancel_detail='"+escape_string(product_cancel_detail)+"',special_detail='"+escape_string(special_detail)+"',update_time = '" + time_now + "',date_detail = '"+escape_string(date_detail)+"'  where md5_url = '" + md5_url + "'"
    
        cursor.execute(sql)
        conn.commit()
    
    def request_url(self,url):
        #print url
        request = urllib2.Request(url)
        request.add_header('User-Agent', 'Baiduspider')
        f = urllib2.urlopen(request,timeout=30)
        text = f.read()
        #text = unicode(f.read(),'utf-8')
        time.sleep(1)
        return text

    def connectDb(self , name = "content"):
        if self.DB_CONN != None:
            return self.DB_CONN
        else:
            try:
                self.DB_CONN = MySQLdb.connect(host="10.121.95.81",user="root",passwd="qihoo@360@qihoo",db="lvyou",charset='utf8')
            except:
                print "Could not connect to MySQL server."
                exit()
            return self.DB_CONN

    def parseJkcf(self,text,item):
        price_have_parse = re.compile("费用包含：</strong>(.*?)<strong>费用",re.S|re.M)
        price_nohave_parse = re.compile("<strong>含：</strong>.*?</p>(.*?)</div>",re.S|re.M)
        fly_parse = re.compile("参考航班信息：(.*?)<p style.*?用餐",re.S|re.M)
        product_know_parse = re.compile("预订信息</b>.*?</div>.*?<div class=\"de_int_b\">(.*?)</div>",re.S|re.M)
        text = unicode(text,'utf-8')
        d = pq(text)
        list = d.items(".b_line")
        for i in list:
            flag = i(".bd_tuan").text()
            if flag != u"自由行":
                continue
            title = i(".bd_title").text()
            img = i(".bl_pic").find("img").attr('src')
            sub_title = i(".bd_deta").text()
        
        
            go_date = ""
            if i(".bd_ne01").eq(2).text()[0:4] == u"出团日期":
                go_date = i(".bd_ne02").eq(2).text()
        
            price_range = i(".bd_pr02").text()
            price_range = price_range.strip('￥').replace(' ','')
            price = price_range.strip('￥|起| ')

            h5_url = 'http://wx.jikechufa.com'+i(".bd_pr03").attr("href")
            detail_url = "http://www.jikechufa.com"+i(".bd_pr03").attr("href")
        
            detail_content = self.request_url(h5_url)
            detail_content_detail = unicode(detail_content,'utf-8')
            d = pq(detail_content_detail)

            #产品推荐热点
            product_recommend = d(".b_xidong").html()

            #价格计算
            product_price = {}
            product_price['have'] = ''
            product_price['nohave'] = ''
            price_have = price_have_parse.findall(detail_content)
            if len(price_have):
                product_price['have'] = price_have[0]
            price_nohave = price_nohave_parse.findall(detail_content)
            if len(price_nohave):
                product_price['nohave'] = price_nohave[0]
            product_price_detail = json.dumps(product_price,ensure_ascii=False)
        
            #获取航空信息
            #获取酒店信息
            hotal_list = d(".hotel").items("dt")
            hotal = {}

            dayone = d(".bd_xx").eq(0).items("p")
            fly_content = {}
            j = 1
            hotal_flag = 1
            hotal_content = ''
            for day in dayone:
                if '参考航班信息' in day.text():
                    fly_content[j] = day.text()
                    j = 2
                    continue
                if j >= 2:
                    if '用餐' in day.text():
                        continue
                    if '参考酒店' in day.text():
                        hotal['hotal_name'] = day.text().strip('参考酒店：')
                        hotal_flag =2
                        j = -1
                        continue
                    fly_content[j] = day.text()
                    j += 1
                if hotal_flag == 2:
                    hotal_content += day.text().strip()
                    if day.find("img"):
                        hotal['hotal_img'] = day.find("img").attr("src")

            hotal['hotal_content'] = hotal_content
            fly_list = {}
            k = 1
            for fly in fly_content:
                fly_detail = fly_content[fly].strip("参考航班信息：").strip()
                if fly_detail != '':
                    fly_content_li = {}
                    f = fly_detail.split()
                    if len(f) ==3:
                        fly_content_li['goto']= f[0] 
                        fly_content_li['company'] = f[1]
                        fly_content_li['fly_time']= f[2] +"起飞 "
                        fly_content_li['fly_time'] += f[2] +"到"
                        fly_list[k] = fly_content_li
                        k += 1
            fly_result = {}
            fly_result[1] = fly_list
            hotal = json.dumps(hotal,ensure_ascii=False)
            fly_company = json.dumps(fly_result,ensure_ascii=False)

            #获取订票须知
            detail_content = self.request_url(detail_url)
            detail_content_detail = unicode(detail_content,'utf-8')
            d = pq(detail_content_detail)
            product_know_arr = product_know_parse.findall(detail_content)
            product_know = ''
            if len(product_know_arr):
                product_know_temp = product_know_arr[0].strip()
                if product_know_temp != '':
                    product_know_temp = unicode(product_know_temp,'utf-8')
                    pk = pq(product_know_temp)
                    for li in pk.items("p"):
                        product_know += "<p>"+li.text()+"</p>"

            #获取出发地
            from_city = i(".bd_tex").text()
            day = ''
            day_all = d.items(".de_int1")
            day_num = 0
            for da in day_all:
                day_num += 1
            day = str(day_num)+'天'

            #具体出发日期 和 价格
            date_detail = {}
            month_list = d(".tabBar").items("span")
            month = {}
            mnum = 1
            for mn in month_list:
                month[mnum] = mn.text().replace("年|月",'-')
                mnum += 1
            date_month_list = d("#tab_demo").items(".dat02b")
            h = 1
            mnum = 1
            for date_list in date_month_list:
                for dlist in date_list.items(".dat03"):
                    href = dlist.attr("href")
                    if href:
                        date_fmt = month[mnum]+dlist(".dat04a").text()
                        dnum = dlist(".dat04b").text().replace("位",'')
                        dprice = dlist(".dat04c").text().replace("￥",'') 
                        date_detail[h] =  str(date_fmt)+","+str(dnum)+"人,"+str(dprice)+"元"
                        h += 1
                mnum += 1
            date_detail = json.dumps(date_detail,ensure_ascii=False)

            #产品说明
            special_detail = ''
            #取消订单说明
            product_cancel_detail = ''
            self.insertToDb(detail_url,h5_url,day,from_city,item['from'],item['to'],item['type'],price,price_range,title,sub_title,fly_company,hotal,go_date,img,product_recommend,product_know,product_price_detail,product_cancel_detail,special_detail,date_detail)

    def parseQy(self,text,item):
        price_have_parse = re.compile("价格包含</h5>(.*?)</div>",re.S|re.M)
        price_nohave_parse = re.compile("价格不含</h5>(.*?)</div>",re.S|re.M)
        cancel_parse = re.compile("退款说明</h5>(.*?)</div>",re.S|re.M)
        d = pq(text)
        list = d.items(".lmProductList li")
        for i in list:
            title = i(".fontYaHei").text()
            title = title.replace("立即预订 ","")
            img = i(".tuwen").find('img').attr('data-original')
            sub_title = ''
        
            fly_company = ""
        
            hotal = ""
            go_date = i(".ptwo").text()
        
            price_range = i(".cellprice").text()
            price = price_range.strip('元|起| ')
            detail_url = i("a").attr("href")
        
            url_arr = detail_url.split("/")
            h5_url  = 'http://m.qyer.com/z/deal/'+url_arr[len(url_arr)-1]
            detail_content = self.request_url(detail_url)
            d = pq(detail_content)

            #获取产品亮点
            product_recommend = d(".zkjzld-cont ul li").html()
            if product_recommend == None:
                product_recommend = ''

            #获取订票须知
            try:
                product_know = d(".look-more-unit .look-more-inner").html().strip()
            except:
                product_know = ''
                continue

            #价格计算
            product_price = {}
            product_price['have'] = ''
            product_price['nohave'] = ''
            price_have = price_have_parse.findall(detail_content)
            if len(price_have):
                product_price['have'] = price_have[0].strip()
            price_nohave = price_nohave_parse.findall(detail_content)
            if len(price_nohave):
                product_price['nohave'] = price_nohave[0].strip()
            product_price_detail = json.dumps(product_price,ensure_ascii=False)

            #获取航班信息           
            fly_company_items = d(".triffc").items("tbody")
            fly_company = {}
            i = 1
            for fly in fly_company_items:
                fly_list = {}
                k = 1
                for it in fly.items('tr'):
                    fly_content = {}
                    j = 1
                    for td in it.items("td"):
                        if j == 1 or j == 2:
                            j += 1
                            continue
                        if j == 3:
                            fly_content['day'] = td.text().strip()
                        if j == 4:
                            fly_content['goto']= td.text().strip()
                        if j == 6:
                            fly_content['company'] = td.text().strip()
                        if j == 7:
                            fly_content['fly_time']= td.text().strip() +"起飞 "
                        if j == 8:
                            fly_content['fly_time'] += td.text().strip() +"到"
                        j += 1
                    fly_list[k] = fly_content
                    k += 1 
                fly_company[i] = fly_list
                i += 1
            fly_company = json.dumps(fly_company,ensure_ascii=False)

            #获取酒店信息
            hotal_list = d(".jd-cell-top").eq(0).items("p")
            hotal = {}
            i = 1
            for li in hotal_list:
                if i == 1:
                    hotal['hotal_name'] = li(".jd-name").text()
                    star = li(".star-wrap").find("em")
                    hotal['hotal_star'] = len(star)
                if i == 3:
                    hotal['hotal_addr'] = li.text().strip("地址：") 
                i += 1
            
            hotal['hotal_content'] = '' 
            if d(".jd-cell-bottom").length > 0:
                hotal['hotal_content'] = d(".jd-cell-bottom").eq(0).html().strip()

            hotal['hotal_img'] = '' 
            if d(".jd-cell-pic").length > 0:
                hotal['hotal_img'] = d(".jd-cell-pic").eq(0).find("img").attr("src")
            
            hotal = json.dumps(hotal,ensure_ascii=False)

            #取消订单须知
            product_cancel_detail = ''
            cancel_procudt = cancel_parse.findall(detail_content)
            if len(cancel_procudt):
                product_cancel_detail = cancel_procudt[0].strip()

            #产品说明
            special_detail = ''

            #出发城市
            base_items = d(".detail-cell").items(".no-ico")
            for ba_it in base_items:
                ba_name = ba_it(".p-title").text()
                if ba_name == '出发地：':
                    from_city = ba_it(".p-cont").text()
                if ba_name == '旅行时间：':
                    go_date = ba_it(".p-cont").text()
                    
            #获取旅游天数
            day = ''

            #具体出发日期 和 价格
            date_pid = d(".type-list .active").attr("data-pid")
            day = d(".type-list .active").text()
            date_url = "http://z.qyer.com/index.php?action=ajaxGetCategory&pid="+date_pid
            detail_content = self.request_url(date_url)
            json_de = json.loads(detail_content)
            date_datas = json_de['data']
            date_detail = {}
            i = 1
            for (d_k,k_v) in date_datas.items():
                #print d_k
                for vau in k_v:
                    date_detail[i] = d_k + "-" + str(vau['date']) + ",余"+str(vau['stock'])+"人,"+str(vau['price']) + "人"
                    i = i+1
            date_detail = json.dumps(date_detail,ensure_ascii=False)
            
            self.insertToDb(detail_url,h5_url,day,from_city,item['from'],item['to'],item['type'],price,price_range,title,sub_title,fly_company,hotal,go_date,img,product_recommend,product_know,product_price_detail,product_cancel_detail,special_detail,date_detail)

    def parseAlx(self,text,item):
        price_have_parse = re.compile("<span\s*class=\"product-lit-tit\">费用包含</span>(.*?)<div class=\"line\"></div>",re.S|re.M)
        price_nohave_parse = re.compile("<span\s*class=\"product-lit-tit\">费用不含</span>(.*?)</div>.*?</li>",re.S|re.M)
        product_know_parse = re.compile("重要提示</span>(.*?)<div class=\"line-next\"></div>|重要提示</span>(.*?)</div>.*?</li>",re.S|re.M)
        special_parse = re.compile("友情提示</span>(.*?)</div>.*?</li>",re.S|re.M)
        date_price_parse = re.compile("initProduct(.*?)].*?</script>",re.S|re.M)
        d = pq(text)
        list = d.items(".list_main-list")
        for i in list:
            title = i(".list_info__top_nameY").text()
            img = i(".list_main__l").find("img").attr('src')
            sub_title = i(".list_info__top_text").text()
        
            go_date = i(".list_info__date_li").text()
        
            price_range = i(".list_info__price__new").text()
            price_range = price_range.replace(' ','')
            price = price_range.strip('元|起| ')
            detail_url = i(".list_info__buy").attr("href")
            url_arr = detail_url.split("/")
            h5_url = "http://m.ilvxing.com/deal/"+url_arr[len(url_arr)-1]
            detail_content = self.request_url(h5_url)
            d = pq(detail_content)

            #获取产品亮点
            product_recommend = d(".product-details").items("p")
            rec_str = ''
            for reco in product_recommend:
                if reco.text().strip() == '爱小行密语':
                    continue
                rec_str += reco.text() + "<br>"
            product_recommend = rec_str
            
            #价格计算
            product_price = {}
            product_price['have'] = ''
            product_price['nohave'] = ''
            price_have = price_have_parse.findall(detail_content)
            if len(price_have):
                product_price['have'] = price_have[0]
            price_nohave = price_nohave_parse.findall(detail_content)
            if len(price_nohave):
                product_price['nohave'] = price_nohave[0]
            product_price_detail = json.dumps(product_price,ensure_ascii=False)

            #获取航班信息           
            fly_company_items = d(".notice").items(".traffic")
            fly_content = {}
            fly_list = {}
            i = 1
            for fly in fly_company_items:
                fly_content['company'] = fly.find(".traffic-tit b").text()
                fly_content['goto']    = fly(".traffic-tit").text().strip(fly_content['company'])
                fly_content['fly_time']= fly(".traffic-go .back").text() + " "+fly(".traffic-back .back").text()
                fly_list[i] = fly_content
                i += 1 
            fly_company = json.dumps(fly_list,ensure_ascii=False)

            #获取酒店信息
            hotal_list = d(".hotel").items("dt")
            hotal = {}
            for li in hotal_list:
                span = li("span").text()
                if span == '名称：':
                    hotal['hotal_name'] = li.text().strip(span)
                if span == '星级：':
                    hotal['hotal_star'] = li.text().strip(span)
                if span == '地址：':
                    hotal['hotal_addr'] = li.text().strip(span)
                if span == '酒店介绍：':
                    hotal['hotal_content'] = li.text().strip(span)
                    hotal_img = li.find("img").eq(0).attr("src")
            hotal = json.dumps(hotal,ensure_ascii=False)

            #取消订单须知
            product_cancel_detail = ''

            #获取订票须知
            know_parse = product_know_parse.findall(detail_content) 
            product_know = ''
            if len(know_parse):
                product_know = know_parse[0][0]
                if product_know == '':
                    product_know = know_parse[0][1]

            #产品说明
            special_detail_arr = special_parse.findall(detail_content)
            special_detail = ''
            if len(special_detail_arr):
                special_detail = special_detail_arr[0]
        

            #获取游玩天数
            detail_content = self.request_url(detail_url)
            d = pq(detail_content)
            temp = d(".parameter").html()
            day_parse = pq(temp)
            day = ''
            from_city = ''
            k = 0
            for j in day_parse.items('dd'): 
                if k == 4:
                    from_city = j.text()
                if k == 6:
                    day = j.text()
                k = k + 1

            #具体出发日期 和 价格
            date_detail_arr = date_price_parse.findall(detail_content)
            date_detail= {}
            j = 1
            try:
                if len(date_detail_arr):
                    date_detail_content = date_detail_arr[0][2:]
                    #print date_detail_content
                    s = json.loads(date_detail_content)
                    for (k_date,v_value) in s['dates'].items():
                        date_detail[j] = str(k_date) + ",余"+str(v_value['most'])+"人,"+str(v_value['trip_price'])+"元"
                        j += 1
            except:
                date_detail= {}
            finally:
                date_detail = json.dumps(date_detail,ensure_ascii=False)
            
            self.insertToDb(detail_url,h5_url,day,from_city,item['from'],item['to'],item['type'],price,price_range,title,sub_title,fly_company,hotal,go_date,img,product_recommend,product_know,product_price_detail,product_cancel_detail,special_detail,date_detail)
            
    def parseLlh(self,text,item):
        cancel_parse = re.compile("<div\s*class=\"ydCon\">.*?<h5>取消规则：</h5>(.*?)<h5\s*class=\"line\">预定须知：",re.S|re.M)
        special_parse = re.compile("<h5\s*class=\"line\">\s*特别说明：</h5>(.*?)</div>.*?</div>",re.S|re.M)
        know_parse = re.compile("<h5\s*class=\"line\">预定须知：</h5>(.*?)<h5\s*class=\"line\">\s*特别说明",re.S|re.M)
        price_have_parse = re.compile("<h5>费用包含：</h5>(.*?)<h5\s*class=\"line\">\s*费用不包含",re.S|re.M)
        price_nohave_parse = re.compile("<h5\s*class=\"line\">费用不包含：</h5>(.*?)</div>\s*</div>\s*<!--预订须知-->",re.S|re.M)
        product_recomend_parse = re.compile("<dl\s*class=\"pro_box\">.*?<dt>产品亮点：</dt>.*?<dd>(.*?)<style",re.S|re.M)
        hotal_addr_parse = re.compile("<li>地址(.*?)</li>",re.S|re.M)
        hotal_content_parse = re.compile("<li>酒店简介：(.*?)</li>",re.S|re.M)

        d = pq(text)
        is_have = d(".noreslut").text()
        if is_have == u'抱歉，没有找到相关的商品':
            return ''
        list = d.items(".hotList li")
        for i in list:
            title = i("h3").find('a').text()
            img = ""+i(".lazy").attr('data-original')
            sub_title = i("p").text()
             
            go_date = i("dl dt").text()
             
            price_range = i("dl dd").text()
            price_range = price_range.strip('￥').replace(' ','')
            price = price_range.strip('元|起| ')
            
            detail_url = 'http://www.lailaihui.com'+i("h3 a").attr("href")
            product_url_temp = i("h3 a").attr("href").strip().split("/")
            product_num = product_url_temp[len(product_url_temp)-1]
            h5_url = 'http://m.lailaihui.com/fline/'+product_num
        
            detail_content = self.request_url(h5_url)
            d = pq(detail_content)
            #获取产品亮点
            product_recommend = product_recomend_parse.findall(detail_content)
            if len(product_recommend) > 0:
                product_recommend = product_recommend[0].strip()
            else:
                product_recommend = ''
 
            #获取航班信息
            fly_detail = {}
            fly_company = d(".air").items(".b")
            i = 1
            for fly in fly_company:
                j = 0
                fly_items = fly.items("table tr")
                item_detail = {}
                for table in fly_items:
                    if j == 0:
                        j = j+1
                        continue
                    its = table.items("td")
                    k = 0
                    it_detail = {}
                    for it in its:
                        if k == 0: 
                            it_detail["day"] = it.text()
                        if k == 1: 
                            it_detail["goto"] = it.text()# .replace('<br>','   ')
                        if k == 2: 
                            it_detail["company"] = it.text()
                        if k == 3: 
                            it_detail["fly_type"] = it.text()
                        if k == 4: 
                            it_detail["fly_time"] = it.text().replace('<br>','   ')
                        k = k + 1
 
                    item_detail[j] = it_detail
                   # print item_detail 
                    j = j+1
                fly_detail[i] = item_detail
                i = i + 1
            fly_company = json.dumps(fly_detail,ensure_ascii=False)

            #酒店信息
            hotal_detail = {}
            hotal_detail['img'] = d(".hotal li").find("img").attr("src")
            hotal_detail['hotal_name'] = d(".hotal li").find("b").text()
            hotal_addr = hotal_addr_parse.findall(detail_content);
            if len(hotal_addr) > 0:
                hotal_detail['hotal_addr'] = hotal_addr[0]
            else:
                hotal_detail['hotal_addr'] = ''
            hotal_detail['hotal_star'] = d(".hotal li").find("star_img").text()
            hotal_content = hotal_content_parse.findall(detail_content);
            if len(hotal_content):
                hotal_detail['hotal_content'] = hotal_content[0] 
            else:
                hotal_detail['hotal_content'] = ''
            hotal = json.dumps(hotal_detail,ensure_ascii=False)

            #获取订票须知
            product_know = {}
            product_know = d(".bd .t1").text()
            #取消订单须知
            product_cancel_detail = d(".bd .t2").text()

            #价格计算
            product_price = {}
            product_price['have'] = d(".bd .y").text() 
            product_price['nohave'] = d(".bd .n").text()
            product_price_detail = json.dumps(product_price,ensure_ascii=False)
            
            #产品说明
            special_detail = d(".visa .bd").html()

            #出发城市
            from_city = d(".intro_box .fl").text()
            if from_city != '':
                from_city = from_city.split("-")[1].strip()

            #获取游玩天数
            day = d(".info_box li").eq(1).find("span").text()

            #来来会本地游 出发地 为不限，转为为目的地
            if from_city.decode('utf-8') == '':
                from_city = item['to'] 
            
            #具体出发日期 和 价格
            date_detail_option = d(".ri_qi").items("option")
            date_detail = {}
            i = 1
            for date in date_detail_option:
                date_detail[i] = date.text()
                i = i+1
            date_detail = json.dumps(date_detail,ensure_ascii=False)
            
            #保存到数据库
            self.insertToDb(detail_url,h5_url,day,from_city,item['from'],item['to'],item['type'],price,price_range,title,sub_title,fly_company,hotal,go_date,img,product_recommend,product_know,product_price_detail,product_cancel_detail,special_detail,date_detail)
            
    def parseQn(self,text,item):
        special_parse = re.compile("<h5\s*class=\"line\">\s*特别说明：</h5>(.*?)</div>.*?</div>",re.S|re.M)
        product_know_parse = re.compile("<h3\s*class=\"h_title_t\">重要提示</h3>.*?<div>(.*?)</div>.*?</div>",re.S|re.M)
        cancel_parse = re.compile("<h3\s*class=\"h_title_t\">退款说明</h3>.*?<div>(.*?)</div>.*?</div>",re.S|re.M)
        price_have_parse = re.compile("<h3\s*class=\"h_title_t\">费用包含</h3>.*?<div\s*class=\"cf\">(.*?)</div>.*?</div>",re.S|re.M)
        price_nohave_parse = re.compile("<h3\s*class=\"h_title_t\">费用不包含</h3>.*?<div\s*class=\"cf\">(.*?)</div>.*?</div>",re.S|re.M)
        special_parse = re.compile("<h3\s*class=\"h_title_t\">友情提示</h3>.*?<div>(.*?)</div>.*?</div>",re.S|re.M)
        s = json.loads(text)
        if not s.has_key('headData') :
            return ''
        list = s['headData']
        for li in list:
            h5_url = str(li['touchurl'])
            title  = li['pdContain']
            img = li['imgurl']
            go_date = li['startDate']
            price_range = li['price']
            price = li['price'] 
            detail_url = li['linkurl']
            day = li['days']
            detail_content = self.request_url(detail_url)
            d = pq(detail_content)
            sub_title = ''
            #获取航空公司信息
            fly_tables = d(".tra_box").items("table")
            fly_detail = {}
            i = 1
            for table in fly_tables:
                trs = table.items("tr")
                item_detail = {}
                j = 1
                for tr in trs:
                    its = tr.items("td")
                    k = 0
                    it_detail = {}
                    for it in its:
                        if it.find(".title"):
                            continue
                        if k == 0: 
                            it_detail["day"] = it.text()
                        if k == 2: 
                            it_detail["goto"] = it.text()# .replace('<br>','   ')
                        if k == 3: 
                            it_detail["company"] = it.text()
                        if k == 6: 
                            it_detail["fly_type"] = it.text()
                        if k == 4: 
                            it_detail["fly_time"] = it.text()
                        if k == 5: 
                            it_detail["fly_time"] = it_detail["fly_time"] + "" +it.text()
                        if k == 7: 
                            it_detail["seat"] = it.text()
                        k = k + 1
                    item_detail[j] = it_detail
                    j = j+1
                fly_detail[i] = item_detail
                i = i + 1
            fly_company = json.dumps(fly_detail,ensure_ascii=False)

            #获取酒店信息
            hotal_detail = {}
            imgs = d(".hotel_det").items("img")
            for imgli in imgs:
                if not "https" in imgli.attr("data-lazy"): 
                    hotal_detail['img'] = imgli.attr("data-lazy")
                    break
            hotal_detail['hotal_name'] = d(".h_hotel_name em").text()
            hotal_detail['hotal_addr'] = ''
            hotal_detail['hotal_star'] = d(".h_hotel_name b").text()
           # hotal_content = hotal_content_parse.findall(detail_content);
           # if len(hotal_content):
           #     hotal_detail['hotal_content'] = hotal_content[0] 
           # else:
           #     hotal_detail['hotal_content'] = ''
            hotal_content_list = d(".hotel_det").items("p")
            hotal_detail['hotal_content'] = ''
            for hotal_li in hotal_content_list:
                if hotal_li.text() == '':
                    continue
                hotal_detail['hotal_content'] += "<p>" + hotal_li.text() + "</p>" 

            hotal = json.dumps(hotal_detail,ensure_ascii=False)

            #获取产品亮点
            product_recommend = d('.groom .ct').html().strip()
            if product_recommend == '':
                recommend_list = d(".pm_recommend .pm_list").items("li")
                for rec in recommend_list:
                    product_recommend += rec.text() + "<br>"

            #预定须知
            know_parse = product_know_parse.findall(detail_content) 
            product_know = ''
            if len(know_parse):
                product_know = know_parse[0]

            #出发城市
            from_city = item['from'] 

            #取消订单须知
            cancel_par = cancel_parse.findall(detail_content) 
            product_cancel_detail = ''
            if len(cancel_par):
                product_cancel_detail = cancel_par[0]

            #价格计算
            product_price = {}
            product_price['have'] = ''
            product_price['nohave'] = ''
            price_have = price_have_parse.findall(detail_content)
            if len(price_have):
                product_price['have'] = price_have[0]

            price_nohave = price_nohave_parse.findall(detail_content)
            if len(price_nohave):
                product_price['nohave'] = price_nohave[0]
            product_price_detail = json.dumps(product_price,ensure_ascii=False)
            
            #产品说明
            special_detail_arr = special_parse.findall(detail_content)
            special_detail = ''
            if len(special_detail_arr):
                special_detail = special_detail_arr[0]
            

            #具体出发日期 和 价格
            next_month = int(time.time()) + 31 * 24 * 60 * 60 
            next2_month = int(time.time()) + 2 * 31 * 24 * 60 * 60 
            date_arr = (time.strftime("%Y-%m"),time.strftime("%Y-%m",time.localtime(next_month)),time.strftime("%Y-%m",time.localtime(next2_month))) 

            urlparsedetail = urlparse.urlparse(h5_url)
            query = urlparse.parse_qs(urlparsedetail.query,True)
            id = str(query['id'][0])

            date_detail = {}
            num = 1
            for da in date_arr:
                date_url = "http://gzyq1.package.qunar.com/api/calPrices.json?pId="+id+"&month="+da
                json_result = self.request_url(date_url)
                load = json.loads(json_result)
                strr = ''
                data_list = load['data']['team']
                for dlist in data_list:
                    strr = str(dlist['date'])+",余"+str(dlist['maxBuyCount'])+"人,"+str(dlist['prices']['adultPrice'])+"元"
                    date_detail[num] = strr
                    num +=1
            date_detail = json.dumps(date_detail,ensure_ascii=False)

            #保存到数据库
            self.insertToDb(detail_url,h5_url,day,from_city,item['from'],item['to'],item['type'],price,price_range,title,sub_title,fly_company,hotal,go_date,img,product_recommend,product_know,product_price_detail,product_cancel_detail,special_detail,date_detail)

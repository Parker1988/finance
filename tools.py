import datetime
import re
import os
import requests
from bs4 import BeautifulSoup
import json
import time
from pandas import DataFrame
def stock_list(Stkcd,code_str):
    for stock_code in Stkcd:
        stock_code = int(stock_code)
        stock_string = str(stock_code)
        len_num = len(stock_string)
        for num in range(0, 6 - len_num):  # 迭代 10 到 20 之间的数字
            stock_string = "0" + stock_string
        code_str.append(stock_string)

def Begindate_list(DateBegin,begintime):
    for begindate in DateBegin:
        delta = datetime.timedelta(days=begindate)
        begindate = datetime.datetime.strptime('1899-12-30', '%Y-%m-%d') + delta  # 将1899-12-30转化为可以计算的时间格式并加上要转化的日期戳
        begindate = datetime.datetime.strftime(begindate, '%Y-%m-%d')  # begindate是个str
        # begindate = datetime.datetime.strptime(begindate, '%Y-%m-%d')
        begintime.append(begindate)


def Enddate_list(DateEnd,endtime):
    for enddate in DateEnd:
        delta = datetime.timedelta(days=enddate)
        enddate = datetime.datetime.strptime('1899-12-30', '%Y-%m-%d') + delta  # 将1899-12-30转化为可以计算的时间格式并加上要转化的日期戳
        enddate = datetime.datetime.strftime(enddate, '%Y-%m-%d')
        endtime.append(enddate)


def crawl(web_data,stock_code, event_time, begin_time, end_time):
    notice_list = []
    pt = "1e56yui9"
    web_data.encoding = web_data.apparent_encoding
    html = web_data.text
    #    str_html = str(html)
    html = html[:-1]+pt
    pat = re.compile('='+'(.*?)'+pt,re.S)
    result = pat.findall(html)
    strdata = result[0]
    jd = json.loads(strdata)

    notices = jd["data"]

    # 分析网页可以发现返回内容是两个json嵌套，内层json在data里，可以拿出来循环然后解析
    for notice in notices:
        noticedate = notice['NOTICEDATE'][0:10]
        noticedate_f = time.mktime(time.strptime(noticedate, '%Y-%m-%d'))
        begin_time_f = time.mktime(time.strptime(begin_time, '%Y-%m-%d'))
        end_time_f = time.mktime(time.strptime(end_time, '%Y-%m-%d'))
        diff_begin = noticedate_f - begin_time_f
        diff_end = noticedate_f - end_time_f

        if (diff_begin < 0 or diff_end > 0 or (notice["CDSY_SECUCODES"][0]["SECURITYTYPE"] != 'A股')):
        # if (diff_begin < 0 or diff_end > 0 ):
            continue
        title = notice['NOTICETITLE']
        # date = notice['NOTICEDATE']
        url = notice['Url']
        ANN_RELCOLUMNS = notice['ANN_RELCOLUMNS']
        type_notice = ANN_RELCOLUMNS[0]['COLUMNNAME']
        pdf_data = requests.get(url)

        if pdf_data.text:
            pdf_soup = BeautifulSoup(pdf_data.text, 'lxml')
            for x in pdf_soup.find_all('a', href=re.compile('\.pdf')):
                pdf_url = x.get('href')
                if pdf_url:
                    # pdf_url = link
                    DownloadPdf(pdf_url, stock_code,type_notice,noticedate)
                    print(pdf_url)
                    # xia zai
                    break
        notice_list.append([stock_code, event_time, title, type_notice, noticedate, url])
    df = DataFrame(notice_list)
    if not df.empty:
        df.columns = ['Stkcd', 'Eventdate', 'Title', 'Type', 'NOTICEDATE', 'URL']
    return stock_code,event_time,df

def DownloadPdf(pdf_url,stock_code,type_notice,noticedate):
    file_exist = False
    file_name1 = pdf_url[25:]
    # file_name = stock_code+'-'+noticedate+'.pdf'
    file_name = stock_code+'-'+noticedate+'-'+file_name1
    file_path = r'D:\1-RESEARCH\GSH\SEO\InfoManipulate\爬虫公告\PDF_Files\\'
    for root, dirs, files in os.walk(file_path):
        for f in files:
            if f == file_name:
                file_exist=True
                # print(stock_code + ':PDF公告已存在')
    if file_exist==False:
        path = r'D:\1-RESEARCH\GSH\SEO\InfoManipulate\爬虫公告\PDF_Files\\'+ file_name
        r = requests.get(pdf_url)
        f = open(path, "wb")
        f.write(r.content)
        f.close()

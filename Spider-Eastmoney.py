# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 00:49:57 2019

@author: 86518
"""
import tools
import urllib
import re
import time
import json
import os
import xlrd
import datetime
import requests
from pandas import DataFrame
import pandas as pd
from bs4 import BeautifulSoup
begintime = []
endtime = []
code_str = []

if __name__ == "__main__":
    # 这里的list是股票代码list
    EventFile = xlrd.open_workbook(r'D:\1-RESEARCH\GSH\SEO\InfoManipulate\爬虫公告\Eventdate.xlsx', 'r',
                                   encoding_override='utf-8')
    Sheet_names = EventFile.sheet_names()
    EventStkcd = EventFile.sheet_by_name(Sheet_names[0])
    Stkcd = EventStkcd.col_values(0)[1:]
    DateEvent = EventStkcd.col_values(1)[1:]
    DateBegin = EventStkcd.col_values(2)[1:]
    DateEnd = EventStkcd.col_values(3)[1:]
    begintime = []
    endtime = []
    code_str = []
    eventtime = []
    Announce_num = []
    df_result = pd.DataFrame(columns=['Stkcd', 'Eventdate', 'Title', 'Type', 'NOTICEDATE', 'URL'])  # 创建一个空的dataframe
    tools.stock_list(Stkcd, code_str)
    tools.Begindate_list(DateBegin, begintime)
    tools.Enddate_list(DateEnd, endtime)

    for i in range(0,len(code_str)):
        finish = False  #没有读取成功
        url = 'http://data.eastmoney.com/notices/getdata.ashx?StockCode=' + code_str[i] + '&FirstNodeType=0&SecNodeType=0&CodeType=1&PageIndex=1&PageSize=99999'
        while finish == False:
            try:
                web_data = requests.get(url)
                Code,Event_date,df=tools.crawl(web_data,code_str[i], DateEvent[i],begintime[i], endtime[i])
                df_result = df_result.append(df)
                Announce_num.append([Code,Event_date,df.shape[0]])
                df_num = DataFrame(Announce_num)
                df_num.columns = ['Stkcd', 'Eventdate', 'AnnouncementNum']
                finish = True
                print(i)
            # except ZeroDivisionError as e:
            except:
                # a = False
                time.sleep(10)
                print('重新提交-请稍等')
    df_result.to_csv(r'D:\1-RESEARCH\GSH\SEO\InfoManipulate\爬虫公告\result.csv', encoding="utf_8_sig", index=False)
    df_num.to_csv(r'D:\1-RESEARCH\GSH\SEO\InfoManipulate\爬虫公告\AnnouncementNum.csv', encoding="utf_8_sig", index=False)

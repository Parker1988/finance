#自动爬取巨潮咨询公告链接，名称，时间

import sys
from selenium import webdriver
import time
from lxml import etree
browser = webdriver.Chrome()

sub_code_list = []
sub_name_list = []
sub_title_list = []
sub_time_list = []
code_name_list =["000001","000002","000003"]
http_l = "http://www.cninfo.com.cn"
for code in code_name_list:
    browser.get('http://www.cninfo.com.cn/new/commonUrl?url=disclosure/list/notice')
    browser.find_element_by_class_name("page-more-filter").click()
    time.sleep(5)

    res = browser.find_elements_by_css_selector('.page-action-tab-search a')
    res[2].click()
    time.sleep(1)
    res1 = browser.find_elements_by_css_selector('.page-filter-select a')
    res1[3].click()

    time.sleep(1)
    browser.find_element_by_id("index-cw-input-obj-more").send_keys(code)
    time.sleep(1)
    browser.find_element_by_name(code).click()
    abc=browser.find_element_by_xpath("/html/body/div[3]/div[2]/div[2]/div[1]/table/tbody/tr/td[2]/div/span")
    txt=abc.text
    page_count=txt.strip('共').strip('条')
    page_count = int(page_count)
    # print(txt.strip('共').strip(''))
    page_last = page_count%30
    page_count = int(page_count/30)
    if page_last:
        page_count+=1
    print(page_count)
    page_active=1

    for page_i in range(1,page_count+1):
        html = browser.page_source
        tree = etree.HTML(html)
        page_active = tree.xpath(
            "/html/body/div[3]/div[2]/div[2]/div[5]/div/ul//li[@class='page-tabs-list active']//text()")
        page_active = int(page_active[0])
        print(page_active)
        while page_i != page_active:
            html=browser.page_source
            tree=etree.HTML(html)
            page_active=tree.xpath("/html/body/div[3]/div[2]/div[2]/div[5]/div/ul//li[@class='page-tabs-list active']//text()")
            page_active = int(page_active[0])
            print(page_active)

        sub_code=tree.xpath("/html/body/div[3]/div[2]/div[2]/div[4]/table/tbody//td[@class='sub-code']//text()")
        sub_code_list.append(sub_code)

        sub_name=tree.xpath("/html/body/div[3]/div[2]/div[2]/div[4]/table/tbody//td[@class='sub-name']//text()")
        sub_name_list.append(sub_name)

        sub_title=tree.xpath("/html/body/div[3]/div[2]/div[2]/div[4]/table/tbody//td[@class='sub-title']//a/@href")
        for sub_title_text in sub_title:
            sub_title_text = http_l+sub_title_text
            sub_title_list.append(sub_title_text)


        sub_time=tree.xpath("/html/body/div[3]/div[2]/div[2]/div[4]/table/tbody//div[@class='sub-time-time']//text()")
        sub_time_list.append(sub_time)

        # tree.xpath("/html/body/div[3]/div[2]/div[2]/div[5]/div/ul/li[6]").click
        next_p = page_count+3
        next_p = str(next_p)
        browser.find_element_by_xpath("/html/body/div[3]/div[2]/div[2]/div[5]/div/ul/li["+next_p+"]/a").click()
        time.sleep(3)

print(sub_title_list)
print("end")
#保存数据至硬盘

time.sleep(10)
browser.quit()
import base64
import json
import re
import time

import requests
import tikets_

import selenium.webdriver as webdriver
from selenium.webdriver.support.select import Select

from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

options =webdriver.ChromeOptions()
# options.add_argument('headless')

file = open(r'D:\Users\yostar\PycharmProjects\BigDate\tiket.json', "rb")

fileJson = json.load(file)

driver = webdriver.Chrome(options = options)

login_url = 'https://kyfw.12306.cn/otn/resources/login.html'

driver.get(login_url)

time.sleep(2)

driver.find_element_by_link_text('账号登录').click()

driver.find_element_by_id('J-userName').send_keys(fileJson['tiket']['login_name'])

driver.find_element_by_id('J-password').send_keys(fileJson['tiket']['login_pwd'])

while True:     #手动进行图片验证，并登录
    curpage_url = driver.current_url
    if curpage_url != login_url:
        if curpage_url[:-1] != login_url:
            print('.......登陆成功........')
            break
        else:
            time.sleep(3)
            print('--------->等待用户进行图片验证')

time.sleep(2)

from urllib.parse import quote
import string

fs = fileJson['start_station']

ts = fileJson['end_station']

fs_code = tikets_.get_station(fs)
ts_code = tikets_.get_station(ts)

data = fileJson['start_date']
#出发时间
departure_time = fileJson['start_time']
#用户
user_be_name = fileJson['user_name']

departure_timeStamp = 0
if departure_time != 'all':
    tss1 = data + ' ' + departure_time + ":00"
    timeArray = time.strptime(tss1, "%Y-%m-%d %H:%M:%S")
    departure_timeStamp = int(time.mktime(timeArray))


select_tiket = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs='+fs+','+fs_code+'&ts='+ts+','+ts_code+'&date='+data+'&flag=N,N,Y'

select_tiket = quote(select_tiket, safe = string.printable)

print(select_tiket)

driver.get(select_tiket)

time.sleep(2)

from bs4 import BeautifulSoup

soup = BeautifulSoup(driver.page_source,'lxml')

tiket_list = soup.findAll('tbody',attrs={'id':'queryLeftTable'})

tiket_soup = tiket_list[0].findAll('tr')



for tiket in tiket_soup:
    station_num_tag = tiket.find('a',attrs = {'class':'number'})
    station_num = ' * '
    if station_num_tag != None:
        station_num = station_num_tag.text
    else:
        continue

    staticon_tags = tiket.find('div',attrs={'class':'cdz'}).findAll('strong')
    start_s = staticon_tags[0].text
    end_s = staticon_tags[1].text

    emailid_regexp = re.compile('YW_+\w')

    yz = tiket.find('td',attrs={'id':emailid_regexp})
    yw_text = '无("")'
    if yz != None:
        yw_text = yz.text

    station_times = tiket.find('div',attrs={'class':'cds'}).findAll('strong')
    start_time = station_times[0].text
    end_time = station_times[1].text
    tss2 = data + ' ' + start_time + ":00"
    timeArray2 = time.strptime(tss2, "%Y-%m-%d %H:%M:%S")
    start_timeStamp = int(time.mktime(timeArray2))

    if start_timeStamp > departure_timeStamp:
        print('这个时间出发' + station_num)
        statrt = tiket.find('a',text ='预订')
        js = statrt.get('onclick')
        driver.execute_script(js)
        break


    print(station_num + ' ---- ' +start_s+ '<->' +end_s+ ' ---- '  + '硬卧：'+yw_text  + ' ---- '  + '出发时间：' + start_time + ',到达时间：'+end_time)

time.sleep(2)


def submit_order():
    try:
        try:
            try:
                Select(driver.find_element_by_id("seatType_1")).select_by_value('3')
            except:
                Select(driver.find_element_by_id("seatType_1")).select_by_value('2')
        except:
            Select(driver.find_element_by_id("seatType_1")).select_by_value('1')
    except:
        Select(driver.find_element_by_id("seatType_1")).select_by_value('O')

    cursor_soup = BeautifulSoup(driver.page_source, 'lxml')
    # cursor: pointer
    cursor_tags = cursor_soup.find('ul', attrs={'id': 'normal_passenger_id'}).find_all('li')

    for cursor_tag in cursor_tags:
        user_tag = cursor_tag.find('label')
        for user_name in user_be_name:
            if user_tag.text in user_name:
                cursor_id = user_tag.get('for')
                print(cursor_id)
                driver.find_element_by_id(cursor_id).click()

    driver.find_element_by_link_text('提交订单').click()
    time.sleep(3)
    driver.find_element_by_link_text('确认').click()

submit_order()
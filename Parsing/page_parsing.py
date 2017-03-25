# coding: utf-8
from bs4 import BeautifulSoup
import requests
import pymongo
from time import sleep


client = pymongo.MongoClient('localhost', 27017)
graduation = client['graduation']
url_list = graduation['url_list']
item_info = graduation['item_info']
start_url = 'http://sh.58.com/chuzu'


def get_links_from(url, pages, who_rent=0):
    list_view = url + '/{}/pn{}/'.format(str(who_rent), str(pages))
    wb_data = requests.get(list_view)
    sleep(1)
    soup = BeautifulSoup(wb_data.text, 'lxml')
    if soup.find('ul', 'listUl'):
        links = soup.select('ul.listUl > li > div.des > h2 > a')
        for link in links:
            item_link = link.get('href')
            url_list.insert_one({'url': item_link})
            print {'url': item_link}
    else:   # 最后一页
        pass


def get_item_info(url):
    wb_data = requests.get(url)
    soup = BeautifulSoup(wb_data.text, 'lxml')
    rent_type = soup.select('ul.f14 > li > span')[1].text[:2] if soup.find('ul','f14') else None
    price = soup.select('span.c_ff552e > b.f36')[0].text
    area = soup.select('ul.f14 > li > span > a')[1].text if soup.find('ul','f14') else None
    item_info.insert_one({'price':price, 'area':area, 'url':url, 'rent_type':rent_type})
    # print {'price':price, 'area':area, 'url':url}


def get_all_links_from(url):
    for j in [0, 1]:    # 区分个人房源和经纪人房源
        for i in range(1,100):  # 遍历page页
            try:
                get_links_from(url, i, j)
            except Exception,e:
                print url, i, j
                print e


# db_urls = [item['url'] for item in url_list.find()]
#
# index_urls = [item['url'] for item in item_info.find()]
# x = set(db_urls)
# y = set(index_urls)
# rest_of_urls = x-y
# for url in rest_of_urls:
#     try:
#         get_item_info(url)
#     except Exception,e:
#         print url
#         print e

def get_area_price(area, rent_type=None):
    price_index=['低于600元','600-1000元','1000-1500元','1500-2000元','2000-3000元','3000-5000元','5000-8000元']
    post_times = [0,0,0,0,0,0,0,0]
    if rent_type == None:
        items = item_info.find({"area":area})
    else:
        items = item_info.find({"area":area,"rent_type":rent_type})
    for i in items:
        if i['price'] < 600:
            post_times[0] += 1
        elif 600<=i['price']<1000:
            post_times[0] += 1
        elif 1000<= i['price']<1500:
            post_times[1] += 1
        elif 1500<= i['price']<2000:
            post_times[2] += 1
        elif 2000<= i['price']<3000:
            post_times[3] += 1
        elif 3000<= i['price']<5000:
            post_times[4] += 1
        elif 5000<= i['price']<8000:
            post_times[5] += 1
        elif 8000<= i['price']:
            post_times[6] += 1
    print post_times
    length=0
    if length <= len(price_index):
        for price,times in zip(price_index,post_times):
            data = {
                'name':price,
                'data':times,
            }
            yield data
            length += 1
# -*- coding:utf8 -*-
import datetime
import json
import math
import os
import time
from threading import Thread
import threading

import requests
from bs4 import BeautifulSoup
from config import conf
from download import Download
from login_api import Login
from db import save_db

class Pixiv:
    def __init__(self):
        self.session = Login().login()
        self.download = Download()

    # 每日热点
    def _day_parser(self, path, mode):
        payload = {'mode': mode}
        url = 'https://www.pixiv.net/ranking.php'
        login = requests.get(url, params=payload)
        pages = BeautifulSoup(login.text, 'lxml')
        ranking_items = pages.find('div', class_='ranking-items adjust').find_all('div', class_='ranking-image-item')
        img_list = []
        for ranking_item in ranking_items:
            pic_id = ranking_item.find('img')['data-id']  # 获取图片id
            try:
                page_count = int(ranking_item.find('div', class_='page-count').get_text())  # 插画页数
            except:
                page_count = 1
            pic_src = ranking_item.find('img')['data-src'].replace('/c/240x480', '').replace('_master1200', '').replace(
                'master', 'original')
            img_list.append([pic_src, pic_id, page_count])
        # print(path)
        self.download.thread_download(img_list, path)

    def day(self, mode='daily'):
        path = conf('day')  # 自定义输入保存路径
        if mode == 'daily':
            yesterday = str(datetime.date.today() - datetime.timedelta(days=1))
        else:
            yesterday = str(datetime.date.today() - datetime.timedelta(days=1)) + '_r18'
        path = os.path.join(path, yesterday)
        self._day_parser(path, mode)

    # 收藏
    def _collection_parser(self, col_page, user_id, path):
        url = 'https://www.pixiv.net/bookmark.php'
        payload = {'id': user_id, 'rest': 'show', 'p': col_page}
        try:
            r = self.session.get(url, parms=payload)
        except:
            time.sleep(2)
            r = self.session.get(url, params=payload)
        print(r.url)
        image_items = BeautifulSoup(r.text, 'lxml').find_all('li', class_='image-item')
        img_list = []
        for image_item in image_items:
            pic_id = image_item.find('img')['data-id']
            pic_src = image_item.find('img')['data-src'].replace('/c/150x150', '').replace('_master1200', '').replace(
                'master', 'original')
            try:
                page_count = image_item.find('div', class_='page-count').get_text()
            except:
                page_count = 1
            img_list.append([pic_src, pic_id, page_count])
        self.download.thread_download(img_list, path)
        print('''
    下载完一页啦
        ''')

    def get_col_page_num(self, user_id=''):
        url = 'https://www.pixiv.net/bookmark.php'
        if user_id == '':
            payload = {}
        else:
            payload = {'id': user_id}
        r = self.session.get(url, params=payload)
        col_num = int(
            BeautifulSoup(r.text, 'lxml').find('div', 'column-label').find('span', class_='count-badge').get_text().replace('件', ''))
        print("共{}个作品".format(col_num))
        end_page = math.ceil(col_num / 20)
        return end_page

    def collection(self, user_id='', mode='all'):
        path = conf('collection')  # 自定义输入保存路径
        if user_id == '':
            path = os.path.join(path, '1')
        else:
            path = os.path.join(path, user_id)

        if mode == 'all':
            start_page = 1
            end_page = self.get_col_page_num(user_id)
        else:
            start_page = int(input('请输入要开始的起始页数：'))
            end_page = int(input('请输入你要结束的页数：'))
        print('开始下载')
        for col_page in range(start_page, end_page + 1):
            self._collection_parser(str(col_page), user_id, path)  # collection 函数
            time.sleep(1)
        print('下载结束')

    # 作者id下载
    def _author_parser(self, col_page, author_id, path):
        url = 'https://www.pixiv.net/member_illust.php'  # 作者页
        payload = {'id': author_id, 'type': 'all', 'p': col_page}
        r = self.session.get(url, params=payload)
        try:
            name = BeautifulSoup(r.text, 'lxml').find('a', class_='user-name').get_text()
            print(name)
        except:
            print('输入错误，请重新输入')
            time.sleep(100)

        path = os.path.join(path, name)
        img_list = []
        image_items = BeautifulSoup(r.text, 'lxml').find_all('li', class_='image-item')
        for image_item in image_items:
            pic_id = image_item.find('img')['data-id']
            pic_src = image_item.find('img')['data-src'].replace('/c/150x150', '').replace('_master1200', '').replace(
                'master', 'original')
            try:
                page_count = image_item.find('div', class_='page-count').get_text()
            except:
                page_count = 1
            img_list.append([pic_src, pic_id, page_count])
        self.download.thread_download(img_list, path)

        print('''
                下载完一页啦
            ''')

    def author(self, author_id, start_page, end_page):
        path = conf('author')  # 自定义输入保存路径
        for col_page in range(int(start_page), int(end_page) + 1):
            self._author_parser(col_page, author_id, path)

    # 下面方法是关于搜索
    def _get_page_num(self, keyword, mode):
        url = 'https://www.pixiv.net/search.php?word={}&order=date_d&mode={}&p={}'.format(keyword, mode, 1)
        r = self.session.get(url)
        num = BeautifulSoup(r.text, 'lxml').find('div', class_='search-result-information').find(
            'span').get_text().replace('件', '')
        page_num = math.ceil(int(num) / 20)
        return page_num

    # 获得页数的url
    def get_page_urls(self, keyword, mode):
        base_url = 'https://www.pixiv.net/search.php?word={}&order=date_d&mode={}&p={}'
        page = self._get_page_num(keyword, mode)
        print('共{}页需要解析'.format(page))
        print('解析中·····')
        urls = [base_url.format(keyword, mode, i) for i in range(1, page + 1)]
        return urls

    def get_detail(self, page_url, img_data):
        print(page_url)
        try:
            r = self.session.get(page_url)
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(2)
            return False

        data = BeautifulSoup(r.text, 'lxml').find('input', id='js-mount-point-search-result-list')['data-items']
        image_items = json.loads(data)
        for image_item in image_items:
            url = image_item['url']
            star = image_item['bookmarkCount']
            page_count = image_item['pageCount']
            illust_id = image_item['illustId']
            img_data.append([url, star, page_count, illust_id])

    # 根据页面url获得图片列表并按照star排序
    def get_all_urls(self, page_urls, keyword):
        start_time = time.time()
        img_data = []
        threads = []
        for page_url in page_urls:
            t = threading.Thread(target=self.get_detail, args=[page_url, img_data])
            threads.append(t)

        for t in threads:
            t.start()
            while True:
                # 判断正在运行的线程数量,如果小于5则退出while循环,
                # 进入for循环启动新的进程.否则就一直在while循环进入死循环
                if (threading.active_count() < 150):
                    break

        for t in threads:
            t.join()
        sorted_pic_urls = sorted(img_data, key=lambda x: x[1], reverse=True)
        save_db(sorted_pic_urls, keyword)  # 写入数据库
        end_time = time.time()
        print("搜索共花费{}秒".format(end_time - start_time))
        return sorted_pic_urls

    def get_original_urls(self, sorted_img, num):
        img_list = []
        for img in sorted_img[:num]:
            pic_src = img[0].replace('/c/240x240', '').replace('_master1200', '').replace('master', 'original')
            pic_id = img[3]
            page_count = img[2]
            img_list.append([pic_src, pic_id, page_count])
        return img_list

    def search(self, keyword, num, mode):
        # 获得排序过的图片列表
        # print(os.getcwd())
        path = conf('search')  # 自定义输入保存路径
        path = os.path.join(path, keyword)
        page_urls = self.get_page_urls(keyword, mode)
        sorted_img = self.get_all_urls(page_urls, keyword)
        img_list = self.get_original_urls(sorted_img, num)
        self.download.thread_download(img_list, path)


if __name__ == '__main__':
    pixiv = Pixiv()
    # pixiv.get_col_page_num()
    pixiv.get_col_page_num(3703525)

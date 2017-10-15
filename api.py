# -*- coding:utf8 -*-
import datetime
import json
import math
import os
import time
from threading import Thread
import threading

from bs4 import BeautifulSoup
from config import conf
from download import Download
from login_api import Login


class Pixiv:
    def __init__(self):
        self.session = Login().login()
        self.download = Download()

    # 每日热点
    def _day_parser(self, path, param=''):
        url = 'https://www.pixiv.net/ranking.php?mode=daily' + param
        login = self.session.get(url)
        pages = BeautifulSoup(login.text, 'lxml')
        ranking_items = pages.find('div', class_='ranking-items adjust').find_all('div', class_='ranking-image-item')
        img_list = []
        for ranking_item in ranking_items:
            img_data = []
            pic_id = ranking_item.find('img')['data-id']  # 获取图片id
            try:
                page_count = int(ranking_item.find('div', class_='page-count').get_text())
            except:
                page_count = 1
            pic_src = ranking_item.find('img')['data-src'].replace('/c/240x480', '').replace('_master1200', '').replace(
                'master', 'original')
            img_data.append(pic_src)
            img_data.append(pic_id)
            img_data.append(page_count)
            img_list.append(img_data)
        print(path)
        self.thread_download(img_list, path)

    def day(self, param=''):
        path = conf('day')  # 自定义输入保存路径
        if param == '':
            yesterday = str(datetime.date.today() - datetime.timedelta(days=1))
        else:
            yesterday = str(datetime.date.today() - datetime.timedelta(days=1)) + '_r18'
        path = os.path.join(path, yesterday)
        self._day_parser(path)

    # 个人收藏
    def _collection_parser(self, col_page, path):
        url = 'https://www.pixiv.net/bookmark.php?rest=show&p=' + col_page
        try:
            login = self.session.get(url)
        except:
            time.sleep(2)
            login = self.session.get(url)
        image_items = BeautifulSoup(login.text, 'lxml').find('div', class_='display_editable_works').find_all('li',
                                                                                                              class_='image-item')
        img_list = []
        for image_item in image_items:
            img_data = []
            pic_id = image_item.find('img')['data-id']
            pic_src = image_item.find('img')['data-src'].replace('/c/150x150', '').replace('_master1200', '').replace(
                'master', 'original')
            try:
                page_count = image_item.find('div', class_='page-count').get_text()
            except:
                page_count = 1
            img_data.append(pic_src)
            img_data.append(pic_id)
            img_data.append(page_count)
            img_list.append(img_data)
        self.thread_download(img_list, path)
        print('''
    下载完一页啦
        ''')

    def collection(self, name='all'):
        path = conf('collection')  # 自定义输入保存路径
        url = 'https://www.pixiv.net/bookmark.php'
        r = self.session.get(url)
        col_num = int(
            BeautifulSoup(r.text, 'lxml').find('div', 'column-label').get_text().replace('你的收藏', '').replace('件', ''))
        print("共{}个作品".format(col_num))
        if name == 'all':
            start_page = 1
            end_page = math.ceil(col_num / 20)
        else:
            start_page = int(input('请输入要开始的起始页数：'))
            end_page = int(input('请输入你要结束的页数：'))
        print('开始下载')
        for col_page in range(start_page, end_page + 1):
            self._collection_parser(str(col_page), path)  # collection 函数
            time.sleep(1)
        print('下载结束')

    # 作者id下载
    def _author_parser(self, col_page, author_id, path):
        url = 'https://www.pixiv.net/member_illust.php?id=' + author_id + '&type=all&p=' + col_page  # 作者页
        login = self.session.get(url)
        try:
            name = BeautifulSoup(login.text, 'lxml').find('a', class_='user-name').get_text()
            print(name)
        except:
            print('输入错误，请重新输入')
            time.sleep(100)
        path = os.path.join(path, name)
        img_list = []
        image_items = BeautifulSoup(login.text, 'lxml').find_all('li', class_='image-item')
        for image_item in image_items:
            img_data = []
            pic_id = image_item.find('img')['data-id']
            pic_src = image_item.find('img')['data-src'].replace('/c/150x150', '').replace('_master1200', '').replace(
                'master', 'original')
            try:
                page_count = image_item.find('div', class_='page-count').get_text()
            except:
                page_count = 1
            img_data.append(pic_src)
            img_data.append(pic_id)
            img_data.append(page_count)
            img_list.append(img_data)
        # print(img_list)
        self.thread_download(img_list, path)

        print('''
                下载完一页啦
            ''')

    def author(self, author_id, start_page, end_page):
        path = conf('author')  # 自定义输入保存路径
        for col_page in range(start_page, end_page + 1):
            self._author_parser(str(col_page), str(author_id), path)

    # 下面方法是关于搜索
    def _get_page(self, keyword, mode):
        url = 'https://www.pixiv.net/search.php?word={}&order=date_d&mode={}&p={}'.format(keyword, mode, 1)
        r = self.session.get(url)
        num = BeautifulSoup(r.text, 'lxml').find('div', class_='search-result-information').find(
            'span').get_text().replace('件', '')
        pages = math.ceil(int(num) / 20)
        return pages

    def get_page_urls(self, keyword, mode):
        base_url = 'https://www.pixiv.net/search.php?word={}&order=date_d&mode={}&p={}'
        page = self._get_page(keyword, mode)
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
            data_list = []
            data_list.append(image_item['url'])
            data_list.append(image_item['bookmarkCount'])
            data_list.append(image_item['pageCount'])
            data_list.append(image_item['illustId'])
            img_data.append(data_list)

    # 排序图片列表
    def sort_list(self, keyword, mode):
        start_time = time.time()
        page_urls = self.get_page_urls(keyword, mode)
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
        sorted_img = sorted(img_data, key=lambda x: x[1], reverse=True)
        end_time = time.time()
        print("搜索共花费{}秒".format(end_time - start_time))
        return sorted_img

    # 多线程下载
    def thread_download(self, img_list, path):
        threads = []
        for url in img_list:
            # print(url)
            pic_src = url[0]
            pic_id = url[1]
            page_count = int(url[2])
            print(page_count)
            t = threading.Thread(target=self.download.download, args=[pic_src, pic_id, page_count, path])
            threads.append(t)

        for t in threads:
            t.start()
            while True:
                # 判断正在运行的线程数量,如果小于5则退出while循环,
                # 进入for循环启动新的进程.否则就一直在while循环进入死循环
                if (threading.active_count() < 10):
                    break
        for t in threads:
            t.join()
        print('下载完成')

    def get_image_list(self, sorted_img, num):
        img_list = []
        for img in sorted_img[:num]:
            img_src = []
            img_src.append(img[0].replace('/c/240x240', '').replace('_master1200', '').replace('master', 'original'))
            img_src.append(img[3])
            img_src.append(img[2])
            img_list.append(img_src)
        return img_list

    def search(self, keyword, num, mode):
        # 获得排序过的图片列表
        # print(os.getcwd())
        path = conf('search')  # 自定义输入保存路径
        path = os.path.join(path, keyword)
        print(path)
        sorted_img = self.sort_list(keyword, mode)
        img_list = self.get_image_list(sorted_img, num)
        self.thread_download(img_list, path)


if __name__ == '__main__':
    pixiv = Pixiv()
    pixiv._author_parser('1', '3703525', '')
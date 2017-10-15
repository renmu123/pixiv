# -*- coding:utf8 -*-
import os
import time
import threading

import requests
from bs4 import BeautifulSoup
from config import img_headers
from login_api import Login


class Download:
    def __init__(self):
        self.session = Login().login()

    def _download(self, pic_src, pic_id, page_count, path):
        # print(path)
        extension = pic_src[-4:]  # 扩展名
        for i in range(0, int(page_count)):
            name = pic_id + '_' + str(i) + extension
            name_path = os.path.join(path, name)
            print(name_path)
            img_src = pic_src[:-5] + str(i) + extension
            if os.path.isfile(os.path.join(path, name)):  # 如果文件存在就跳过
                continue
            # print(img_src)
            try:
                img = self.session.get(img_src, headers=img_headers)
            except:
                time.sleep(3)
                img = self.session.get(img_src, headers=img_headers)
            with open(os.path.join(path, name), 'ab') as f:
                f.write(img.content)

            if os.path.getsize(os.path.join(path, name)) < 200:  # 因为pixiv的缩略图都是经过压缩的jpg格式，当下载的我文件太小时，把格式变为png重新下载
                os.remove(str(os.path.join(path, name)))
                extension = '.png'
                name = pic_id + '_' + str(i) + extension
                name_path = os.path.join(path, name)
                if os.path.isfile(name_path):
                    continue
                self.download_png(pic_src, name_path)

    # 下载图片
    def download(self, pic_src, pic_id, page_count, path):
        # print('下载中·······')
        extension = pic_src[-4:]  # 扩展名
        if page_count == 1:
            if os.path.isfile(os.path.join(path, pic_id + extension)):  # 如果文件存在
                return True
            else:
                self._download(pic_src, pic_id, page_count, path)
        else:
            if os.path.exists(os.path.join(path, pic_id)):  # 判断文件夹存在
                self._download(pic_src, pic_id, page_count, os.path.join(path, pic_id))
            else:
                path_name = os.path.join(path, pic_id)
                os.makedirs(path_name)
                self._download(pic_src, pic_id, page_count, path_name)

    def download_png(self, pic_src, name_path):
        url = pic_src[:-4] + '.png'
        img = self.session.get(url, headers=img_headers)
        with open(name_path, 'ab') as f:
            f.write(img.content)

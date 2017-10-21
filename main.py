# -*- coding:utf8 -*-
import os
import time

from api import Pixiv
from config import conf


class Menu:
    def __init__(self):
        self.pixiv = Pixiv()
        self.choices = {
            '1': self.day,
            '2': self.collection,
            '3': self.author,
            '4': self.search,
        }

        self.page_choices = {
            '1': 'all',
            '2': 'page'
        }

        self.daily_mode = {
            '1': 'daily',
            '2': 'daily_r18'
        }

        self.mode = {
            '1': 'all',
            '2': 'safe',
            '3': 'r18'
        }

    def display_menu(self):
        print('''
爬取每日排行榜输入1 （默认下载前50张）
爬取收藏输入2  
爬取作者作品输入3
爬取搜索结果输入4
            ''')

    def run(self):
        self.display_menu()
        choice = input('请输入选项： ')
        action = self.choices.get(choice)
        if action:
            action()
        else:
            print('{0}不是有效操作'.format(choice))

    def day(self):
        while True:
            print('''
请输入选项：
1   普通排行榜
2   r18排行榜
                    ''')
            choice = input('请输入选项： ')
            mode = self.daily_mode.get(choice)
            if choice == '1' or your_choice == '2':
                self.pixiv.day(mode)
            else:
                print('{0}不是有效操作'.format(choice))

    def collection(self):
        while True:
            user_id = input('''
默认为登陆用户
请输入用户id： ''')
            print('''
请输入选项：
1   全部内容
2   自定义页数
默认为全部下载
            ''')
            choice = input('请输入选项： ')

            pages = self.page_choices.get(choice)
            if pages:
                self.pixiv.collection(user_id, pages)
            else:
                print('{0}不是有效操作'.format(choice))

    def author(self):
        while True:
            author_id = input('''
例如：https://www.pixiv.net/member_illust.php?id=3703525&type=all    id=3703525就是作者的id
请输入作者id：''')
    #             print('''
    # 请输入选项：
    # 1   全部内容
    # 2   自定义页数
    #             ''')
    #             choice = input('请输入选项： ')
            if choice == '1' or choice == '2':
                start_page = input('请输入要开始的起始页数：')
                end_page = input('请输入你要结束的页数：')
                self.pixiv.author(author_id, start_page, end_page)

    def search(self):
        keyword = input('请输入关键字：')
        print('''
请选择模式
1   全部
2   普通
3   r18
        ''')
        choice = input('请输入选项：')
        mode = self.mode.get(choice)
        num = int(input('请输入要爬取的前n个作品（按照星数排列）：'))
        self.pixiv.search(keyword, num, mode)


if __name__ == '__main__':
    menu = Menu()
    menu.run()
    time.sleep(100)

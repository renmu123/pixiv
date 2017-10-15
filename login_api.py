# -*- coding:utf8 -*-
import requests
from bs4 import BeautifulSoup
import http.cookiejar as cookielib
from config import headers
import os

class Login:
    def __init__(self):
        self.session = requests.session()
        self.login_url = 'https://accounts.pixiv.net/login'
        self.post_url = 'https://accounts.pixiv.net/api/login?lang=zh'

    #  获取post_key
    def _get_post_key(self):
        r = self.session.get(self.login_url)
        post_key = BeautifulSoup(r.text, 'lxml').find('input', type='hidden')['value']
        return post_key

    # 登陆
    def get_cookie(self):
        account = input('请输入账号：')
        password = input('请输入密码：')
        postdata = {
            'post_key': self._get_post_key(),  # 获取post_key
            'password': password,
            'pixiv_id': account,
        }
        login_page = self.session.post(self.post_url, headers=headers, data=postdata)
        success = login_page.json()['body']
        success_true = {'success': {'return_to': 'https://www.pixiv.net/'}}  # 成功登录的提示
        if success == success_true:
            print(os.getcwd())
            self.session.cookies.save()  # 保存cookie
            print('登陆成功')
        else:
            print('账号或密码错误，请重新登录')
            get_cookie()

    def login(self):
        self.session.cookies = cookielib.LWPCookieJar(filename='cookies')
        try:
            self.session.cookies.load(ignore_discard=True)
            # print('登陆成功')
        except:
            print("Cookie 未能加载")
            self.get_cookie()
        finally:
            return self.session


if __name__ == '__main__':
    login()

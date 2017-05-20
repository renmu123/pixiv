# -*- coding: utf-8 -*-
# author renmu
# blog www.irenmu.xyz
# v1.0 实现爬取今日榜
# 多线程
# 模块化
# 保存的文件夹不存在退出
# 增加爬取个人收藏入口
# - - - - - - - - - - - - - - 代增加的功能
# 增加多种命名方式
# 增加根据画师下载

import requests
from bs4 import BeautifulSoup
import http.cookiejar as cookielib
import os
import time

# 确认输入路径是否存在
def comfirm_path(save_txt):
    path = input('请输入要保存的地址：')
    if not os.path.exists(path):
        print('你输入的地址不存在，请重新输入')
        comfirm_path()
    else:
        f = open(save_txt, 'w')
        f.write(path)
        f.close()
    return path

# 自定义输入保存路径
def path_save(save_txt):
    if os.path.isfile(save_txt):
        f = open(save_txt, 'r')
        path = f.read()
        f.close()
        return path
    else:
        path = comfirm_path(save_txt)
        return path

#登录
def login():
    account = input('请输入账号：')
    password = input('请输入密码：')
    postdata = {
        'post_key': get_post_key(),
        'password': password,
        'pixiv_id': account,
        # 'return_to': 'https://www.pixiv.net/'
    }
    login_page = session.post('https://accounts.pixiv.net/api/login?lang=zh', headers=headers, data=postdata)
    aaa = login_page.json()['body']
    bbb = {'success': {'return_to': 'https://www.pixiv.net/'}}  #成功登录的提示
    # print(aaa)
    if aaa == bbb:
        os.chdir(pro_path)
        print(pro_path)
        session.cookies.save()  # 保存cookie
        os.chdir(path)
        os.chdir(now_time)
    else:
        print('账号或密码错误，请重新登录')
        login()

#获取post_key
def get_post_key():
    url = 'https://accounts.pixiv.net/login'
    start_url = session.get(url)
    post_key = BeautifulSoup(start_url.text,'lxml').find('input', type = 'hidden')['value']
    # print(post_key)
    return post_key

# 处理下载单幅图片
def one_pic_download(url, id):
    real_page = session.get(url)
    real_page_img = BeautifulSoup(real_page.text, 'lxml').find_all('div', class_='wrapper')[-1].find('img')['data-src']  # 非漫画的地址
    # print(real_page_img) #原图地址
    pic = real_page_img[-4:]  # 扩展名
    if os.path.isfile(id + pic):  # 如果文件存在就跳过
        # print('跳过')
        return True
    img = session.get(real_page_img, headers=img_headers)
    f = open(id + pic, 'ab')
    f.write(img.content)
    f.close()

# 处理漫画套图
def manga_download(url, id):
    # 漫画套图
    manga_url = url.replace('medium', 'manga')
    manga_page = session.get(manga_url)
    manga_page_imgs = BeautifulSoup(manga_page.text, 'lxml').find_all('img', class_='image ui-scroll-view')
    page_number = 0
    if os.path.exists(id):
        os.chdir(id)
        # print('文件夹已存在，继续执行')
    else:
        os.mkdir(id)
        os.chdir(id)

    for manga_page_img in manga_page_imgs:
        page_number += 1
        manga_page_img_url = manga_page_img['data-src']
        # print(manga_page_img_url)
        pic = manga_page_img_url[-4:]  # 扩展名
        if os.path.isfile(id + '_' + str(page_number) + pic):  # 如果文件存在就跳过
            # print('    文件已存在')
            continue
        img = session.get(manga_page_img_url, headers=img_headers)
        f = open(id + '_' + str(page_number) + pic, 'ab')
        f.write(img.content)
        f.close()

session = requests.session()
#第一次登陆后加载保存在本地的cookies
n = 0
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
    print('cookie加载成功')
    n =1
except:
    print("Cookie 未能加载")

headers = {
    "Host": "accounts.pixiv.net",
    "Referer": "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Origin': 'https://accounts.pixiv.net'
}

img_headers = {
        "Host": "i.pximg.net",
        "Referer": "https://www.pixiv.net",  # 图片服务器的headers referer是关键
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    }

# 每日热点
def day():
    url = 'https://www.pixiv.net/ranking.php?mode=daily'
    login = session.get(url)
    num = 1 #计数
    pages = BeautifulSoup(login.text, 'lxml').find('div', class_ = 'ranking-items adjust').find_all('div', class_ = '_layout-thumbnail')

    for page in pages:
        id = page.find('img')['data-id']  # 获取图片id
        print('正在下载中%s/50' % num)
        num += 1
        url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + id  # id页面
        # print(url)
        try:
            # 单幅图片处理
            one_pic_download(url, id)
        except:
            manga_download(url, id)
            os.chdir( path ) #返回当前日期的根文件夹
            os.chdir(now_time)
            continue



    print('下载完成')
    time.sleep(1000)

# 个人收藏
def collection (col_page):
    url = 'https://www.pixiv.net/bookmark.php?rest=show&type=illust_all&p=' + col_page
    login = session.get(url)
    num = 1  # 计数
    pages = BeautifulSoup(login.text, 'lxml').find('div', class_= 'display_editable_works').find_all('div',class_= '_layout-thumbnail')
    os.chdir(path)
    for page in pages:
        id = page.find('img')['data-id']
        print('正在下载中%s/20' % num)
        num += 1
        url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + id  # id页面
        # print(url)
        try:
            one_pic_download(url, id)
        except:
            manga_download(url, id)

            os.chdir(path)
            continue

    print('''
        下载完一页啦
    ''')

# 作者id下载
def author(col_page, path, author_id):
    url = 'https://www.pixiv.net/member_illust.php?id=' + author_id +  '&type=all&p=' + col_page  #作者页
    login =session.get(url)
    num = 1
    name = BeautifulSoup(login.text,'lxml').find('a', class_='user-link').find('h1', class_='user').get_text()
    try:
        os.mkdir(name)
        os.chdir(name)
    except:
        os.chdir(name)
        pass
    pages = BeautifulSoup(login.text,'lxml').find_all('li', class_='image-item')
    for page in pages:
        id = page.find('img')['data-id']
        print('正在下载中%s/20' % num)
        num += 1
        url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + id  # id页面
        # print(url)
        try:
            one_pic_download(url, id)
        except:
            manga_download(url, id)
            os.chdir(path)
            os.chdir(name)
            continue

    print('''
            下载完一页啦
        ''')


if __name__ == '__main__':
    if n == 1:
        print('你已经登录')
    else:
        print('你尚未登录')
        login()


    choice = input('''
    如果要爬取每日图片请输入day,
    如果要爬取你的收藏请输入collection  
    如果要爬去某作者的图片请输入author   
    ''')

    if choice == 'day':
        path = path_save('day_txt.txt')  # 自定义输入保存路径
        pro_path = os.getcwd()  # 源文件运行地址
        os.chdir(path)
        now_time = time.strftime('%Y-%m-%d')
        if os.path.exists(now_time):
            os.chdir(now_time)
            # print('文件夹已存在，继续执行')
        else:
            os.mkdir(now_time)
            os.chdir(now_time)

        day()
    elif choice == 'collection':
        path = path_save('con_txt.txt')  # 自定义输入保存路径
        pro_path = os.getcwd()  # 源文件运行地址
        os.chdir(path)
        start_page = int(input('请输入要开始的起始页数：'))
        end_page = int(input('请输入你要结束的页数：'))
        print('开始下载')
        for col_page in range(start_page, end_page+1):
           collection(str(col_page))  #collection 函数
           os.chdir(path)
        print('下载结束')

    elif choice == 'author':
        path = path_save('author_txt.txt')
        pro_path = os.getcwd()
        os.chdir(path)
        author_id = input('''
    请输入作者id
    例如：https://www.pixiv.net/member_illust.php?id=3703525&type=all    id=3703525就是作者的id
    ''')
        start_page = int(input('请输入要开始的起始页数：'))
        end_page = int(input('请输入你要结束的页数：'))
        print('开始下载')
        for col_page in range(start_page, end_page + 1):
            author(str(col_page), path, str(author_id) )
            os.chdir(path)
        print('下载结束')
   # day()

    # collection()












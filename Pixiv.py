# -*- coding: utf-8 -*-
# author renmu
# blog www.irenmu.xyz
# v1.0 实现爬取今日榜
# 多线程
import requests
from bs4 import BeautifulSoup
import http.cookiejar as cookielib
import os
import time

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

agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
headers = {
    "Host": "accounts.pixiv.net",
    "Referer": "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Origin': 'https://accounts.pixiv.net'
}
#自定义输入保存路径
if os.path.isfile('path_txt.txt'):
    f = open('path_txt.txt', 'r')
    path = f.read()
    f.close()

else:
    path = input('请输入要保存的地址：')
    f = open('path_txt.txt','w')
    f.write(path)
    f.close()

#文件保存路径
pro_path = os.getcwd() #源文件运行地址
print(pro_path)
os.chdir(path)
now_time = time.strftime('%Y-%m-%d')
if os.path.exists(now_time):
    os.chdir(now_time)
    # print('文件夹已存在，继续执行')
else:
    os.mkdir(now_time)
    os.chdir(now_time)

#获取post_key
def get_post_key():
    url = 'https://accounts.pixiv.net/login'
    start_url = session.get(url)
    post_key = BeautifulSoup(start_url.text,'lxml').find('input', type = 'hidden')['value']
    # print(post_key)
    return post_key

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
    bbb = {'success': {'return_to': 'https://www.pixiv.net/'}}
    print(aaa)
    if aaa ==bbb:
        os.chdir(pro_path)
        session.cookies.save()  # 保存cookie
        os.chdir(path)
        os.chdir(now_time)
    else:
        print('账号或密码错误，请重新登录')
        login()


#确认是否已经登录
def islogin():
    return True

#下载函数
def download():
    pass
#主函数
def main():
    #每日热点
    url = 'https://www.pixiv.net/ranking.php?mode=daily'
    login = session.get(url)
    num = 1 #计数
    img_headers = {
        "Host": "i.pximg.net",
        "Referer": "https://www.pixiv.net",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    }
    pages = BeautifulSoup(login.text, 'lxml').find('div', class_ = 'ranking-items adjust').find_all('div', class_ = '_layout-thumbnail')

    for page in pages:
        # img_url = id.find('img')['data-src'].replace('240x480', '600x600')
        # print(img_url)
        id = page.find('img')['data-id']
        print('正在下载中%s/50' % num)
        num += 1
        url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + id  #id页面
        # print(url)
        try:
            real_page = session.get(url)
            real_page_img = BeautifulSoup(real_page.text, 'lxml').find_all('div', class_ = 'wrapper')[-1].find('img')['data-src'] #非漫画的地址
            # print(real_page_img) #原图地址
        except:
            #漫画套图
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
                page_number+=1
                manga_page_img_url = manga_page_img['data-src']
                # print(manga_page_img_url)
                pic = manga_page_img_url[-4:] # 扩展名
                if os.path.isfile(id + '_' + str(page_number) + pic):  # 如果文件存在就跳过
                    # print('    文件已存在')
                    continue
                img = session.get(manga_page_img_url, headers=img_headers)
                f = open(id + '_' + str(page_number) + pic, 'ab')
                f.write(img.content)
                f.close()
            os.chdir( path ) #返回当前日期的根文件夹
            os.chdir(now_time)
            continue

        pic = real_page_img[-4:]  # 扩展名
        if os.path.isfile(id + pic) : #如果文件存在就跳过
            # print('文件已存在')
            continue
        img = session.get(real_page_img, headers = img_headers)
        f = open(id + pic, 'ab')
        f.write(img.content)
        f.close()
    print('下载完成')



if __name__ == '__main__':
    if n == 1:
        print('你已经登录')
    else:
        print('尚未登录')
        login()

    main()













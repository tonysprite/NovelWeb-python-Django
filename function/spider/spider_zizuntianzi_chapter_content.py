'''
从表novel_info中拿到小说章节的id，剩下的章节id从网页上获取，最后组成url，开始爬取
'''
from pydoc import doc
import time
import pymysql
from threading import Thread
from selenium import webdriver
from pyquery import PyQuery as pq
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re

url = 'https://www.sxu3xs.com/read/6491_25778523.html'
browser = webdriver.Chrome()

db = pymysql.connect(host='localhost', user='root', password='12345678', port=3306, db='spider')
cursor = db.cursor()
sql = "INSERT INTO charpter_detail(charpter_id,charpter_content,charpter_name) values(%s,%s,%s)"

def get_100_novel_id():
    novel_ids = [6491]
    # sql = 'SELECT id FROM novel_info LIMIT 880,6966'
    # cursor.execute(sql) #result是共有多少条结果
    # result = cursor.fetchall() #数据类型是元组,可迭代类型数据

    # for data in result:
    #   novel_ids.append(data)

    return novel_ids

#组成小说页面的url
def make_novel_url(novel_ids):
    urls = []
    for id in novel_ids:
        url = "https://www.sxu3xs.com/book/"+str(id)+".html"
        print(url)
        urls.append(url)
    return urls

#点击目录链接
def click_href(url):
    try:
        browser.get(url)
        wait = WebDriverWait(browser, 20)
        # 显示等待,小说页面加载完成
        # content_click = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'list-charts'))).click()
        # content_click = wait.until(EC.element_to_be_clickable(doc.find_element_by_path('')))
        # browser.find_element_by_link_text('目录').click()
        # time.sleep(4)
        # contents = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.container>.row>.col-sm-12>.panel>.panel-body>.list-group>li>a'))).click()
        # contents_next_page = wait.until(EC.presence_of_all_elements_located((By.LINK_TEXT,'下一篇'))).click()
        html = browser.page_source
        return html
    except:
        html = click_href(url)
        return html


#拿到免费章节的相应信息,id,name.组成相应的url。
def get_charpter_info(html):
    datas=[]
    doc = pq(html)
    li_list=doc('.container>.row>.col-sm-12>.panel>.panel-body>.list-group>li').items()
    for li in li_list:
        link = "https://www.sxu3xs.com"+li.find('a').attr('href')
        link_arr = re.split("/|_|\.",link)
        name = li.find('a').text()
        data={
            'charpter_id':link_arr[7],
            'charpter_name':name,
            'content_href':link,
        }
        datas.append(data)
    # print('基本信息保存完成')
    return datas


#插入charpter_content并保存到MYSQL数据库
def insert_charpterContent_and_save(datas):
    for data in datas:
        charpter_url = data['content_href']
        # print(charpter_url)
        print("====================开始下载章节"+data['charpter_name']+"==================")
        content = get_one_charpter_content(charpter_url)
        data['charpter_content'] = content
        print("====================完成下载章节"+data['charpter_name']+"==================")
        save_to_MYSQL(data)


#装饰器，给get_one_cahrpter_content(url)函数新增功能
def time_limited_pri(time_limited):
    def wrapper(func):  #接收的参数是函数
        def __wrapper(params):
            class TimeLimited(Thread):  #class中的两个函数是必须的
                def __init__(self):
                    Thread.__init__(self)

                def run(self):
                    func(params)

            t = TimeLimited()
            t.setDaemon(True)  #这个用户线程必须设置在start()前面
            t.start()
            t.join(timeout=time_limited)
            if t.is_alive():
                raise Exception('连接超时')

        return __wrapper

    return wrapper

#获取免费章节的文本内容
@time_limited_pri(86400)
def get_one_charpter_content(url):
    try:
        browser.get(url)
        wait = WebDriverWait(browser, 120)
        contents = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'content-ext')))
        # time.sleep(2)
        html = browser.page_source
        doc = pq(html)
        content = doc('.content-ext').text().replace("扫码↓↓↓下载本站官方app妙阅小说，精彩好书在线手机阅读，打开手机绝不迷路!","\n\n")
        print(content)
        # data['novel_id'] = doc('#main').attr('bookid')
        # print(data['novel_id'])
        return content
    except:
        content = get_one_charpter_content(url)
        return content


#将数据插入到数据库，一次只插入一条
def save_to_MYSQL(new_data):
    try:
        cursor.execute(sql, (new_data['charpter_id'],new_data['charpter_content'],new_data['charpter_name']))
        db.commit()
        print('插入数据成功',new_data['charpter_name'])
    except Exception as e:
        print('插入数据失败！！',e)
        db.rollback()



if __name__ == '__main__':
    ids = get_100_novel_id()
    urls = make_novel_url(ids)
    print(urls)
    count = 0
    for url in urls:
        count += 1
        html = click_href(url)
        datas = get_charpter_info(html)
        try:
            insert_charpterContent_and_save(datas)  #循环拿到章节url,然后爬取数据
        except Exception as e:
            print('跳出这一层循环',e)
            continue

        print('第%s部小说保存完成\n'%count)

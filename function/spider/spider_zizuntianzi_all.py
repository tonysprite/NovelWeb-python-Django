'''
Author: tonysprite tangli53@gome.com.cn
Date: 2022-08-23 19:01:22
LastEditors: tonysprite tangli53@gome.com.cn
LastEditTime: 2022-08-23 20:07:02
FilePath: /NovelWeb-python-Django/function/spider/spider_zizuntianzi_all.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from genericpath import exists
from pydoc import doc
from threading import Thread
from selenium import webdriver
from pyquery import PyQuery as pq
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re

browser = webdriver.Chrome()
#点击目录链接
def click_href(url):
    try:
        browser.get(url)
        wait = WebDriverWait(browser, 60)
        # 显示等待,小说页面加载完成
        # content_click = wait.until(EC.element_to_be_clickable((By.LINK_TEXT,'下一篇'))).click()
        # browser.find_element_by_link_text('目录').click()
        # time.sleep(4)
        # contents = wait.until(EC.presence_of_element_located((By.LINK_TEXT, '下一篇')))
        html = browser.page_source
        return html
    except:
        html = click_href(url)
        return html

#获取免费章节的文本内容
def get_one_charpter_content(url):
    try:
        html=click_href(url)
        doc = pq(html)
        content = doc('.content-ext').text().replace("扫码↓↓↓下载本站官方app妙阅小说，精彩好书在线手机阅读，打开手机绝不迷路!","\n\n")
        title = doc('.panel-heading').text()
        print(title+"\n\n")
        print(content)
        sleep(2)
        url="https://www.sxu3xs.com"+doc('.next>.btn-info').attr('href')
        # print("next page url:"+url)
        if url:
            # print("has next page")
            get_one_charpter_content(url)

        return content
    except:
        content = get_one_charpter_content(url)
        return content
if __name__ == '__main__':
    # url="https://www.sxu3xs.com/read/6491_25778523.html"
    # url="https://www.sxu3xs.com/read/6491_25794305.html"
    # url="https://www.sxu3xs.com/read/6491_26759334.html"
    url="https://www.sxu3xs.com/read/6491_27073940.html"
    get_one_charpter_content(url)



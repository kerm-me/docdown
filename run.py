from threading import activeCount
from tkinter import image_names
from playwright.sync_api import Playwright, sync_playwright
import time
from bs4 import BeautifulSoup
import requests
import img2pdf
import sys

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    # context = browser.new_context(storage_state="./peer2profit")
    context = browser.new_context()

    # Open new page
    page = context.new_page()
    url = sys.argv[1]
    # url = 'https://max.book118.com/html/2017/1105/139064432.shtm'
    imagepath = []
    page.goto(url)
    # 直接下滑页面到底部
    while True:
        try:
            el = page.query_selector("//button[@id='btn_preview_remain']").click() 
        except:
            break

                # for i in range(15):
                # page.keyboard.press("PageDown")
                # time.sleep(1.5)

    # 处理下载链接，为防止错误，这里再次进行下拉操作
    # 直接全部下拉完成再进行获取似乎不行，尝试一张一张获取
    # for i in range(20):
    #     page.keyboard.press("PageDown")
    #     time.sleep(1.5)
    divs = page.query_selector_all("//div[@class='webpreview-item']")
    for div in divs:
        # div.focus()
        div.scroll_into_view_if_needed()
        while True:
            time.sleep(1)
            try:
                inner = div.inner_html()
                soup = BeautifulSoup(inner,'lxml')
                imgurl = soup.img.attrs['src']
                break
            except:
                pass
        # imgurl = soup.attrs['src']
        # print(soup.prettify())
        # 注意这里的soup之后自动添加了头尾，所以需要手动定位到img标签上，获取这个元素的信息，然后使用attrs获取属性字典，最后使用src获取内容
        # try
        dir = imgurl[-10:]
        imagepath.append(dir)
        file = requests.get('https:'+imgurl)
        with open(dir,"wb") as code:
            code.write(file.content)
    context.close()
    browser.close()
    # 生成pdf
    with open("download.pdf","wb") as f:
	    f.write(img2pdf.convert(imagepath))
# 版权声明：本文为CSDN博主「卓晴」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/zhuoqingjoking97298/article/details/110222668


with sync_playwright() as playwright:
    # print(os.getcwd())
    run(playwright)

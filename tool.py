from playwright.sync_api import Playwright, sync_playwright
import time
from bs4 import BeautifulSoup
import requests
import img2pdf
import base64
import os

# 使用 canvas 进行截图
def handle_docin(page):
    imagepath = []
    command = """id => {
                elements = document.getElementsByTagName('canvas')[id] 
                return elements.toDataURL("image/png")};"""
    divs = page.query_selector_all("//div[@class='model panel scrollLoading']")
    for i in range(len(divs)) :
        divs[i].scroll_into_view_if_needed()
        while True:
            try:
                time.sleep(0.5)
                data = page.evaluate(command,i)
                image_base64 = data.split(",")[1]
                image_bytes = base64.b64decode(image_base64) 
                imagepath.append(str(i)+'.png')
                break
            except:
                pass
        with open(str(i)+'.png',"wb") as code:
            code.write(image_bytes)
    return imagepath

# 使用screenshot进行截图
def handle_baidu(page):
    imagepath = []
    page.query_selector("//span[@class='read-all']").click()
    for i in ['reader-topbar','sidebar-wrapper','tool-bar-wrapper','fold-page-content','theme-enter-wrap','search-box-wrapper','doc-info-wrapper','header-wrapper']:
        page.evaluate('document.querySelector(".{}").remove()'.format(i))
    divs = page.query_selector_all("//canvas")
    for i in range(len(divs)) :
        divs[i].scroll_into_view_if_needed()
        while True:
            try:
                time.sleep(1)
                divs[i].screenshot(path=str(i)+'.jpeg',quality=100,type='jpeg')
                imagepath.append(str(i)+'.jpeg')
                break
            except Exception as e:
                print(str(e))
                pass
    return imagepath

# 直接下载图片
def handle_book118(page):
    imagepath = []
    file_type = 'None'
    while True:
        try:
            page.query_selector("//button[@id='btn_preview_remain']").click()
            time.sleep(0.2)
        except:
            break
    file_type = page.query_selector("//*[@id='main']/div[1]/div[1]/div/i").get_attribute('class')[-3:]

    if file_type in ['doc','ocx','pdf']:
        divs = page.query_selector_all("//div[@class='webpreview-item']")
        for i in range(len(divs)):
            divs[i].scroll_into_view_if_needed()
            while True:
                time.sleep(0.5)
                try:
                    inner = divs[i].inner_html()
                    soup = BeautifulSoup(inner,'lxml')
                    imgurl = soup.img.attrs['src']
                    break
                except:
                    pass
            dir = str(i)+'.png'
            imagepath.append(dir)
            file = requests.get('https:'+imgurl)
            with open(dir,"wb") as code:
                code.write(file.content)

    elif file_type in ['ppt','ptx']:
        page.query_selector("//button[@id='btn_preview_remain']").click()
        time.sleep(1.5)
        try:
            framelink = page.wait_for_selector("//iframe").content_frame().url
            print('您可以直接访问PPT预览（无广告）：\n'+framelink)
            page.goto(framelink)
            time.sleep(1.5)
            nums = int(page.locator("//span[@id='PageCount']").inner_text())
            while True:
                time.sleep(0.1)
                page.locator("//div[@class='btmRight']").click()
                if int(page.locator("//span[@id='PageIndex']").inner_text()) == nums:
                    for i in range(10):
                        time.sleep(0.1)
                        page.locator("//div[@class='btmRight']").click()
                    break
            for i in range(nums+1):
                time.sleep(0.5)
                pageid = int(page.locator("//span[@id='PageIndex']").inner_text())
                page.locator("//div[@id='slide"+str(pageid-1)+"']").screenshot(path=str(pageid)+".png")
                imagepath.append(str(pageid)+'.png')
                page.locator("//div[@id='pagePrev']").click()
            imagepath.reverse()
        except Exception as e :
            print(str(e))
            print('下载PPT失败，请至GitHub提交issue，附上下载链接')

    return imagepath

def download_from_url(url):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.set_viewport_size({"width": 800, "height": 800})
        page.goto(url)
        time.sleep(1)
        title = page.query_selector("//title").inner_text()

        if url[8:18]=='www.docin.':
            imagepath = handle_docin(page)
        elif url[8:18]=='wenku.baid':
            imagepath = handle_baidu(page)
        elif url[8:18]=='max.book11':
            imagepath = handle_book118(page)

        temp=[]
        [temp.append(i) for i in imagepath if not i in temp]
        imagepath = temp
        context.close()
        browser.close()
        filename_ = title + ".pdf"
        try:
            with open(filename_,"wb") as f:
                f.write(img2pdf.convert(imagepath))
        except:
            print("下载失败，请注意关闭代理，如果还有问题，请至GitHub提交issue，附上下载链接")
        for image in imagepath:
            os.remove(image)
        return filename_

download_from_url('https://max.book118.com/html/2017/1105/139064432.shtm')
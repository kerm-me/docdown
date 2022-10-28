from PIL import Image
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
                return elements.toDataURL("image/jpeg")};"""
    divs = page.query_selector_all("//div[@class='model panel scrollLoading']")
    for i in range(len(divs)):
        divs[i].scroll_into_view_if_needed()
        while True:
            try:
                time.sleep(0.5)
                data = page.evaluate(command, i)
                image_base64 = data.split(",")[1]
                image_bytes = base64.b64decode(image_base64)
                imagepath.append(str(i) + '.jpg')
                break
            except:
                pass
        with open(str(i) + '.jpg', "wb") as code:
            code.write(image_bytes)
    return imagepath


# 使用screenshot进行截图
def handle_baidu(page):
    imagepath = []
    page.query_selector("//span[@class='read-all']").click()
    for i in ['reader-topbar', 'sidebar-wrapper', 'tool-bar-wrapper', 'fold-page-content', 'theme-enter-wrap',
              'search-box-wrapper', 'doc-info-wrapper', 'header-wrapper']:
        page.evaluate('document.querySelector(".{}").remove()'.format(i))
    divs = page.query_selector_all("//canvas")
    for i in range(len(divs)):
        divs[i].scroll_into_view_if_needed()
        while True:
            try:
                time.sleep(1)
                divs[i].screenshot(path=str(i) + '.jpeg', quality=100, type='jpeg')
                imagepath.append(str(i) + '.jpeg')
                break
            except Exception as e:
                print(str(e))
                pass
    return imagepath


# 直接下载图片
def handle_book118(page):
    imagepath = []
    file_type = 'None'
    file_type = page.query_selector("//*[@id='main']/div[1]/div[1]/div/i").get_attribute('class')[-3:]

    if file_type in ['doc', 'ocx', 'pdf']:
        while True:
            try:
                page.query_selector("//button[@id='btn_preview_remain']").click()
                time.sleep(0.2)
            except:
                break
        divs = page.query_selector_all("//div[@class='webpreview-item']")
        for i in range(len(divs)):

            divs[i].scroll_into_view_if_needed()
            while True:
                time.sleep(0.5)
                try:
                    inner = divs[i].inner_html()
                    soup = BeautifulSoup(inner, 'lxml')
                    imgurl = soup.img.attrs['src']
                    break
                except:
                    pass

            dir = str(i) + '.jpg'

            imagepath.append(dir)
            file = requests.get('https:' + imgurl)
            with open(dir, "wb") as code:
                code.write(file.content)

    elif file_type in ['ppt', 'ptx']:
        page.query_selector("//button[@id='btn_preview_remain']").click()
        time.sleep(1.5)
        try:
            framelink = page.wait_for_selector("//iframe").content_frame().url
            print('您可以直接访问PPT预览（无广告）：\n' + framelink)
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
            for i in range(nums + 1):
                time.sleep(0.5)
                pageid = int(page.locator("//span[@id='PageIndex']").inner_text())

                page.locator("//div[@id='slide" + str(pageid - 1) + "']").screenshot(path=str(pageid) + ".jpg")
                imagepath.append(str(pageid) + '.jpg')

                page.locator("//div[@id='pagePrev']").click()
            imagepath.reverse()
        except Exception as e:
            print(str(e))
            print('下载PPT失败，请至GitHub提交issue，附上下载链接')

    return imagepath


def handle_doc88(page):
    import re
    imagepath = []
    file_type = 'None'
    file_type = re.findall("格式：([a-zA-Z]*)", page.query_selector("//*[@id='box1']/div/div/div[1]").text_content())[
        0].lower()

    while True:
        try:
            page.query_selector("//*[@id='continueButton']").click()
            time.sleep(0.2)
        except AttributeError:
            break
        except Exception as e:
            print(f'some error occured：{e}')

    js = """id => {var temp = document.getElementsByTagName("canvas")[id].getAttribute("lz")
    if (temp==null){
        return false
    }else{return document.getElementsByTagName("canvas")[id].toDataURL("image/jpeg")}
    };"""

    data = False
    divs = page.query_selector_all("//div[@class='outer_page']")
    for i in range(len(divs)):
        divs[i].scroll_into_view_if_needed()
        while True:

            try:
                # 检测是否加载完成
                while not data:
                    time.sleep(0.5)
                    data = page.evaluate(js, i * 2 + 1)
                image_base64 = data.split(",")[1]
                image_bytes = base64.b64decode(image_base64)
                imagepath.append(str(i) + '.jpg')

                break
            except:
                pass
        with open(str(i) + '.jpg', "wb") as code:
            code.write(image_bytes)

    return imagepath


def download_from_url(url):
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=False)
        except:
            browser = playwright.webkit.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.set_viewport_size({"width": 800, "height": 800})
        page.goto(url)
        time.sleep(1)
        title = page.query_selector("//title").inner_text()

        if url[8:18] == 'www.docin.':
            imagepath = handle_docin(page)
        elif url[8:18] == 'wenku.baid':
            imagepath = handle_baidu(page)
        elif url[8:18] == 'max.book11':
            imagepath = handle_book118(page)
        elif url[8:18] == 'www.doc88.':
            imagepath = handle_doc88(page)

        temp = []
        [temp.append(i) for i in imagepath if not i in temp]
        imagepath = temp
        context.close()
        browser.close()
        filename_ = title + ".pdf"

        # 将图片中alpha透明通道删除
        for image in imagepath:
            img = Image.open(image)
            # 将PNG中RGBA属性变为RGB，即可删掉alpha透明度通道
            img.convert('RGB').save(image)
            img.close()

        try:
            with open(filename_, "wb") as f:
                f.write(img2pdf.convert(imagepath))
        except Exception as e:
            print("下载失败，请注意关闭代理，如果还有问题，请至GitHub提交issue，附上下载链接")
            print(e)
        # 删除图片
        for image in imagepath:
            os.remove(image)
        return filename_


if __name__ == '__main__':
    #测试用
    url = ''
    download_from_url(url)
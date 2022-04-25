from playwright.sync_api import Playwright, sync_playwright
import time
from bs4 import BeautifulSoup
import requests
import img2pdf
import sys
import base64
import os


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    # context = browser.new_context(storage_state="./peer2profit")
    context = browser.new_context()
    # Open new page
    page = context.new_page()
    url = sys.argv[1]
    # url = 'https://max.book118.com/html/2019/0929/6203012025002111.shtm'
    # url = 'https://max.book118.com/html/2017/1105/139064432.shtm'
    imagepath = []
    # 设置界面的大小，防止截图的时候分辨率过低。
    page.set_viewport_size({"width": 800, "height": 800})
    page.goto(url)
    time.sleep(1)
    title = page.query_selector("//title").inner_text()
    if url[8:18]=='www.docin.':
        # 如果是docin豆丁网
        # 执行js命令，获取canvas内容，下载，参考：https://blog.csdn.net/birdnet5/article/details/119170101
        # 注意todata只能对canvas元素使用，否则会报错not function：https://stackoverflow.com/questions/8667458/todataurl-not-a-function
        command = """id => {
        elements = document.getElementsByTagName('canvas')[id] 
        return elements.toDataURL("image/png")};"""
        divs = page.query_selector_all("//div[@class='model panel scrollLoading']")

        for i in range(len(divs)) :
            divs[i].scroll_into_view_if_needed()
            # 等待时间2秒，可以自己调节
            # time.sleep(1)
            #playwright执行js命令 https://playwright.dev/python/docs/evaluating
            while True:
                try:
                    time.sleep(0.5)
                    data = page.evaluate(command,i)
                    image_base64 = data.split(",")[1]      # 获得base64编码的图片信息
                    image_bytes = base64.b64decode(image_base64) 
                    imagepath.append(str(i)+'.png')
                    break
                except:
                    pass
            #按序号进行存储
            with open(str(i)+'.png',"wb") as code:
                code.write(image_bytes)
    elif url[8:18]=='max.book11':
        # page.query_selector("//i[@class='icon icon-format icon-format-ppt']").is_visible()
        # 需要判断PPT或docx
        try:

            page.query_selector("//i[@class='icon icon-format icon-format-docx']").is_visible()
            # 直接下拉到底
            while True:
                try:
                    el = page.query_selector("//button[@id='btn_preview_remain']").click()  
                except:
                    break

            # 处理下载链接，为防止错误，这里再次进行下拉操作
            # 直接全部下拉完成再进行获取似乎不行，尝试一张一张获取
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
                # 注意这里的soup之后自动添加了头尾，所以需要手动定位到img标签上，获取这个元素的信息，然后使用attrs获取属性字典，最后使用src获取内容
                # try
                dir = str(i)+'.png'
                imagepath.append(dir)
                file = requests.get('https:'+imgurl)
                with open(dir,"wb") as code:
                    code.write(file.content)
        except:
            try:
                page.query_selector("//i[@class='icon icon-format icon-format-ppt']").is_visible()
                page.query_selector("//button[@id='btn_preview_remain']").click()
                time.sleep(1.5)
                try:
                    
                    # 注意这里的预览界面实际上是写在一个iframe里面，所以虽然界面元素上有这些元素，但是直接使用selector是获取不了的。
                    # 要单独对iframe进行处理。由于iframe实际上相当于一个独立的网页，所以这里考虑的是直接获取链接之后访问，比较方便，
                    # 截图的效果也比较好。
                    # 对于iframe的处理，playwright提供了frame、frames、frame_locator等方案，但是这些方法都不是很好用，
                    # 使用这些方法得到的结果很多操作都不能够进行，算是一个残废。
                    # 这里是用的content的方法，参考：https://thompson-jonm.medium.com/handling-iframes-using-python-and-playwright-da46d1c64196
                    framelink = page.wait_for_selector("//iframe").content_frame().url
                    print('您可以直接访问PPT预览（无广告）：\n'+framelink)
                    # frame = page.frame_locator('.preview-iframe').
                    # frame.locator("//span[@id='PageCount']").inner_text()
                    # framelink = page.query_selector("//iframe").get_attribute('src')
                    page.goto(framelink)
                    time.sleep(1.5)
                    # nums = int(frame.locator("//span[@id='PageCount']").inner_text())
                    # # nums = int(page.query_selector("//span[@class='counts']").inner_text()[3:])
                    # for i in range(nums):
                    #     time.sleep(0.5)
                    #     # 此元素应该在界面中，但是无法获取#
                    #     # ipage！
                    #     frame.locator("//div[@id='slide"+str(i)+"']").screenshot(path=str(i)+".png")
                    #     imagepath.append(str(i)+'.png')
                    #     # page.locator(".header").screenshot(path="screenshot.png")
                    #     frame.locator("//div[@id='pageNext']").click()


                    # 比较生草的一点就是这个PPT默认是没有放映动画的，所以直接下载会得到空白。
                    # 如果等待动画一个个放映，不仅判定条件比较难写，而且时间上也会消耗很多，。
                    # 这里考虑的是直接拖到最后一个，然后从后往前进行截取

                    # 获取总页数
                    nums = int(page.locator("//span[@id='PageCount']").inner_text())
                    while True:
                        # 快速点击下一步 跳到最后一页。
                        time.sleep(0.1)
                        page.locator("//div[@class='btmRight']").click()
                        if int(page.locator("//span[@id='PageIndex']").inner_text()) == nums:
                            # 可能有BUG
                            # 防止最后一页还有一堆动画，这里随便设置一个10次，懒得做检测了
                            for i in range(10):
                                time.sleep(0.1)
                                page.locator("//div[@class='btmRight']").click()
                            break
                    # page.locator("//div[@id='pagePrev']").click()
                    # nums = int(page.query_selector("//span[@class='counts']").inner_text()[3:])
                    # 对于这个执行的个数，总之就是非常迷惑，这里多设置一次，防止没有执行完
                    for i in range(nums+1):
                        time.sleep(0.5)
                        # 此元素应该在界面中，但是无法获取#
                        # ipage！
                        pageid = int(page.locator("//span[@id='PageIndex']").inner_text())
                        # 直接使用截图功能
                        page.locator("//div[@id='slide"+str(pageid-1)+"']").screenshot(path=str(pageid)+".png")
                        imagepath.append(str(pageid)+'.png')
                        # page.locator(".header").screenshot(path="screenshot.png")
                        # pageid = int(page.locator("//span[@id='PageIndex']").inner_text())
                        # page.locator("//div[@id='pageNext']").click()
                        page.locator("//div[@id='pagePrev']").click()
                    imagepath.reverse()
                except Exception as e :
                    print(str(e))
                    print('下载PPT失败，请至GitHub提交issue，附上下载链接')
            except:
                print('请至GitHub提交issue，附上下载链接')



    # 通过list set组合降重不能保证其顺序。
    #  https://blog.csdn.net/Jerry_1126/article/details/79843751
    # imagepath = list(set(imagepath))
    temp=[]
    [temp.append(i) for i in imagepath if not i in temp]
    imagepath = temp
    context.close()
    browser.close()
    # 生成pdf
    try:
        with open(title + ".pdf","wb") as f:
            f.write(img2pdf.convert(imagepath))
    except:
        print("转换pdf失败，请至GitHub提交issue，附上下载链接")
    
    #删除文件：https://www.w3school.com.cn/python/python_file_remove.asp
    for image in imagepath:
        os.remove(image)

    
# 版权声明：本文为CSDN博主「卓晴」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/zhuoqingjoking97298/article/details/110222668


with sync_playwright() as playwright:
    # print(os.getcwd())
    run(playwright)


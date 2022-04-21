from threading import activeCount
from django.shortcuts import render
from playwright.sync_api import Playwright, sync_playwright
import time
from bs4 import BeautifulSoup
import requests
import img2pdf
import sys
import base64
import os
from flask import Flask,send_from_directory,render_template
from flask_cors import CORS,cross_origin
from flask_socketio import SocketIO, emit

def run(playwright: Playwright,url) -> None:
    browser = playwright.chromium.launch(headless=True)
    # context = browser.new_context(storage_state="./peer2profit")
    context = browser.new_context()
    # Open new page
    page = context.new_page()
    # url = 'https://max.book118.com/html/2017/1105/139064432.shtm'
    imagepath = []
    page.goto(url)

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
    title = page.query_selector("//title").inner_text()
    
    context.close()
    browser.close()
    filename = title + ".pdf"
    # 生成pdf
    with open(title + ".pdf","wb") as f:
	    f.write(img2pdf.convert(imagepath))
    
    for image in imagepath:
        os.remove(image)
    
    return filename
# 版权声明：本文为CSDN博主「卓晴」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/zhuoqingjoking97298/article/details/110222668

app = Flask(__name__)
app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'
socketio = SocketIO(app)

@cross_origin(origins='*')
@app.route('/download/<string:filename>')
def download_image(filename):
    return send_from_directory(os.getcwd(), path=filename, as_attachment=True)

@cross_origin(origins='*')
@app.route('/')
def index():
    return render_template('index.html')

@cross_origin(origins='*')
@socketio.on('download')
def emit_init_balan(message):
    socketio.emit('start')
    with sync_playwright() as playwright:
        filename = run(playwright,message['url'])
    socketio.emit('done',{'filename':filename})

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")

# DocDown

文档：[DocDown 使用 Playwright 驱动的 豆丁 docin / 原创力文档 book118/ 百度文库 baidu 预览文档下载工具](https://docdown.net/)


使用 playwright 强力驱动的 原创力文档 book118 & 豆丁网 docin & 百度文库 baiduwenku 下载工具。

支持范围：book118 doc ppt pdf，docin doc，百度文库。

## 项目说明

使用 playwright 强力驱动的 原创力文档 book118 & 豆丁网 docin & 百度文库 baiduwenku 下载工具。

支持范围：book118 doc ppt pdf，docin doc，百度文库。

## 使用教程

### 打包版本

[下载链接](https://www.123pan.com/s/czw9-Le3WA)


访问待下载网站，点击预览，复制链接，格式如下；

```
https://max.book118.com/html/2017/1105/139064432.shtm
```

以上面的链接为例，在下载目标文件夹下，右键-在终端中打开（Windows11），按住 Shift+右键-在此处打开 Powershell 窗口（Windows10），然后运行

```Powershell
./docdown 下载链接带英文引号

# 例如：
./docdown 'https://max.book118.com/html/2017/1105/139064432.shtm'
```

之后会弹出浏览器窗口，一段时间后会在目录下生成 PDF 文件。

### 直接运行源码

克隆本项目，安装依赖

```Powershell
pip install -r requirements.txt

# 安装playwright库
pip install playwright

# 安装浏览器驱动文件（安装过程稍微有点慢）
python3 -m playwright install

# 或者（如果上面命令报错）
playwright install
```

访问待下载网站，点击预览，复制链接，格式如下；

```
https://max.book118.com/html/2017/1105/139064432.shtm
```

以上面的链接为例，在项目文件夹下，使用：

```Powershell
## book118
python run.py 'https://max.book118.com/html/2017/1105/139064432.shtm'

# 或者

python3 run.py 'https://max.book118.com/html/2019/0929/6203012025002111.shtm'

## docin
python run.py 'https://www.docin.com/p-1052644960.html'
```

运行将会在运行目录下生成pdf文档。

如果报错`Image contains an alpha channel which will be stored as a separate soft mask (/SMask) image in PDF.`属于正常现象，不影响最终结果。

### 从源码打包

克隆项目，打开 cmd，使用

```Powershell
set PLAYWRIGHT_BROWSERS_PATH=0
playwright install webkit
```

安装 webkit，然后使用 pyinstaller 打包文件`run.py`。

参考：[playwright在pyinstaller下打包](https://www.52pojie.cn/thread-1598055-1-1.html)

## 常见问题

### 使用问题

如果遇到运行错误请先确保以下内容均已注意，再提 issue。

- 注意关闭系统代理。
- 复制粘贴链接时需要打上英文引号`'`。

### 技术问题

目前这些问题无法解决，如果您有好的解决方法请提 issue。

- 部分文档格式不支持。
- 需要付费预览的文档不支持。
- 只支持下载为 PDF 格式（image 转 pdf）。
- 百度文库清晰度较低（Playwright 截图限制）。

## 进阶使用

您可以考虑使用 [百度 OCR](https://ai.baidu.com/tech/ocr) 对下载的 PDF 文档作转文本操作。


# Book118&docin

使用playwright强力驱动的book118&docin&百度文库下载工具。

支持范围：book118 doc ppt pdf，docin doc，百度文库。

## 使用说明

克隆本项目，安装依赖

```
pip install -r requirements.txt

# 安装playwright库
pip install playwright

# 安装浏览器驱动文件（安装过程稍微有点慢）
python3 -m playwright install
```

访问待下载网站，点击预览，复制链接，格式如下；

```
https://max.book118.com/html/2017/1105/139064432.shtm
```

以上面的链接为例，在项目文件夹下，使用：

```
## book118
python run.py 'https://max.book118.com/html/2017/1105/139064432.shtm'

# 或者

python3 run.py 'https://max.book118.com/html/2019/0929/6203012025002111.shtm'

## docin
python run.py 'https://www.docin.com/p-1052644960.html'
```

运行将会在运行目录下生成pdf文档。

如果报错`Image contains an alpha channel which will be stored as a separate soft mask (/SMask) image in PDF.`属于正常现象，不影响最终结果。

import tool
import sys

url = sys.argv[1]
try:
    sleep_time = sys.argv[2]
except:
    sleep_time = 1
tool.download_from_url(url,sleep_time)
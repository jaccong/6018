import requests
import re
import time
taop = ''
newnine = ''
cqyx=''
jsyd=''
from process_channels import process_channel_with_alias
from process_channels import process_multiline_text
from process_channels import CHANNEL_ALIAS_MAP
from channel_sorter import sorter_main
from channel_sorter import custom_order
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def simplify_guangdong(text):
    # 正则匹配：广东开头的任意字符，强制截取前4个字（广东+2个字符）
    pattern = r'(广东.{2})(?:.*?)(?=[,\s]|$)'
    # 替换为捕获的前4个字（核心频道名）
    return re.sub(pattern, r'\1', text)

def simplify_cctv(text):
    # 正则表达式模式：匹配 CCTV-xx 开头的字符串
    # 解释：
    # CCTV-：匹配 "CCTV-" 字面量
    # (\d+)：匹配一个或多个数字（频道号），并捕获为分组1
    # [^\\s]*：匹配零个或多个非空白字符（如 "高清"、"高" 等）
    pattern = r'^CCTV[-]?([0-9]+[+]?[Kk]?)[^\s,]*'
    
    # 使用 re.sub 进行替换，并重定向输出
    simplified_text = re.sub(pattern, r'CCTV\1', text)
    
    return simplified_text

def getget(filename):
  with open(filename, 'r', encoding='utf-8') as file:
    text = file.read()
  return text

def get_source_content(url, selenium_options):
    try:
        print(f"【数据源处理】Selenium 访问：{url}")
        driver = webdriver.Chrome(options=selenium_options)
        driver.get(url)
        time.sleep(6)
        page_content = driver.page_source +"\n"
        driver.quit()
        page_content_lines = page_content.splitlines()
        print(f"【数据源处理】成功获取：{url},整体文本有{len(page_content_lines)}行")
        return page_content
    except Exception as e:
        print(f"【数据源处理】失败：{url}（错误：{str(e)[:50]}）")
        return ""
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/16.1 Safari/604.1",
    "Upgrade-Insecure-Requests":"1",
    "Accept": "test/plain,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive"
    
}
# Selenium配置
selenium_options = Options()
selenium_options.add_argument('--headless=new')
selenium_options.add_argument('--no-sandbox')
selenium_options.add_argument('--disable-dev-shm-usage')
selenium_options.add_argument(f'--user-agent={HEADERS["User-Agent"]}')
selenium_options.add_argument('--blink-settings=imagesEnabled=false')
# 新增：隐藏Selenium自动化特征（核心！防止服务器识别） 
selenium_options.add_argument('--disable-blink-features=AutomationControlled') 
selenium_options.add_experimental_option('excludeSwitches', ['enable-automation']) 
selenium_options.add_experimental_option('useAutomationExtension', False)
with open('test.txt', 'r', encoding='utf-8') as file:
  test = file.read()
  ##test = re.sub(r'\[.*\]Updated\.\,\#genre\#.*','',test,flags=re.DOTALL)
  test = re.sub('parse=1','',test)
  test = re.sub('player=2','',test)
  test = re.sub(r'ua=.*','',test)
  test = re.sub(r'纬来体育.*','',test)
  test = re.sub(r'TVBPlus.*','',test)


##iptv = getlink('')
##itv = getlink('https://kakaxi-1.asia/ipv4.txt')
##gxgx = getget('gxgx.txt')
fmm = get_source_content('https://877622.xyz/m2t.php?url=https://kakaxi-1.asia/ipv6.m3u', selenium_options)
kkxv4 = get_source_content('https://raw.githubusercontent.com/kakaxi-1/IPTV/refs/heads/main/ipv4.txt', selenium_options)
rihou = get_source_content('http://rihou.cc:555/gggg.nzk', selenium_options)
shulao = get_source_content('https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg1', selenium_options)
bcitv = get_source_content('https://877622.xyz/m2t.php?url=https://188766.xyz/itv', selenium_options)
print(bcitv)
aptv = get_source_content('https://877622.xyz/m2t.php?url=https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u', selenium_options)

kx = aptv +kkxv4 + bcitv + rihou + shulao
kx=re.sub(r'&amp;','&',kx)
##kx1 = process_multiline_text(kx, CHANNEL_ALIAS_MAP)

##kx1 = simplify_guangdong(simplify_cctv(kx))
##kxtt = re.findall(r'.*\,.*:\/\/.*',kx1)

all_links=fmm+test
all_links=re.sub(r'[a-zA-Z]+\,',',',all_links)
all_links=re.sub('超清','',all_links)
all_links=re.sub('home','',all_links)
all_links=re.sub('unicome','',all_links)
all_links=re.sub('-4K,',',',all_links)
all_links=re.sub('家里','',all_links)
all_links=re.sub('CGTN','',all_links)
all_links=re.sub('广东广东','广东',all_links)
all_links=re.sub(r'电信|广电','',all_links)
all_links=re.sub(r'少儿卫视.*|广东南方购物.*|XF星空卫视.*','',all_links)
all_links=re.sub(r'（.*）','',all_links)
all_links=re.sub(r'\(.*\)','',all_links)
all_links=re.sub(r'([\u4e00-\u9fff]+)\d+',r'\1',all_links)
all_links=re.sub(r'粤语节目\d*','',all_links)


all_links = process_multiline_text(all_links + kx, CHANNEL_ALIAS_MAP)

total = re.findall(r'.*\,.*:\/\/.*',all_links)
total = sorter_main(total, custom_order)
##print(total)
count=0
gd_keywords = ['广东卫视','广东体育','广东珠江','广东新闻','广东影视','广东民生','广东少儿', '嘉佳卡通', '大湾区卫视']
ys_keywords =['CCTV1', 'CCTV2', 'CCTV3', 'CCTV4', 'CCTV5', 'CCTV6', 'CCTV7', 'CCTV8', 'CCTV9', 'CCTV10', 'CCTV11', 'CCTV12', 'CCTV13', 'CCTV14', 'CCTV15', 'CCTV16', 'CCTV17','CHC家庭影院','CHC动作电影','CHC影迷电影']
gat_keywords = ['TVB翡翠台','无线新闻台','NOW新闻台','中天新闻台','千禧经典台','美亚电影台']
ws_keywords = ['卫视']
remove_keywords = ['smt','smart','Smart','cmvideo','mobile','/rtp/','/udp/']
ws_remove_keywords = remove_keywords + ['大湾区卫视','广东卫视']

with open("108.txt", 'w', encoding='utf-8') as file:
  file.write('广东频道,#genre#\nplayer=2\n')
  for list in total:
    if any(keyword in list for keyword in gd_keywords) and all(key not in list for key in remove_keywords):
      file.write(f'{list}\n')
      count=count+1
  
  file.write('港澳频道,#genre#\nplayer=2\n')
  for list in total:
    if any(keyword in list for keyword in gat_keywords):
      file.write(f'{list}\n')
      count=count+1
  
  file.write('央视频道,#genre#\nplayer=2\n')
  for list in total:
    if any(keyword in list for keyword in ys_keywords) and all(key not in list for key in remove_keywords):
      file.write(f'{list}\n')
      count=count+1
  file.write('卫视频道,#genre#\nplayer=2\n')
  for list in total:
    if any(keyword in list for keyword in ws_keywords) and all(key not in list for key in ws_remove_keywords):
      file.write(f'{list}\n')
      count=count+1
 
  #file.write(getget('ty.txt'))
  #time = re.findall(r'\[.*\:.*\].*\#genre\#.*',test,flags=re.DOTALL)
  time = re.findall(r'\自动更新\,\#genre\#.*',test,flags=re.DOTALL)
  file.write(f'{time[0]}\n')
      ##file.write(f'{test}\n')
      ##file.write(f'{xtext}\n')
      ##file.write(f'{taop}\n')
      ##file.write(f'{newnine}\n')
content = '已更新频道'+str(count)+'个'

import requests
import re
taop = ''
newnine = ''
cqyx=''
jsyd=''
from process_channels import process_channel_with_alias
from process_channels import process_multiline_text
from process_channels import CHANNEL_ALIAS_MAP

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
def getlink(url):
  linktext=''
 
  try:
    linktext = requests.get(url,{'Content-Type':'application/text'},timeout=10).content.decode('utf-8')+'\n'
    #if 'Warning' not in linktext and 'Not Found' not in linktext and 'not found' not in linktext:
    pattern = re.compile(r'(?i)Warning|not found', re.IGNORECASE)
    if not pattern.search(linktext):
      print(f'<<{url}>>———————— O K ')
    else:
      linktext=''
      print(f'<<{url}>>———————— F A L S E ')
  except Exception as e:
    print(f'error:【{e}】')
  return linktext

with open('test.txt', 'r', encoding='utf-8') as file:
  test = file.read()
  ##test = re.sub(r'\[.*\]Updated\.\,\#genre\#.*','',test,flags=re.DOTALL)
  test = re.sub('parse=1','',test)
  test = re.sub('player=2','',test)
  test = re.sub(r'ua=.*','',test)
  test = re.sub(r'纬来体育.*','',test)
  test = re.sub(r'TVBPlus.*','',test)

##iptv = getlink('')
itv = getlink('https://kakaxi-1.asia/ipv4.txt')
##gxgx = getget('gxgx.txt')
fmm = getlink('https://fanmingming.com/txt?url=https://kakaxi-1.asia/ipv6.m3u')
kx = getlink('http://rihou.cc:555/gggg.nzk')
shulao = getlink('https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg1')
bcitv = getlink('https://188766.xyz/itv')
kx=re.sub(r'\S*翡翠\S*\,','翡翠台,',kx)
kx=re.sub(r'\S*千禧经典\S*\,','千禧经典台,',kx)
kx=re.sub(r'\S*美亚电影\S*\,','美亚电影台,',kx)
kx=re.sub(r'广东大湾区','大湾区',kx)
kx=re.sub(r'频备','',kx)
kx=re.sub(r'(高清|标清|超清)','',kx)
kx=re.sub(r'\[.*?\*.*?\]','',kx)

kx=kx + '\n' + bcitv + '\n' + shulao
kx1 = process_multiline_text(kx, CHANNEL_ALIAS_MAP)
##kx1 = simplify_guangdong(simplify_cctv(kx))
kxtt = re.findall(r'.*,http.*',kx1)

all_links=fmm+test+itv
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
all_links=re.sub(r'\S*翡翠\S*\,','翡翠台,',all_links)
all_links=re.sub(r'\S*无线新闻\S*\,','无线新闻台,',all_links)
all_links=re.sub(r'\S*千禧经典\S*\,','千禧经典台,',all_links)
all_links=re.sub(r'\S*美亚电影\S*\,','美亚电影台,',all_links)

total = re.findall(r'.*,http.*',all_links)
totalk = total + kxtt
##print(total)
count=0
gd_keywords = ['广东卫视','广东体育','广东珠江','广东新闻','广东影视','广东民生','广东少儿', '嘉佳卡通', '大湾区卫视', '翡翠台']
with open("108.txt", 'w', encoding='utf-8') as file:
  file.write('广东频道,#genre#\nplayer=2\n')
  for list in totalk:
    if any(keyword in list for keyword in gd_keywords):
      file.write(f'{list}\n')
      count=count+1
  '''
  file.write('港澳频道,#genre#\nplayer=2\n')
  
  for list in totalk:
    if '翡翠' in list or '千禧经典' in list or '美亚电影' in list:
      file.write(f'{list}\n')
      count=count+1
  '''
  file.write('央视频道,#genre#\nplayer=2\n')
  for list in total:
    if 'CCTV' in list or 'CHC' in list:
      file.write(f'{list}\n')
      count=count+1
  file.write('卫视频道,#genre#\nplayer=2\n')
  for list in total:
    if '卫视' in list and '大湾区' not in list and '广东' not in list :
      file.write(f'{list}\n')
      count=count+1
 
  #file.write(getget('ty.txt'))
  time = re.findall(r'\[.*\:.*\].*\#genre\#.*',test,flags=re.DOTALL)
  file.write(f'{time[0]}\n')
      ##file.write(f'{test}\n')
      ##file.write(f'{xtext}\n')
      ##file.write(f'{taop}\n')
      ##file.write(f'{newnine}\n')
content = '已更新频道'+str(count)+'个'

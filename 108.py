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


def fetch_txt(url):
    """
    简单调用：获取目标URL的纯TXT内容并保存
    :param url: 目标TXT地址（必填）
    :param save_path: 保存路径（默认epg.txt）
    :return: 成功返回True，失败返回False
    """
    # 优化后的请求头（强制要TXT）
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/16.1 Safari/604.1",
        "Accept": "text/plain,*/*",  # 只请求TXT，拒绝HTML
        "Connection": "keep-alive"
    }
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.encoding = "utf-8"  # 避免中文乱码
        # 直接保存纯TXT（无HTML标签）
        line_count = len(response.text.splitlines())  # 兼容所有换行符（\n/\r/\r\n）
        print(f"✅ 成功获取{url}内容，📊 文本总行数：{line_count}")
        return response.text+'\n'
    except requests.exceptions.Timeout:
        print(f"❌ 错误：请求超时（超过15秒）")
        return None
    except requests.exceptions.ConnectionError:
        print(f"❌ 错误：网络连接失败")
        return None
    except Exception as e:
        print(f"❌ 错误：{str(e)}")
        return None
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
fmm = fetch_txt('https://877622.xyz/m2t.php?url=https://kakaxi-1.asia/ipv6.m3u')
kkxv4 = fetch_txt('https://raw.githubusercontent.com/kakaxi-1/IPTV/refs/heads/main/ipv4.txt')
rihou = fetch_txt('http://rihou.cc:555/gggg.nzk')
shulao = fetch_txt('https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg1')
bcitv = fetch_txt('https://877622.xyz/m2t.php?url=https://188766.xyz/itv')
aptv = fetch_txt('https://877622.xyz/m2t.php?url=https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u')
cat = fetch_txt('https://877622.xyz/m2t.php?url=https://iptv.catvod.com/tv.m3u')

kx = aptv +kkxv4 + bcitv + rihou + shulao
kx=re.sub(r'&amp;','&',kx)
##kx1 = process_multiline_text(kx, CHANNEL_ALIAS_MAP)

##kx1 = simplify_guangdong(simplify_cctv(kx))
##kxtt = re.findall(r'.*\,.*:\/\/.*',kx1)

all_links=fmm + cat + test
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

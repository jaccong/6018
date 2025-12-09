import eventlet
eventlet.monkey_patch()
import time
import datetime
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import re
from collections import defaultdict
import threading
import os
##===========================================================================================##
taop = ''
newnine = ''
cqyx=''
jsyd=''
from process_channels import process_channel_with_alias
from process_channels import process_multiline_text
from process_channels import CHANNEL_ALIAS_MAP
from channel_sorter import sorter_main
from channel_sorter import custom_order


##===========================================================================================##
##===========================================================================================##
# 核心配置
TIMEOUT = 1.0  # IP扫描超时
CHANNEL_TIMEOUT = 3.0  # 频道检测超时（含分辨率解析，稍长）
MAX_WORKERS = 500
RETRY_TIMES = 1
RETRY_INTERVAL = 0.02
IP_SEGMENT_RANGE = range(1, 256)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Connection": "keep-alive"
}

# 分辨率优先级映射（中文关键词+完整字符串）
RESOLUTION_PRIORITY = {
    '4K': 10, '2160p': 10, '超高清': 10,
    '1080p': 9, 'FHD': 9, '全高清': 9,
    '720p': 8, 'HD': 8, '高清': 8,
    '480p': 7, 'SD': 7, '标清': 7,
    '360p': 6, '流畅': 6,
    '240p': 5,
    '未知': 1
}

# 全局会话
session = requests.Session()
session.headers.update(HEADERS)

# 线程安全计数器
scan_counter = 0
valid_counter = 0
channel_scan_counter = 0
channel_valid_counter = 0
lock = threading.Lock()

def modify_urls(url):
    modified_urls = []
    try:
        if url.startswith('https://'):
            ip_start_index = url.find("https://") + 8
            base_url = "https://"
        else:
            ip_start_index = url.find("//") + 2
            base_url = "http://"
        
        ip_end_index = url.find(":", ip_start_index)
        if ip_end_index == -1:
            return modified_urls
        
        ip_address = url[ip_start_index:ip_end_index]
        port = url[ip_end_index:]
        ip_end = "/iptv/live/1000.json?key=txiptv"
        
        ip_parts = ip_address.split(".")
        if len(ip_parts) != 4:
            return modified_urls
        ip_prefix = ".".join(ip_parts[:3])
        
        for i in IP_SEGMENT_RANGE:
            modified_ip = f"{ip_prefix}.{i}"
            modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
            modified_urls.append(modified_url.strip())
    except Exception as e:
        print(f"【URL扩展失败】基础URL：{url}（错误：{str(e)[:50]}）")
        pass
    return modified_urls

def validate_base_url(url):
    pattern = r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"
    return re.match(pattern, url) is not None

def request_with_retry(url, method="GET", timeout=TIMEOUT, **kwargs):
    kwargs.setdefault("headers", HEADERS)
    kwargs.setdefault("timeout", timeout)
    for _ in range(RETRY_TIMES + 1):
        try:
            response = session.request(method, url, **kwargs)
            if response.status_code in [200, 302]:
                return response
        except requests.exceptions.RequestException:
            time.sleep(RETRY_INTERVAL)
    return None

def is_url_accessible(url):
    global scan_counter, valid_counter
    response = request_with_retry(url)
    with lock:
        scan_counter += 1
        if scan_counter % 5000 == 0:
            print(f"【IP扫描进度】已完成 {scan_counter} 个URL，当前可用 {valid_counter} 个")
        if response:
            valid_counter += 1
            return url
    return None

def parse_resolution(m3u8_content, channel_name):
    """解析M3U8内容获取分辨率，无则从名称推测"""
    # 从M3U8 #EXT-X-STREAM-INF中提取带宽/分辨率
    stream_inf_pattern = r"#EXT-X-STREAM-INF:.*?(BANDWIDTH=(\d+)|RESOLUTION=(\d+x\d+))"
    matches = re.findall(stream_inf_pattern, m3u8_content, re.IGNORECASE)
    resolution = '未知'
    
    # 从分辨率字段提取
    for match in matches:
        if match[2]:  # RESOLUTION=1920x1080
            w, h = match[2].split('x')
            h = int(h)
            if h >= 2160:
                resolution = '2160p'
            elif h >= 1080:
                resolution = '1080p'
            elif h >= 720:
                resolution = '720p'
            elif h >= 480:
                resolution = '480p'
            elif h >= 360:
                resolution = '360p'
            break
    
    # 从带宽推测（备用）
    if resolution == '未知':
        for match in matches:
            if match[1]:  # BANDWIDTH=1000000
                bandwidth = int(match[1])
                if bandwidth >= 20000000:
                    resolution = '4K'
                elif bandwidth >= 5000000:
                    resolution = '1080p'
                elif bandwidth >= 2000000:
                    resolution = '720p'
                elif bandwidth >= 1000000:
                    resolution = '480p'
                break
    
    # 从频道名称推测（最终备用）
    # 中文关键词兜底
    if resolution == '未知':
        name_lower = channel_name.lower()
        if any(kw in name_lower for kw in ['4k', '2160p', '超高清']):
            resolution = '4K'
        elif any(kw in name_lower for kw in ['1080p', 'fhd', '全高清']):
            resolution = '1080p'
        elif any(kw in name_lower for kw in ['720p', 'hd', '高清']):
            resolution = '720p'
        elif any(kw in name_lower for kw in ['480p', 'sd', '标清']):
            resolution = '480p'
        elif any(kw in name_lower for kw in ['360p', '流畅']):
            resolution = '360p'
    
    return resolution

def is_channel_accessible(channel_tuple):
    """检测：可用性+响应速度+分辨率"""
    global channel_scan_counter, channel_valid_counter
    name, url = channel_tuple
    response = None
    response_time = float('inf')
    resolution = '未知'
    
    # 1. 检测可用性+响应速度（HEAD优先）
    start_time = time.time()
    response = request_with_retry(url, method="HEAD", timeout=CHANNEL_TIMEOUT)
    if response:
        response_time = time.time() - start_time
    else:
        # HEAD失败用GET，同时获取M3U8内容用于解析分辨率
        start_time = time.time()
        response = request_with_retry(url, method="GET", timeout=CHANNEL_TIMEOUT, stream=True)
        if response:
            response_time = time.time() - start_time
            # 2. 解析分辨率（仅读取前2048字节，避免下载大文件）
            m3u8_content = response.raw.read(2048).decode('utf-8', errors='ignore')
            resolution = parse_resolution(m3u8_content, name)
    
    with lock:
        channel_scan_counter += 1
        if channel_scan_counter % 200 == 0:
            print(f"【频道检测进度】已完成 {channel_scan_counter} 个，有效 {channel_valid_counter} 个")
        if response:
            channel_valid_counter += 1
            priority = RESOLUTION_PRIORITY[resolution]
            #print(f"【优质频道】{name} | 分辨率：{resolution} | 响应速度：{response_time:.3f}s | {url}")
            return (name, url, priority, response_time)
        else:
            ##print(f"【无效频道】{name} → {url}")
            return None

def extract_urls_from_source(source_content):
    pattern = r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"
    raw_urls = re.findall(pattern, source_content)
    processed_urls = []
    for url in raw_urls:
        if not url.startswith(('http://', 'https://')):
            url = f"http://{url}"
        processed_urls.append(url)
    return processed_urls

def get_source_content(url, selenium_options):
    try:
        print(f"【数据源处理】Selenium 访问：{url}")
        driver = webdriver.Chrome(options=selenium_options)
        driver.get(url)
        time.sleep(6)
        page_content = driver.page_source
        driver.quit()
        print(f"【数据源处理】成功获取：{url}")
        return page_content
    except Exception as e:
        print(f"【数据源处理】失败：{url}（错误：{str(e)[:50]}）")
        return ""

if __name__ == "__main__":
    print("="*50)
    print(f"【程序启动】时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)

    # 读取本地IP列表
    try:
        with open('ip.txt', 'r', encoding='utf-8') as file:
            iplist = file.read().strip()
        print(f"【本地IP读取】成功读取ip.txt（字符长度：{len(iplist)}）")
    except Exception as e:
        iplist = ""
        print(f"【本地IP读取】失败：{str(e)}（忽略，继续执行）")

    # 生成时间戳
    now = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('[ %m/%d %H:%M ]')

    # 数据源URL（仅前2个）
    urls = [
        "https://877622.xyz/ip/ips.txt",
        "https://raw.githubusercontent.com/jaccong/iptv-api/master/output/user_result.txt"
    ]

    # Selenium配置
    selenium_options = Options()
    selenium_options.add_argument('--headless=new')
    selenium_options.add_argument('--no-sandbox')
    selenium_options.add_argument('--disable-dev-shm-usage')
    selenium_options.add_argument(f'--user-agent={HEADERS["User-Agent"]}')
    selenium_options.add_argument('--blink-settings=imagesEnabled=false')

    # 提取待扫描URL
    all_scan_urls = set()
    total_raw_ip = 0
    invalid_base_url_count = 0
    print("\n【待扫描URL生成】开始处理数据源...")
    for idx, source_url in enumerate(urls, 1):
        if source_url == "fromiptxt":
            source_content = iplist
            print(f"【数据源{idx}/{len(urls)}】处理本地ip.txt...")
        else:
            source_content = get_source_content(source_url, selenium_options)
        
        raw_urls = extract_urls_from_source(source_content)
        total_raw_ip += len(raw_urls)
        print(f"【数据源{idx}/{len(urls)}】提取IP数：{len(raw_urls)}（累计：{total_raw_ip}）")

        for raw_url in raw_urls:
            try:
                if not validate_base_url(raw_url):
                    invalid_base_url_count += 1
                    continue
                
                if raw_url.startswith('https://'):
                    ip_start_index = raw_url.find("https://") + 8
                    base_proto = "https://"
                else:
                    ip_start_index = raw_url.find("//") + 2
                    base_proto = "http://"
                
                ip_end_index = raw_url.find(":", ip_start_index)
                if ip_end_index == -1:
                    invalid_base_url_count += 1
                    continue
                
                ip_full = raw_url[ip_start_index:ip_end_index]
                port = raw_url[ip_end_index:]
                ip_parts = ip_full.split(".")
                if len(ip_parts) != 4:
                    invalid_base_url_count += 1
                    continue
                
                offset = 0
                third_part = int(ip_parts[2]) + offset
                if 0 <= third_part <= 255:
                    extended_ip_prefix = f"{'.'.join(ip_parts[:2])}.{third_part}"
                    extended_url = f"{base_proto}{extended_ip_prefix}.1{port}"
                    if validate_base_url(extended_url):
                        all_scan_urls.add(extended_url.strip())
                    else:
                        invalid_base_url_count += 1
            except Exception:
                invalid_base_url_count += 1
                continue
    
    # 计算扫描任务数
    total_scan_tasks = 0
    valid_base_url_count = len(all_scan_urls)
    for idx, url in enumerate(all_scan_urls):
        extended_urls = modify_urls(url)
        total_scan_tasks += len(extended_urls)
        if (idx + 1) % 100 == 0:
            print(f"【扩展统计】已处理 {idx + 1}/{valid_base_url_count} 个URL，累计任务：{total_scan_tasks}")
    
    print(f"\n【待扫描URL生成】完成！")
    print(f"- 原始IP数：{total_raw_ip} | 无效URL数：{invalid_base_url_count} | 有效基础URL数：{valid_base_url_count}")
    print(f"- 总扫描任务数：{total_scan_tasks}")

    # IP扫描
    valid_urls = []
    print("\n" + "="*50)
    print(f"【IP扫描】启动（线程：{MAX_WORKERS}，超时：{TIMEOUT}s）")
    print("="*50)
    start_scan_time = time.time()

    if total_scan_tasks > 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_url = {}
            for url in all_scan_urls:
                for modified_url in modify_urls(url):
                    future = executor.submit(is_url_accessible, modified_url)
                    future_to_url[future] = modified_url
            
            for future in concurrent.futures.as_completed(future_to_url):
                result = future.result()
                if result:
                    valid_urls.append(result)
    else:
        print("【IP扫描】无任务，跳过")

    # IP扫描统计
    scan_time = round(time.time() - start_scan_time, 2)
    scan_speed = scan_counter / scan_time if scan_time > 0 else 0
    print(f"\n【IP扫描完成】耗时：{scan_time}s | 速度：{scan_speed:.0f}个/秒 | 可用IP：{len(valid_urls)}（命中率：{len(valid_urls)/scan_counter*100:.2f}%）")

    # 提取频道
    channel_data = []
    print("\n" + "="*50)
    if len(valid_urls) == 0:
        print(f"【频道提取】无可用IP，跳过")
    else:
        print(f"【频道提取】处理 {len(valid_urls)} 个IP...")
        print("="*50)
        for idx, url in enumerate(valid_urls, 1):
            if idx % 10 == 0:
                print(f"【提取进度】{idx}/{len(valid_urls)} 个IP，已提取频道：{len(channel_data)}")
            response = request_with_retry(url)
            if not response:
                continue
            try:
                json_data = response.json()
                if json_data.get('count', 0) == 0:
                    continue
                for item in json_data.get('data', []):
                    if not isinstance(item, dict):
                        continue
                    name = item.get('name', '')
                    urlx = item.get('url', '')
                    num = item.get('chid', '')
                    srcid = item.get('srcid', '')
                    if not (name and urlx):
                        continue
                    try:
                        if url.startswith('https://'):
                            ip_start_index = url.find("https://") + 8
                        else:
                            ip_start_index = url.find("//") + 2
                        ip_index_second = url.find("/", ip_start_index + 1)
                        base_ip = url[ip_start_index:ip_index_second]
                        base_url = f"{url[:ip_start_index]}{base_ip}"
                        
                        if 'http' in urlx:
                            final_url = urlx.strip()
                        elif 'udp' in urlx:
                            final_url = f"{base_url}/tsfile/live/{num}_{srcid}.m3u8?key=txiptv&playlive=1&down=1"
                        else:
                            final_url = f"{base_url}{urlx}".strip()
                        channel_data.append((name, final_url))
                    except Exception:
                        continue
            except Exception:
                continue
    
    print(f"【频道提取完成】共提取：{len(channel_data)} 个频道（含重复）")

    #初步筛选频道
    #chubu_keywords = ['广东', '翡翠', '无线', '卫视']
    #channel_data = [item for item in channel_data if any(kw in item[0] for kw in chubu_keywords)]
    
    # 频道检测（可用性+分辨率+响应速度）
    valid_channel_data = []
    print("\n" + "="*50)
    if len(channel_data) == 0:
        print(f"【频道检测】无频道，跳过")
    else:
        print(f"【频道检测】启动（线程：{MAX_WORKERS}，超时：{CHANNEL_TIMEOUT}s）")
        print("="*50)
        start_channel_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(is_channel_accessible, chan) for chan in channel_data]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    valid_channel_data.append(result)
        
        # 排序：分辨率优先级降序 → 响应速度升序（优质频道前置）
        valid_channel_data.sort(key=lambda x: (-x[2], x[3]))
        
        # 检测统计
        channel_time = round(time.time() - start_channel_time, 2)
        channel_speed = channel_scan_counter / channel_time if channel_time > 0 else 0
        print(f"\n【频道检测完成】耗时：{channel_time}s | 速度：{channel_speed:.0f}个/秒 | 有效频道：{len(valid_channel_data)}（有效率：{len(valid_channel_data)/channel_scan_counter*100:.2f}%）")

    
    print("\n" + "="*50)
    print(f"【程序结束】时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
##==================================================================================================================================================##
##==================================================================================================================================================##
##==================================================================================================================================================##

test = '\n'.join(f"{item[0]},{item[1]}" for item in valid_channel_data)
test = re.sub('parse=1|player=2|ua=.*','',test)             #关键文本在这里！！！！！！！！！！！！！！

print("\n" + "="*50)
print('【test文本整理完毕，准备再合并分类处理】')
print("="*50)

fmm = get_source_content('https://fanmingming.com/txt?url=https://kakaxi-1.asia/ipv6.m3u', selenium_options)
rihou = get_source_content('http://rihou.cc:555/gggg.nzk', selenium_options)
shulao = get_source_content('https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg1', selenium_options)
bcitv = get_source_content('https://877622.xyz/m2t.php?url=https://188766.xyz/itv', selenium_options)
aptv = get_source_content('https://fanmingming.com/txt?url=https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u', selenium_options)
kx =aptv+ bcitv + rihou + shulao

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
all_links=re.sub(r'\S*翡翠\S*\,','翡翠台,',all_links)
all_links=re.sub(r'\S*无线新闻\S*\,','无线新闻台,',all_links)
all_links=re.sub(r'\S*千禧经典\S*\,','千禧经典台,',all_links)
all_links=re.sub(r'\S*美亚电影\S*\,','美亚电影台,',all_links)
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

with open("520.txt", 'w', encoding='utf-8') as file:
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

  file.write('自动更新,#genre#\n')
  file.write(f'{now},https://jaccong0520.serv00.net/da.mp4')


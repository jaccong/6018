import requests
import re

# ==================== 重要参数前置（所有配置集中管理）====================
# 1. 输入输出配置
INPUT_LOCAL_FILE = 'test.txt'  # 本地输入文件
OUTPUT_FILE = '108.txt'        # 最终输出文件
TIMEOUT = 10                   # 网络请求超时时间

# 2. 资源合并配置（参数区合并：资源信息+合并顺序绑定）
# 格式：[(资源标识, URL/None), ...] | URL=None→本地文件，列表顺序=合并顺序
RESOURCE_MERGE_CONFIG = [
    ('GDTY', 'https://877622.xyz/gdty.txt'),  # 0. GDTY GDTY
    ('ipv6_m3u', 'https://877622.xyz/m2t.php?url=https://kakaxi-1.asia/ipv6.m3u'),  # 1. IPv6 M3U
    ('cat_tv', 'https://877622.xyz/m2t.php?url=https://iptv.catvod.com/tv.m3u'),  # 2. TV.M3U
    ('local_file', None),  # 3. 本地文件
    ('aptv_m3u', 'https://877622.xyz/m2t.php?url=https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u'), # 8. APTV M3U
    ('bcitv_itv', 'https://877622.xyz/m2t.php?url=https://188766.xyz/itv'),  # 7. BCITV
    ('ipv4_txt', 'https://raw.githubusercontent.com/kakaxi-1/IPTV/refs/heads/main/ipv4.txt'),  # 4. IPv4 TXT
    ('rihou_nzk', 'http://rihou.cc:555/gggg.nzk'),  # 5. 日候 NZK
    ('shulao_txt', 'https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg1')  # 6. 树老 TXT
]

# 3. 频道分类配置
CATEGORY_CONFIG = [
    ('广东频道', ['广东卫视', '广东体育', '广东珠江', '广东新闻', '广东影视', '广东民生', '广东少儿', '嘉佳卡通', '大湾区卫视']),
    ('港澳频道', ['翡翠台', '无线新闻台', 'NOW新闻台', '中天新闻台', '千禧经典台', '美亚电影台']),
    ('央视频道', ['CCTV1', 'CCTV2', 'CCTV3', 'CCTV4', 'CCTV5', 'CCTV6', 'CCTV7', 'CCTV8', 'CCTV9', 'CCTV10', 'CCTV11', 'CCTV12', 'CCTV13', 'CCTV14', 'CCTV15', 'CCTV16', 'CCTV17', 'CHC家庭影院', 'CHC动作电影', 'CHC影迷电影']),
    ('卫视频道', ['卫视'])
]

# 4. 过滤关键词
REMOVE_KEYWORDS = ['smt', 'smart', 'Smart', 'cmvideo', 'mobile', '/rtp/', '/udp/', '台庆']
WS_REMOVE_KEYWORDS = REMOVE_KEYWORDS + ['大湾区卫视', '广东卫视']

# 5. 网络请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/16.1 Safari/604.1",
    "Accept": "text/plain,*/*",
    "Connection": "keep-alive"
}

# ==================== 必要工具函数 ====================
def fetch_txt(url, resource_name):
    """远程拉取TXT内容"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.encoding = "utf-8"
        line_count = len(response.text.splitlines())
        print(f"   ✅ {resource_name} | 行数: {line_count}")
        return response.text + '\n'
    except requests.exceptions.Timeout:
        print(f"   ❌ {resource_name} | 拉取超时")
        return ''
    except requests.exceptions.ConnectionError:
        print(f"   ❌ {resource_name} | 连接失败")
        return ''
    except Exception as e:
        print(f"   ❌ {resource_name} | 错误：{str(e)}")
        return ''

def read_local_file(filename):
    """纯读取本地文件，无任何预处理"""
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

# ==================== 外部模块导入 ====================
from process_channels import process_multiline_text, CHANNEL_ALIAS_MAP
from channel_sorter import sorter_main, custom_order

# ==================== 核心执行流程 ====================
def main():
    print("🚀 开始执行频道处理流程...")
    
    # 1. 纯读取本地文件（无任何预处理）
    print("📁 读取本地文件...")
    local_text = read_local_file(INPUT_LOCAL_FILE)
    print(f"✅ 本地文件读取成功：{INPUT_LOCAL_FILE}")
    
    # 2. 拉取所有远程资源（独立步骤）
    print("\n🌐 拉取所有远程资源...")
    fetched_resources = {}
    remote_resources = [(name, url) for name, url in RESOURCE_MERGE_CONFIG if url is not None]
    
    for resource_name, url in remote_resources:
        print(f"   🔄 拉取：{resource_name}")
        fetched_resources[resource_name] = fetch_txt(url, resource_name)
    print("✅ 所有远程资源拉取完成")
    
    # 3. 按配置顺序合并数据（独立步骤）
    print("\n🧩 按配置顺序合并数据...")
    raw_data = ''
    merge_order_log = []
    
    for resource_name, url in RESOURCE_MERGE_CONFIG:
        merge_order_log.append(resource_name)
        if resource_name == 'local_file' and url is None:
            raw_data += local_text
            print(f"   🔹 已合并：{resource_name}")
        elif resource_name in fetched_resources:
            raw_data += fetched_resources[resource_name]
            print(f"   🔹 已合并：{resource_name}")
        else:
            print(f"   ⚠️  跳过无效配置：{resource_name}")
    
    print("✅ 数据合并完成")
    
    # 4. 频道别名处理
    print("\n🔗 处理频道别名...")
    processed_data = process_multiline_text(raw_data, CHANNEL_ALIAS_MAP)
    print("✅ 频道别名处理完成")
    
    # 5. 筛选有效链接并排序
    print("\n📊 筛选有效链接并排序...")
    valid_links = re.findall(r'.*\,.*:\/\/.*', processed_data)
    sorted_links = sorter_main(valid_links, custom_order)
    print(f"✅ 筛选完成 | 有效链接总数: {len(sorted_links)}")
    
    # 6. 分类写入文件
    print("\n📝 开始写入分类频道...")
    total_written = 0
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as file:
        for cate_name, keywords in CATEGORY_CONFIG:
            file.write(f'{cate_name},#genre#\nplayer=2\n')
            filter_keys = WS_REMOVE_KEYWORDS if cate_name == '卫视频道' else REMOVE_KEYWORDS
            for line in sorted_links:
                if any(kw in line for kw in keywords) and all(k not in line for k in filter_keys):
                    file.write(f'{line}\n')
                    total_written += 1
        
        # 写入自动更新信息（从原始本地文件中提取）
        auto_update_info = re.findall(r'\自动更新\,\#genre\#.*', local_text, flags=re.DOTALL)
        if auto_update_info:
            file.write(f'{auto_update_info[0]}\n')
    
    # 7. 最终报告
    print(f"\n🎉 执行完成！")
    print(f"📊 统计：共写入 {total_written} 个频道")
    print(f"📁 输出文件：{OUTPUT_FILE}")
    print(f"🔍 合并顺序：{' → '.join(merge_order_log)}")

if __name__ == "__main__":
    main()

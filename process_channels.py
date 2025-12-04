def process_channel_with_alias(text, channel_alias_map):
    """单行处理：支持别名匹配+标准名统一"""
    parts = text.strip().split(',')
    if len(parts) != 2:
        return text
    input_name, url = parts[0], parts[1]
    
    input_name_clean = input_name.lower().replace(' ', '')  # 预处理：忽略大小写和空格
    matched_standard = None
    max_match_len = 0  # 最长匹配优先级：避免短别名误匹配（如“翡翠”不匹配“翡翠台”）
    
    # 遍历所有标准频道及其别名，找最长匹配
    for standard_name, aliases in channel_alias_map.items():
        # 合并标准名和别名，统一匹配（既支持标准名输入，也支持别名输入）
        all_match_strings = [standard_name] + aliases
        for match_str in all_match_strings:
            match_str_clean = match_str.lower().replace(' ', '')
            if match_str_clean in input_name_clean:
                # 优先选择匹配长度最长的（确保精准）
                if len(match_str_clean) > max_match_len:
                    max_match_len = len(match_str_clean)
                    matched_standard = standard_name
    
    # 匹配成功则返回标准名，失败则返回原名称
    final_name = matched_standard if matched_standard else input_name
    return f"{final_name},{url}"

# -------------------------- 新增：大段文本处理（不变） --------------------------
def process_multiline_text(multiline_text, channel_alias_map):
    lines = multiline_text.splitlines()
    processed_lines = []
    for line in lines:
        line = line.strip()
        processed_lines.append(process_channel_with_alias(line, channel_alias_map) if line else '')
    return '\n'.join(processed_lines)

# -------------------------- 核心配置：标准名+别名映射字典（分类整理） --------------------------
CHANNEL_ALIAS_MAP = {
    # 一、广东二字开头核心频道（仅保留“广东”前缀，别名覆盖简称、英文、常见叫法）
    "广东卫视": ["广卫", "GDTV", "广东卫视频道", "广东卫视台", "GD Satellite TV", "广东综合卫视"],
    "广东体育": ["广体", "GD Sports", "广东体育频道", "广东体育台", "GD Sports Channel", "广体频道"],
    "广东新闻": ["广新", "GD News", "广东新闻频道", "广东新闻台", "GD News Channel", "广东新闻综合"],
    "广东珠江": ["珠江台", "GD Zhujiang", "广东珠江频道", "珠江卫视频道", "GD Pearl River Channel"],
    "广东民生": ["广民", "GD Minsheng", "广东民生频道", "广东公共民生频道", "GD Minsheng Channel"],  # 修正：广东公共→广东民生
    "广东影视": ["广影", "GD Film", "广东影视频道", "广东电影频道", "GD Movie Channel", "广影视"],
    "广东综艺": ["广综", "GD Variety", "广东综艺频道", "广东综艺娱乐频道", "GD Variety Show Channel"],
    "广东少儿": ["广少", "GD Kids", "广东少儿频道", "广东儿童频道", "GD Children's Channel", "广东少儿台"],
    "嘉佳卡通": ["嘉佳卫视", "GD Jiajia", "嘉佳卡通频道", "广东嘉佳卡通", "Jiajia Cartoon Channel", "嘉佳台"],
    # 新增：大湾区卫视
    "大湾区卫视": ["广东湾区", "GBA TV", "大湾区卫视频道", "Guangdong Greater Bay Area TV", "GBA Satellite TV"],
    # 二、央视含数字主要频道（仅核心数字频道，别名覆盖“央视X套”“XX频道”“英文缩写”）
    "CCTV1": ["央视一套", "综合频道", "CCTV-1", "CCTV One", "央视综合", "一套"],
    "CCTV2": ["央视二套", "财经频道", "CCTV-2", "CCTV Finance", "央视财经", "二套"],
    "CCTV3": ["央视三套", "综艺频道", "CCTV-3", "CCTV Variety", "央视综艺", "三套"],
    "CCTV4": ["央视四套", "中文国际频道", "CCTV-4", "CCTV International", "央视中文国际", "四套"],
    "CCTV5+": ["央视五套+", "体育赛事频道", "CCTV-5+", "CCTV Sports Plus", "央视体育+", "体育赛事台"],
    "CCTV5": ["央视五套", "体育频道", "CCTV-5", "CCTV Sports", "央视体育", "五套", "体育台"],
    "CCTV6": ["央视六套", "电影频道", "CCTV-6", "CCTV Movie", "央视电影", "六套", "电影台"],
    "CCTV7": ["央视七套", "国防军事频道", "CCTV-7", "CCTV National Defense", "央视国防军事", "七套"],
    "CCTV8": ["央视八套", "电视剧频道", "CCTV-8", "CCTV Drama", "央视电视剧", "八套", "电视剧台"],
    "CCTV9": ["央视九套", "纪录频道", "CCTV-9", "CCTV Documentary", "央视纪录", "九套", "纪录台"],
    "CCTV10": ["央视十套", "科教频道", "CCTV-10", "CCTV Science", "央视科教", "十套", "科教台"],
    "CCTV11": ["央视十一套", "戏曲频道", "CCTV-11", "CCTV Opera", "央视戏曲", "十一套", "戏曲台"],
    "CCTV12": ["央视十二套", "社会与法频道", "CCTV-12", "CCTV Society & Law", "央视社会与法", "十二套"],
    "CCTV13": ["央视十三套", "新闻频道", "CCTV-13", "CCTV News", "央视新闻", "十三套", "新闻台"],
    "CCTV14": ["央视十四套", "少儿频道", "CCTV-14", "CCTV Kids", "央视少儿", "十四套", "少儿台"],
    "CCTV15": ["央视十五套", "音乐频道", "CCTV-15", "CCTV Music", "央视音乐", "十五套", "音乐台"],
    "CCTV16": ["央视十六套", "奥林匹克频道", "CCTV-16", "CCTV Olympic", "央视奥运频道", "十六套"],
    "CCTV17": ["央视十七套", "农业农村频道", "CCTV-17", "CCTV Agriculture", "央视农业农村", "十七套"],
    # 三、常见主要卫视频道（仅核心主流卫视，别名覆盖简称、昵称、英文、缩写）
    "湖南卫视": ["芒果台", "HNTV", "湖南卫视频道", "湘卫", "Hunan TV", "芒果卫视", "湖南台"],
    "浙江卫视": ["浙卫", "ZJTV", "浙江卫视频道", "蓝莓台", "Zhejiang TV", "浙台", "浙江台"],
    "东方卫视": ["番茄台", "Dragon TV", "东方卫视频道", "沪卫", "Shanghai TV", "东卫", "上海东方台"],
    "江苏卫视": ["荔枝台", "JSBC", "江苏卫视频道", "苏卫", "Jiangsu TV", "江苏台", "苏视"],
    "北京卫视": ["京卫", "BTV", "北京卫视频道", "北汽卫视", "Beijing TV", "京台", "北京台"],
    "安徽卫视": ["皖卫", "AHTV", "安徽卫视频道", "海豚台", "Anhui TV", "徽卫", "安徽台"],
    "山东卫视": ["鲁卫", "SDTV", "山东卫视频道", "天秤台", "Shandong TV", "鲁台", "山东台"],
    "四川卫视": ["川卫", "SCTV", "四川卫视频道", "熊猫台", "Sichuan TV", "川台", "四川台"],
    "湖北卫视": ["鄂卫", "HBTV", "湖北卫视频道", "长江台", "Hubei TV", "鄂台", "湖北台"],
    "河南卫视": ["豫卫", "HNTV-1", "河南卫视频道", "梨园春台", "Henan TV", "豫台", "河南台"],
    "河北卫视": ["冀卫", "HEBTV", "河北卫视频道", "长城台", "Hebei TV", "冀台", "河北台"],
    "黑龙江卫视": ["黑卫", "HLJTV", "黑龙江卫视频道", "龙视", "Heilongjiang TV", "黑台"],
    "吉林卫视": ["吉卫", "JLTV", "吉林卫视频道", "雾凇台", "Jilin TV", "吉台", "吉林台"],
    "辽宁卫视": ["辽卫", "LNTV", "辽宁卫视频道", "七星台", "Liaoning TV", "辽台", "辽宁台"],
    "天津卫视": ["津卫", "TJTW", "天津卫视频道", "天视", "Tianjin TV", "津台", "天津台"],
    "重庆卫视": ["渝卫", "CQTV", "重庆卫视频道", "麻辣台", "Chongqing TV", "渝台", "重庆台"],
    "贵州卫视": ["黔卫", "GZTV", "贵州卫视频道", "多彩贵州台", "Guizhou TV", "黔台"],
    "云南卫视": ["滇卫", "YNTV", "云南卫视频道", "孔雀台", "Yunnan TV", "滇台", "云南台"],
    "广西卫视": ["桂卫", "GXTV", "广西卫视频道", "桂花台", "Guangxi TV", "桂台", "广西台"],
    "江西卫视": ["赣卫", "JXTV", "江西卫视频道", "红色台", "Jiangxi TV", "赣台", "江西台"],
    "福建东南卫视": ["东南卫视", "SETV", "福建卫视", "海鸥台", "Southeast TV", "闽卫", "东南台"],
    "海南卫视": ["琼卫", "Hainan TV", "海南卫视频道", "旅游卫视", "Hainan Tourism TV", "琼台"],
    "山西卫视": ["晋卫", "SXTV", "山西卫视频道", "黄河台", "Shanxi TV", "晋台", "山西台"],
    "陕西卫视": ["陕卫", "SXTVS", "陕西卫视频道", "华夏台", "Shaanxi TV", "陕台", "陕西台"],
    # 四、港澳台常见主要频道（仅核心主流频道，别名覆盖简称、英文、当地叫法）
    "TVB翡翠台": ["翡翠台", "无线翡翠台", "无线翡翠", "Jade TV", "TVB Jade", "翡翠卫视", "无线台"],
    "TVB明珠台": ["明珠台", "Pearl TV", "TVB Pearl", "无线明珠台", "明珠卫视", "英文台"],
    "TVB星河台": ["星河台", "TVB Star River", "无线星河台", "星河卫视", "Star River Channel"],
    "TVB财经台": ["财经台", "TVB Finance", "无线财经台", "财经资讯台", "TVB Finance Channel"],
    "亚视本港台": ["本港台", "ATV Home", "亚洲本港台", "亚视Home台", "ATV 本港台"],
    "亚视国际台": ["国际台", "ATV World", "亚洲国际台", "亚视World台", "英文国际台"],
    "香港凤凰卫视中文台": ["凤凰中文台", "Phoenix Chinese Channel", "凤凰卫视", "Phoenix TV", "凤凰中文"],
    "香港凤凰卫视资讯台": ["凤凰资讯台", "Phoenix Info News", "凤凰新闻台", "Phoenix Info Channel"],
    "香港凤凰卫视电影台": ["凤凰电影台", "Phoenix Movies", "凤凰影视频道", "Phoenix Movie Channel"],
    "澳门澳广视中文台": ["澳广视中文台", "TDM Chinese", "澳门中文台", "澳视中文", "TDM Canal Chines"],
    "台湾台视": ["台视", "TTV", "台湾电视公司", "台视主频", "Taiwan Television", "TTV Main"],
    "台湾中视": ["中视", "CTV", "中国电视公司", "中视主频", "China Television", "CTV Main"],
    "台湾华视": ["华视", "CTS", "中华电视公司", "华视主频", "China Television Service", "CTS Main"],
    "台湾民视": ["民视", "FTV", "民间全民电视公司", "民视主频", "Formosa TV", "FTV Main"],
    "台湾中天新闻台": ["中天新闻", "CTi News", "中天台", "CTi News Channel", "中天新闻频道"],
    "台湾TVBS": ["TVBS", "TVBS主频", "TVBS综合台", "TVBS Main Channel", "联意电视"],
    "台湾八大综合台": ["八大综合", "GTV Variety", "八大台", "GTV综合台", "GTV Variety Channel"],
    "台湾三立新闻台": ["三立新闻", "SET News", "三立台", "SET News Channel", "三立新闻频道"],
    "台湾东森新闻台": ["东森新闻", "ETtoday News", "东森台", "ET News Channel", "东森新闻频道"],
    # 新增：港澳台指定频道
    "无线新闻台": ["TVB News", "无线新闻频道", "TVB新闻台", "香港无线新闻", "News Channel","无线新闻"],
    "千禧经典台": ["千禧台", "Millennium Classic", "经典台", "千禧经典频道", "Millennium Channel"],
    "美亚电影台": ["美亚影台", "Meiya Movies", "美亚电影频道", "Meiya Film Channel", "MA Movies"]
}
# -------------------------- 测试：别名场景处理效果 --------------------------
input_multiline_text = """
无线翡翠台-高清,http://111.111
翡翠台hd,http://222.222
无线翡翠_FYTV,http://333.333
TVB翡翠台直播,http://444.444
芒果台(超清),http://555.555
央视体育+,http://666.666
珠江频道4K,http://777.777
番茄台Pro,http://888.888
"""

# 执行处理
processed_text = process_multiline_text(input_multiline_text, CHANNEL_ALIAS_MAP)

# 输出结果
print("处理前（含别名）：")
print(input_multiline_text)
print("="*50)
print("处理后（统一标准名）：")
print(processed_text)

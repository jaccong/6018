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
    # 一、广东地方频道（标准名：[别名列表]）
    "广东卫视": ["广东卫视频道", "GDTV"],
    "广东体育": ["广东体育频道", "GD Sports", "广体"],
    "广东新闻": ["广东新闻频道", "GD News"],
    "广东珠江": ["珠江频道", "GD Zhujiang"],
    "广东公共": ["公共频道", "GD Public"],
    "广州新闻": ["广州新闻频道", "GZ News"],
    "深圳卫视": ["深圳卫视频道", "SZTV"],
    
    # 二、卫视频道
    "湖南卫视": ["芒果台", "HNTV", "湖南卫视频道"],
    "浙江卫视": ["浙卫", "ZJTV"],
    "东方卫视": ["番茄台", "Dragon TV", "DFWS"],
    "北京卫视": ["京卫", "BTV"],
    
    # 三、央视频道
    "CCTV5": ["央视体育", "体育频道", "CCTV Sports"],
    "CCTV5+": ["央视体育+", "体育赛事频道", "CCTV5 Plus"],
    "CCTV1": ["央视一套", "综合频道"],
    "央视新闻": ["CCTV新闻", "新闻频道"],
    
    # 四、港澳台频道（重点处理别名）
    "TVB翡翠台": ["无线翡翠台", "翡翠台", "无线翡翠", "Jade TV", "TVB Jade"],
    "TVB明珠台": ["明珠台", "Pearl TV", "TVB Pearl"],
    "香港凤凰卫视中文台": ["凤凰中文台", "Phoenix Chinese Channel"],
    "台湾台视": ["台视", "TTV"],
    "台湾TVBS": ["TVBS频道", "TVBS News"]
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

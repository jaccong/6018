from zhconv import convert  # 需安装：pip install zhconv（繁简转换依赖）

def process_channel_with_alias(text, channel_alias_map, similarity_threshold=0.6):
    """单行处理：支持别名匹配+标准名统一+模糊匹配+繁简转换"""
    parts = text.strip().split(',')
    if len(parts) != 2:
        return text
    input_name, url = parts[0], parts[1]
    
    # 预处理：繁转简+小写+去空格+去特殊字符（保留中文、字母、数字）
    def preprocess(s):
        s = convert(s, 'zh-cn')  # 繁体转简体（如"美亞電影"→"美亚电影"）
        s = s.lower().replace(' ', '')
        return ''.join([c for c in s if c.isalnum() or c in '+-'])  # 保留核心字符
    input_name_clean = preprocess(input_name)
    
    matched_standard = None
    max_match_score = 0  # 匹配得分（相似度+长度权重）
    
    # 遍历所有标准频道及其别名，计算模糊匹配得分
    for standard_name, aliases in channel_alias_map.items():
        all_match_strings = [standard_name] + aliases
        for match_str in all_match_strings:
            match_str_clean = preprocess(match_str)
            if not match_str_clean:
                continue
            
            # 模糊匹配核心逻辑：计算交集字符长度/较短字符串长度（相似度）
            intersection = len(set(input_name_clean) & set(match_str_clean))
            min_len = min(len(input_name_clean), len(match_str_clean))
            similarity = intersection / min_len if min_len > 0 else 0
            
            # 得分加权：相似度×0.7 + 匹配字符串长度占比×0.3（兼顾相似度和完整性）
            len_ratio = len(match_str_clean) / len(input_name_clean) if len(input_name_clean) > 0 else 0
            match_score = (similarity * 0.7) + (len_ratio * 0.3)
            
            # 筛选：得分超过阈值，且取最高得分的匹配结果
            if match_score >= similarity_threshold and match_score > max_match_score:
                max_match_score = match_score
                matched_standard = standard_name
    
    # 匹配成功则返回标准名，失败则返回原名称
    final_name = matched_standard if matched_standard else input_name
    return f"{final_name},{url}"

# -------------------------- 大段文本处理（不变） --------------------------
def process_multiline_text(multiline_text, channel_alias_map):
    lines = multiline_text.splitlines()
    processed_lines = []
    for line in lines:
        line = line.strip()
        processed_lines.append(process_channel_with_alias(line, channel_alias_map) if line else '')
    return '\n'.join(processed_lines)

# -------------------------- 核心配置：标准名+别名映射字典（保持不变） --------------------------
CHANNEL_ALIAS_MAP = {
    # （此处省略原有映射，保持和原代码一致）
    "广东卫视": ["广卫", "GDTV", "广东卫视频道", "广东卫视台", "GD Satellite TV", "广东综合卫视"],
    "美亚电影台": ["美亚影台", "Meiya Movies", "美亚电影频道", "Meiya Film Channel", "MA Movies"],
    "无线新闻台": ["TVB News", "无线新闻频道", "TVB新闻台", "香港无线新闻", "News Channel","无线新闻"],
    # （其他频道映射不变）
}

# -------------------------- 测试：模糊匹配+繁简转换场景 --------------------------
input_multiline_text = """
无线翡翠台-高清,http://111.111
美亚电影欣赏,http://222.222
无线新闻欣赏,http://333.333
美亞電影,http://444.444
無線新聞台,http://555.555
"""

# 执行处理
processed_text = process_multiline_text(input_multiline_text, CHANNEL_ALIAS_MAP)

# 输出结果
print("处理前（含模糊/繁体场景）：")
print(input_multiline_text)
print("="*50)
print("处理后（统一标准名）：")
print(processed_text)

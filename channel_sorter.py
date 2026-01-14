def extract_channel_name(channel_str: str) -> str:
    """从"频道名,URL"格式的字符串中提取频道名"""
    if not isinstance(channel_str, str) or len(channel_str.strip()) == 0:
        return ""
    parts = channel_str.strip().split(',', 1)
    return parts[0].strip() if parts else ""


def extract_channel_url(channel_str: str) -> str:
    """从"频道名,URL"格式的字符串中提取URL"""
    if not isinstance(channel_str, str) or len(channel_str.strip()) == 0:
        return ""
    parts = channel_str.strip().split(',', 1)
    return parts[1].strip() if len(parts) >= 2 else ""


def sort_channels_by_custom_order(original_channels: list, custom_name_order: list, custom_link_order: list) -> list:
    """按【自定义URL关键字顺序(高优先级)】+【自定义频道名顺序】对频道列表排序"""
    if not isinstance(original_channels, list) or len(original_channels) == 0:
        return []
    
    # 构建URL关键字-优先级映射
    link_order_map = {keyword: idx for idx, keyword in enumerate(custom_link_order)}
    max_link_idx = len(custom_link_order)
    
    # 构建频道名-优先级映射
    name_order_map = {name: idx for idx, name in enumerate(custom_name_order)}
    max_name_idx = len(custom_name_order)

    def get_sort_key(channel_str: str) -> tuple:
        channel_url = extract_channel_url(channel_str)
        channel_name = extract_channel_name(channel_str)
        
        # 优先级1: URL关键字匹配度（更高优先级）
        link_weight = max_link_idx
        for keyword, idx in link_order_map.items():
            if keyword in channel_url:
                link_weight = idx
                break
        
        # 优先级2: 频道名匹配度
        name_weight = name_order_map.get(channel_name, max_name_idx)
        
        # 优先级3: 原列表索引（保证排序稳定性）
        original_idx = original_channels.index(channel_str)
        
        return (name_weight, link_weight, original_idx)
    
    sorted_channels = sorted(original_channels, key=get_sort_key)
    return sorted_channels


def print_channel_list(list_name: str, channel_list: list) -> None:
    """格式化打印频道列表"""
    print(f"\n{list_name}：")
    if not channel_list:
        print("  (空列表)")
        return
    for idx, channel in enumerate(channel_list, 1):
        print(f"  {idx}. {channel}")


def sorter_main(original_channels: list, custom_name_order: list, custom_link_order: list) -> list:
    """主函数：执行排序并返回结果"""
    sorted_channels = sort_channels_by_custom_order(original_channels, custom_name_order, custom_link_order)
    return sorted_channels


# 自定义排序规则
custom_link_order = [
    "catvod",
    "rihou",
    "4666888",
    "188766",
    "tvtj",
    "061899",
    "bkpcp",
    "115.190.105",
    "mgtv",
    "migu",
    "/mg/",
    "163189",
    "116.77.33",
    "74.91.26",
]

custom_name_order = [
    "广东卫视",
    "广东珠江",
    "广东体育",
    "广东影视",
    "广东新闻",
    "广东民生",
    "大湾区卫视",
    "广东少儿",
    "嘉佳卡通",
    "翡翠台",
    "无线新闻台",
    "NOW新闻台",
    "中天新闻台",
    "CCTV1",
    "CCTV2",
    "CCTV3",
    "CCTV4",
    "CCTV5",
    "CCTV5+",
    "CCTV6",
    "CCTV7",
    "CCTV8",
    "CCTV9",
    "CCTV10",
    "CCTV11",
    "CCTV12",
    "CCTV13",
    "CCTV14",
    "CCTV15",
    "CCTV16",
    "CCTV17",
    "湖南卫视",
    "浙江卫视",
    "江苏卫视",
    "东方卫视",
    "深圳卫视",
    "北京卫视",
    "安徽卫视",
    "山东卫视",
    "四川卫视",
    "河南卫视",
    "湖北卫视"
]

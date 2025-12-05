
def extract_channel_name(channel_str: str) -> str:
    """从"频道名,URL"格式的字符串中提取频道名"""
    if not isinstance(channel_str, str) or len(channel_str.strip()) == 0:
        return ""
    parts = channel_str.strip().split(',', 1)
    return parts[0].strip() if parts else ""


def sort_channels_by_custom_order(original_channels: list, custom_order: list) -> list:
    """按自定义顺序对频道列表排序"""
    if not isinstance(original_channels, list) or len(original_channels) == 0:
        return []
    
    order_map = {name: idx for idx, name in enumerate(custom_order)}
    max_defined_idx = len(custom_order)
    
    def get_sort_key(channel_str: str) -> tuple:
        channel_name = extract_channel_name(channel_str)
        weight = order_map.get(channel_name, max_defined_idx + original_channels.index(channel_str))
        return (weight, original_channels.index(channel_str))
    
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


def main(original_channels: list, custom_order: list) -> list:
    """主函数：执行排序并返回结果"""
    sorted_channels = sort_channels_by_custom_order(original_channels, custom_order)
    ##print_channel_list("原始频道列表", original_channels)
    ##print_channel_list("按自定义顺序排序后的频道列表", sorted_channels)
    return sorted_channels


# 定义自定义排序规则（可自行修改）
custom_order = [
    "TVB翡翠台",
    "无线新闻台",
    "广东卫视",
    "广东珠江",
    "广东体育",
    "广东影视",
    "广东新闻",
    "广东民生",
    "大湾区卫视",
    "广东少儿",
    "嘉佳卡通",
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
    "北京卫视",
    "安徽卫视",
    "山东卫视",
    "四川卫视",
    "河南卫视",
    "湖北卫视"
]

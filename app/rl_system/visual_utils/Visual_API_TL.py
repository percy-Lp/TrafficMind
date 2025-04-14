import xml.etree.ElementTree as ET
import re
from colorama import init, Fore, Style, Back
from collections import defaultdict
import sys

# 初始化 colorama
init(autoreset=True)


# 增强版颜色映射
def get_color_state(state):
    color_map = {
        'G': Fore.GREEN + '■' + Style.RESET_ALL,
        'r': Fore.RED + '■' + Style.RESET_ALL,
        's': Fore.YELLOW + '■' + Style.RESET_ALL,
        'y': Fore.YELLOW + '■' + Style.RESET_ALL,
        'g': Fore.GREEN + '■' + Style.RESET_ALL
    }
    return ''.join([color_map.get(c, Fore.WHITE + '■') for c in state])

# 自然语言描述优化
def get_natural_language_description(from_road, to_road, turn):
    direction_map = {'0': '北', '1': '东', '2': '南', '3': '西'}
    turn_map = {'r': '右转', 's': '直行', 'l': '左转', 't': '掉头'}

    try:
        from_dir = direction_map[from_road.split('_')[-1]]
        to_dir = direction_map[to_road.split('_')[-1]]
        turn_desc = turn_map.get(turn, '未知方向')

        return f"{Fore.CYAN}{from_dir}{Style.RESET_ALL}→" + \
            f"{Fore.CYAN}{to_dir}{Style.RESET_ALL} " + \
            f"{Fore.MAGENTA}{turn_desc}"
    except Exception:
        return f"{from_road}→{to_road}({turn})"

# 解析 colightTL.log 文件
def parse_log_file(log_file):
    with open(log_file, 'r') as f:
        lines = f.readlines()
    pattern = re.compile(r'Intersection (\d+): Phase (\d+)')
    log_data = []
    for line in lines:
        match = pattern.match(line.strip())
        if match:
            intersection = int(match.group(1))
            phase = int(match.group(2))
            log_data.append((intersection, phase))
    # 每16行为一个时间步（适用于 4x4 路网）
    time_steps = [log_data[i:i + 16] for i in range(0, len(log_data), 16)]
    return time_steps

def parse_net_file(net_file):
    tree = ET.parse(net_file)
    root = tree.getroot()

    # 解析 tlLogic
    tl_logics = {tl.get('id'): tl for tl in root.findall('tlLogic')}

    # 解析 connection，并按 linkIndex 排序
    connections = {}
    for conn in root.findall('connection'):
        tl = conn.get('tl')
        link_index = conn.get('linkIndex')
        if tl and link_index is not None:
            if tl not in connections:
                connections[tl] = []
            connections[tl].append(conn)

    # 对每个 tl 的 connections 按 linkIndex 排序
    for tl in connections:
        connections[tl].sort(key=lambda x: int(x.get('linkIndex')))

    return tl_logics, connections
def get_phase_state(tl_logic, phase_index):
    phases = tl_logic.findall('phase')
    if 0 <= phase_index < len(phases):
        return phases[phase_index].get('state')
    return None


# 优化后的打印函数
def print_intersection_states(tl_logics, connections, time_steps, selected_tl_id=None):
    # 重组数据结构：{交叉口ID: {时间步: 相位数据}}
    intersection_data = defaultdict(dict)

    # 收集所有需要显示的时间步（每5个）
    target_steps = [t for t in range(len(time_steps)) if t % 5 == 0]

    # 填充数据
    for t in target_steps:
        step_data = time_steps[t]
        for intersection, phase in step_data:
            tl_id = f"intersection_{intersection // 4 + 1}_{intersection % 4 + 1}"
            intersection_data[tl_id][t] = (intersection, phase)

    # 如果指定了路口ID，只打印该路口的信息
    if selected_tl_id:
        if selected_tl_id in intersection_data:
            print(f"\n{Back.CYAN}=== 交叉口 {selected_tl_id} ===")
            tl_id = selected_tl_id
            if not intersection_data.get(tl_id):
                print(f"{Fore.RED} 无记录的时间步数据")
                return

            for t, (intersection, phase) in sorted(intersection_data[tl_id].items()):
                print(f"\n{Fore.YELLOW}🕒 时间步 {t}:")
                tl_logic = tl_logics.get(tl_id)
                state = get_phase_state(tl_logic, phase)

                if not state:
                    print(f"{Fore.RED} 无效相位 {phase}")
                    continue

                # 显示相位信息
                duration = 5 if phase % 2 == 1 else 30
                print(f"  {Fore.WHITE}相位 {phase} ({duration}秒) {get_color_state(state)}")

                # 显示连接状态
                conns = connections.get(tl_id, [])
                groups = defaultdict(list)
                for i, conn in enumerate(conns):
                    key = (conn.get('from'), conn.get('to'), conn.get('dir'))
                    groups[key].append((i, state[i]))

                for key, group in groups.items():
                    from_road, to_road, dir_ = key
                    states = ''.join([s for _, s in group])
                    print(f"  ├─ {get_natural_language_description(from_road, to_road, dir_)}")
                    print(f"  └─ 信号模式: {get_color_state(states)}")
        else:
            print(f"{Fore.RED} 未找到路口 {selected_tl_id}")
    else:
        # 打印所有路口的信息（原逻辑）
        for tl_id in tl_logics.keys():
            print(f"\n{Back.CYAN}=== 交叉口 {tl_id} ===")
            if not intersection_data.get(tl_id):
                print(f"{Fore.RED} 无记录的时间步数据")
                continue

            for t, (intersection, phase) in sorted(intersection_data[tl_id].items()):
                print(f"\n{Fore.YELLOW}🕒 时间步 {t}:")
                tl_logic = tl_logics.get(tl_id)
                state = get_phase_state(tl_logic, phase)

                if not state:
                    print(f"{Fore.RED} 无效相位 {phase}")
                    continue

                # 显示相位信息
                duration = 5 if phase % 2 == 1 else 30
                print(f"  {Fore.WHITE}相位 {phase} ({duration}秒) {get_color_state(state)}")

                # 显示连接状态
                conns = connections.get(tl_id, [])
                groups = defaultdict(list)
                for i, conn in enumerate(conns):
                    key = (conn.get('from'), conn.get('to'), conn.get('dir'))
                    groups[key].append((i, state[i]))

                for key, group in groups.items():
                    from_road, to_road, dir_ = key
                    states = ''.join([s for _, s in group])
                    print(f"  ├─ {get_natural_language_description(from_road, to_road, dir_)}")
                    print(f"  └─ 信号模式: {get_color_state(states)}")



def main(net_file, log_file, selected_tl_id=None):
    tl_logics, connections = parse_net_file(net_file)
    time_steps = parse_log_file(log_file)

    print(f"\n{Back.GREEN}=== 信号灯方案报告 ===")
    print(f"总路口数: {len(tl_logics)}")
    print(f"总时间步: {len(time_steps)}\n")

    print_intersection_states(tl_logics, connections, time_steps, selected_tl_id)

if __name__ == "__main__":
    net_file = r"./data/raw_data/hangzhou_4x4_gudang_18041610_1h/hangzhou_4x4_gudang_18041610_1h.net.xml"
    log_file = r"./data/output_data/tsc/sumo_colight/sumohz4x4/test/logger/TL.log"
    selected_tl_id = sys.argv[1] if len(sys.argv) > 1 else None
    main(net_file, log_file, selected_tl_id)
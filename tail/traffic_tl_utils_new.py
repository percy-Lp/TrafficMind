import xml.etree.ElementTree as ET
import re
from colorama import init, Fore, Style, Back
from collections import defaultdict
import sys
import time

class TrafficLightAnalyzer:
    # 路口名称映射
    INTERSECTION_MAPPING = {
        "intersection_1_1": 0, "intersection_1_2": 1, "intersection_1_3": 2, "intersection_1_4": 3,
        "intersection_2_1": 4, "intersection_2_2": 5, "intersection_2_3": 6, "intersection_2_4": 7,
        "intersection_3_1": 8, "intersection_3_2": 9, "intersection_3_3": 10, "intersection_3_4": 11,
        "intersection_4_1": 12, "intersection_4_2": 13, "intersection_4_3": 14, "intersection_4_4": 15
    }

    # 编号到路口名称的反向映射
    INTERSECTION_ID_TO_NAME = {v: k for k, v in INTERSECTION_MAPPING.items()}

    def __init__(self, net_file, log_file):
        # 初始化 colorama
        init(autoreset=True)
        self.net_file = net_file
        self.log_file = log_file
        self.tl_logics, self.connections = self.parse_net_file()
        self.time_steps = self.parse_log_file()

    # 增强版颜色映射
    def get_color_state(self, state):
        color_map = {
            'G': Fore.GREEN + '■' + Style.RESET_ALL,
            'r': Fore.RED + '■' + Style.RESET_ALL,
            's': Fore.YELLOW + '■' + Style.RESET_ALL,
            'y': Fore.YELLOW + '■' + Style.RESET_ALL,
            'g': Fore.GREEN + '■' + Style.RESET_ALL
        }
        return ''.join([color_map.get(c, Fore.WHITE + '■') for c in state])

    # 自然语言描述优化
    def get_natural_language_description(self, from_road, to_road, turn):
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

    def get_simple_direction_description(self, from_road, to_road, turn):
        """返回简单的方向描述，不带颜色标记"""
        direction_map = {'0': '北', '1': '东', '2': '南', '3': '西'}
        turn_map = {'r': '右转', 's': '直行', 'l': '左转', 't': '掉头'}

        try:
            from_dir = direction_map[from_road.split('_')[-1]]
            to_dir = direction_map[to_road.split('_')[-1]]
            turn_desc = turn_map.get(turn, '未知方向')

            return f"{from_dir}→{to_dir} {turn_desc}"
        except Exception:
            return f"{from_road}→{to_road}({turn})"

    # 解析 colightTL.log 文件
    def parse_log_file(self):
        with open(self.log_file, 'r') as f:
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

    def parse_net_file(self):
        tree = ET.parse(self.net_file)
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

    def get_phase_state(self, tl_logic, phase_index):
        phases = tl_logic.findall('phase')
        if 0 <= phase_index < len(phases):
            return phases[phase_index].get('state')
        return None

    # 优化后的打印函数，参数增加了实时显示选项
    def print_intersection_states(self, selected_tl_name=None, filter_steps=False, real_time_mode=False):
        # 重组数据结构：{交叉口ID: {时间步: 相位数据}}
        intersection_data = defaultdict(dict)

        # 根据filter_steps决定是否过滤时间步
        target_steps = [t for t in range(len(self.time_steps))]
        if filter_steps:
            target_steps = [t for t in range(len(self.time_steps)) if t % 5 == 0]

        # 转换选择的路口名称到ID
        selected_id = self.INTERSECTION_MAPPING.get(selected_tl_name, -1) if selected_tl_name else None

        # 填充数据
        for t in target_steps:
            step_data = self.time_steps[t]
            for intersection, phase in step_data:
                # 转换数字ID回名称
                tl_name = next((k for k, v in self.INTERSECTION_MAPPING.items() if v == intersection), f"unknown_{intersection}")
                intersection_data[tl_name][t] = (intersection, phase)
        
        # 筛选目标路口
        target_tl = selected_tl_name if selected_tl_name in self.INTERSECTION_MAPPING else None

        # 如果指定了路口ID，只打印该路口的信息
        if target_tl:
            print(f"\n{Back.CYAN}=== 交叉口 {selected_tl_name} ===")
            if not intersection_data.get(target_tl):
                print(f"{Fore.RED} 无记录的时间步数据")
                return

            sorted_steps = sorted(intersection_data[target_tl].items())
            index = 0
            while index < len(sorted_steps):
                t, (intersection, phase) = sorted_steps[index]
                print(f"\n{Fore.YELLOW}🕒 时间步 {t}:")
                tl_logic = self.tl_logics.get(target_tl)
                state = self.get_phase_state(tl_logic, phase)

                if not state:
                    print(f"{Fore.RED} 无效相位 {phase}")
                    index += 1
                    continue

                # 新增合并相位逻辑
                if phase % 2 == 1:
                    merged_phases = [phase]
                    merged_duration = 5
                    merged_steps = [t]

                    # 检查后续连续时间步
                    next_index = index + 1
                    while next_index < len(sorted_steps):
                        next_t, (_, next_phase) = sorted_steps[next_index]
                        next_state = self.get_phase_state(tl_logic, next_phase)

                        # 仅合并连续奇数相位且状态相同
                        if (next_phase % 2 == 1 and
                                next_state == state and
                                next_t == merged_steps[-1] + 1):
                            merged_phases.append(next_phase)
                            merged_duration += 5
                            merged_steps.append(next_t)
                            next_index += 1
                        else:
                            break

                    # 显示合并结果
                    if len(merged_phases) > 1:
                        phase_range = f"{min(merged_phases)}-{max(merged_phases)}"
                        time_range = f"{min(merged_steps)}-{max(merged_steps)}"
                        print(f"  {Fore.WHITE}相位 {phase_range} ({merged_duration}秒) {self.get_color_state(state)}")
                        print(f"  {Fore.BLUE}合并时间步: {time_range}")
                        index = next_index  # 跳过已处理项
                    else:
                        print(f"  {Fore.WHITE}相位 {phase} (5秒) {self.get_color_state(state)}")
                else:
                    print(f"  {Fore.WHITE}相位 {phase} (30秒) {self.get_color_state(state)}")

                # 显示连接状态
                conns = self.connections.get(target_tl, [])
                groups = defaultdict(list)
                for i, conn in enumerate(conns):
                    key = (conn.get('from'), conn.get('to'), conn.get('dir'))
                    groups[key].append((i, state[i]))

                for key, group in groups.items():
                    from_road, to_road, dir_ = key
                    states = ''.join([s for _, s in group])
                    print(f"  ├─ {self.get_natural_language_description(from_road, to_road, dir_)}")
                    print(f"  └─ 信号模式: {self.get_color_state(states)}")

                # 如果启用实时模式，添加延迟
                if real_time_mode and index < len(sorted_steps) - 1:
                    time.sleep(5)

                index += 1
        else:
            # 打印所有路口的信息
            for tl_id in self.tl_logics.keys():
                print(f"\n{Back.CYAN}=== 交叉口 {tl_id} ===")
                if not intersection_data.get(tl_id):
                    print(f"{Fore.RED} 无记录的时间步数据")
                    continue

                sorted_steps = sorted(intersection_data[tl_id].items())
                index = 0
                while index < len(sorted_steps):
                    t, (intersection, phase) = sorted_steps[index]
                    print(f"\n{Fore.YELLOW}🕒 时间步 {t}:")
                    tl_logic = self.tl_logics.get(tl_id)
                    state = self.get_phase_state(tl_logic, phase)

                    if not state:
                        print(f"{Fore.RED} 无效相位 {phase}")
                        index += 1
                        continue

                    # 相位合并逻辑
                    if phase % 2 == 1:
                        merged_phases = [phase]
                        merged_duration = 5
                        merged_steps = [t]

                        # 检查后续连续时间步
                        next_index = index + 1
                        while next_index < len(sorted_steps):
                            next_t, (_, next_phase) = sorted_steps[next_index]
                            next_state = self.get_phase_state(tl_logic, next_phase)

                            if (next_phase % 2 == 1 and
                                    next_state == state and
                                    next_t == merged_steps[-1] + 1):
                                merged_phases.append(next_phase)
                                merged_duration += 5
                                merged_steps.append(next_t)
                                next_index += 1
                            else:
                                break

                        # 显示合并结果
                        if len(merged_phases) > 1:
                            phase_range = f"{min(merged_phases)}-{max(merged_phases)}"
                            time_range = f"{min(merged_steps)}-{max(merged_steps)}"
                            print(f"  {Fore.WHITE}相位 {phase_range} ({merged_duration}秒) {self.get_color_state(state)}")
                            print(f"  {Fore.BLUE}合并时间步: {time_range}")
                            index = next_index
                        else:
                            print(f"  {Fore.WHITE}相位 {phase} (5秒) {self.get_color_state(state)}")
                    else:
                        print(f"  {Fore.WHITE}相位 {phase} (30秒) {self.get_color_state(state)}")

                    # 显示连接状态
                    conns = self.connections.get(tl_id, [])
                    groups = defaultdict(list)
                    for i, conn in enumerate(conns):
                        key = (conn.get('from'), conn.get('to'), conn.get('dir'))
                        groups[key].append((i, state[i]))

                    for key, group in groups.items():
                        from_road, to_road, dir_ = key
                        states = ''.join([s for _, s in group])
                        print(f"  ├─ {self.get_natural_language_description(from_road, to_road, dir_)}")
                        print(f"  └─ 信号模式: {self.get_color_state(states)}")

                    # 如果启用实时模式，添加延迟
                    if real_time_mode and not (tl_id == list(self.tl_logics.keys())[-1] and index == len(sorted_steps) - 1):
                        time.sleep(5)

                    index += 1

    def get_intersection_light_data(self, intersection_id):
        """返回特定路口的信号灯数据，适合JSON格式化"""
        # 转换路口ID为名称
        selected_tl_name = self.INTERSECTION_ID_TO_NAME.get(intersection_id)
        if not selected_tl_name:
            return {"error": f"找不到编号为 {intersection_id} 的路口"}
            
        result = {
            "intersection_name": selected_tl_name,
            "time_steps": []
        }
        
        # 重组数据结构
        intersection_data = defaultdict(dict)
        
        # 收集所有时间步
        target_steps = [t for t in range(len(self.time_steps))]
        
        # 填充数据
        for t in target_steps:
            step_data = self.time_steps[t]
            for inter, phase in step_data:
                # 转换数字ID回名称
                tl_name = next((k for k, v in self.INTERSECTION_MAPPING.items() if v == inter), f"unknown_{inter}")
                intersection_data[tl_name][t] = (inter, phase)
                   
        # 如果没有该路口的数据，返回空结果
        if not intersection_data.get(selected_tl_name):
            return {"error": "无记录的时间步数据"}
            
        # 处理相位合并
        sorted_steps = sorted(intersection_data[selected_tl_name].items())
        index = 0
        while index < len(sorted_steps):
            t, (_, phase) = sorted_steps[index]
            tl_logic = self.tl_logics.get(selected_tl_name)
            state = self.get_phase_state(tl_logic, phase)
            
            if not state:
                index += 1
                continue
            
            # 检查是否需要合并相位
            duration = 5 if phase % 2 == 1 else 30
            merged_phases = None
            merged_steps = None
            
            # 对奇数相位进行合并检查
            if phase % 2 == 1:
                merged_phases = [phase]
                merged_steps = [t]
                merged_duration = duration

                # 检查后续连续时间步
                next_index = index + 1
                while next_index < len(sorted_steps):
                    next_t, (_, next_phase) = sorted_steps[next_index]
                    next_state = self.get_phase_state(tl_logic, next_phase)

                    # 仅合并连续奇数相位且状态相同
                    if (next_phase % 2 == 1 and
                            next_state == state and
                            next_t == merged_steps[-1] + 1):
                        merged_phases.append(next_phase)
                        merged_duration += 5
                        merged_steps.append(next_t)
                        next_index += 1
                    else:
                        break

                # 如果有合并，更新处理索引和持续时间
                if len(merged_phases) > 1:
                    index = next_index
                    duration = merged_duration
            
            # 创建时间步数据
            time_step_data = {
                "time_step": t if not merged_steps else f"{min(merged_steps)}-{max(merged_steps)}",
                "phase": phase if not merged_phases else f"{min(merged_phases)}-{max(merged_phases)}",
                "duration": duration,
                "state": state,
                "connections": []
            }
            
            # 添加连接信息
            conns = self.connections.get(selected_tl_name, [])
            groups = defaultdict(list)
            for i, conn in enumerate(conns):
                key = (conn.get('from'), conn.get('to'), conn.get('dir'))
                groups[key].append((i, state[i]))
            
            for key, group in groups.items():
                from_road, to_road, dir_ = key
                states = ''.join([s for _, s in group])
                
                description = self.get_simple_direction_description(from_road, to_road, dir_)
                
                time_step_data["connections"].append({
                    "description": description,
                    "states": states
                })
            
            result["time_steps"].append(time_step_data)
            
            if not merged_phases:
                index += 1
        
        return result

    def analyze_intersection(self, intersection_id=None, filter_steps=False, real_time_mode=False):
        """分析特定路口或所有路口的信号灯情况"""
        print(f"\n{Back.GREEN}=== 信号灯方案报告 ===")
        print(f"总路口数: {len(self.tl_logics)}")
        print(f"总时间步: {len(self.time_steps)}\n")

        # 如果提供了路口编号，转换为路口名称
        selected_tl_name = None
        if intersection_id is not None:
            try:
                intersection_id = int(intersection_id)
                if 0 <= intersection_id <= 15:
                    selected_tl_name = self.INTERSECTION_ID_TO_NAME.get(intersection_id)
                    if not selected_tl_name:
                        print(f"{Fore.RED}错误: 找不到编号为 {intersection_id} 的路口")
                        return
                else:
                    print(f"{Fore.RED}错误: 路口编号必须在 0-15 之间")
                    return
            except ValueError:
                print(f"{Fore.RED}错误: 路口编号必须是一个整数")
                return

        self.print_intersection_states(selected_tl_name, filter_steps, real_time_mode)


def main():
    net_file = r"./data/hangzhou_net.xml"
    log_file = r"./data/tl.log"
    
    # 检查命令行参数
    args = sys.argv[1:]
    
    # 解析命令行参数
    intersection_id = None
    filter_steps = False
    real_time_mode = False
    
    i = 0
    while i < len(args):
        if args[i] == "--id" and i + 1 < len(args):
            try:
                intersection_id = int(args[i + 1])
                i += 2
            except ValueError:
                print(f"{Fore.RED}错误: 路口编号必须是一个整数")
                return
        elif args[i] == "--filter":
            filter_steps = True
            i += 1
        elif args[i] == "--real-time":
            real_time_mode = True
            i += 1
        else:
            intersection_id = args[i] if args[i].isdigit() else None
            if intersection_id:
                intersection_id = int(intersection_id)
            i += 1
    
    # 创建分析器对象
    analyzer = TrafficLightAnalyzer(net_file, log_file)
    
    # 如果没有通过命令行指定路口ID，请求用户输入
    if intersection_id is None and not any(args):
        try:
            user_input = input(f"{Fore.YELLOW}请输入路口编号(0-15)，按Enter显示所有路口: ")
            if user_input.strip() != "":
                try:
                    intersection_id = int(user_input)
                except ValueError:
                    print(f"{Fore.RED}错误: 路口编号必须是一个整数")
                    return
            
            filter_input = input(f"{Fore.YELLOW}是否只显示每5个时间步 (y/n)，默认n: ").lower()
            filter_steps = filter_input.startswith('y')
            
            real_time_input = input(f"{Fore.YELLOW}是否启用实时模式 (y/n)，默认n: ").lower()
            real_time_mode = real_time_input.startswith('y')
        except:
            pass
    
    # 分析路口
    analyzer.analyze_intersection(intersection_id, filter_steps, real_time_mode)

if __name__ == "__main__":
    main()
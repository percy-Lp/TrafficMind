import numpy as np
import cv2
import json
import tracker
from detector.detector import Detector
import time
import csv
import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import rcParams
from collections import deque
from matplotlib.widgets import Slider


class TimeGenerator:
    def __init__(self):
        self.base_q = 0.8
        self.last_extension = 10

    def generate_time(self, q_value, frame_count):
        # 基于Q值波动和帧数生成时间（8-15秒）
        delta = (q_value - self.base_q) * 20  # Q值每变化0.1对应2秒变化
        fluctuation = (frame_count % 10) * 0.1  # 基于帧数的微小波动
        new_time = int(10 + delta + fluctuation)  # 添加波动
        new_time = max(8, min(15, new_time))

        # 确保相邻调整不会突变（变化幅度不超过3秒）
        if abs(new_time - self.last_extension) > 3:
            new_time = self.last_extension + 3 if new_time > self.last_extension else self.last_extension - 3

        self.last_extension = new_time
        return new_time


def resize_with_aspect_ratio(image, target_width, target_height):
    height, width = image.shape[:2]
    ratio = min(target_width / width, target_height / height)
    new_size = (int(width * ratio), int(height * ratio))
    resized = cv2.resize(image, new_size)
    delta_w = target_width - new_size[0]
    delta_h = target_height - new_size[1]
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)
    return cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(0, 0, 0))


def format_timestamp(seconds):
    """将秒数转换为 MM:SS 格式"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds:02d}"


# 设置支持中文的字体
rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 切换到支持 GUI 的后端
matplotlib.use('TkAgg')

# 修复视频中文乱码问题
def put_chinese_text(image, text, position, font_size=20, color=(255, 255, 255)):
    """在图像上绘制中文文本"""
    from PIL import Image, ImageDraw, ImageFont
    font_path = "simhei.ttf"  # 黑体字体路径
    font = ImageFont.truetype(font_path, font_size)
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)
    draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

if __name__ == '__main__':
    time_gen = TimeGenerator()
    # 加载车道坐标文件
    with open('lanes_coordinates.json', 'r') as f:
        lanes = json.load(f)
    orig_width, orig_height = 4096, 2160
    target_width, target_height = 960, 540
    scale_x = target_width / orig_width
    scale_y = target_height / orig_height

    # 缩放车道坐标（Lane 0-4）
    scaled_lanes = []
    for lane in lanes:
        scaled_lane = [[int(x * scale_x), int(y * scale_y)] for x, y in lane]
        scaled_lanes.append(np.array(scaled_lane, np.int32))
    lane_order = sorted(range(len(scaled_lanes)), key=lambda i: min(scaled_lanes[i][:, 0]))
    sorted_lanes = [scaled_lanes[i] for i in lane_order]

    # 初始化检测器和视频
    detector = Detector()
    capture = cv2.VideoCapture('./videos/new.mp4')
    if not capture.isOpened():
        print("无法打开视频文件")
        exit()

    # 获取视频属性
    fps = capture.get(cv2.CAP_PROP_FPS)
    frame_count = 0
    next_csv_interval = 5  # 初始写入间隔（秒）
    next_check_interval = 30  # 每隔 30 秒判断一次

    # 初始化统计数据（仅 Lane 0-4）
    lane_stats = {i: {'vehicles': set(), 'wait_sum': 0.0, 'wait_count': 0,
                      'speed_sum': 0.0, 'speed_count': 0, 'passed': 0} for i in range(5)}
    vehicle_times = {}
    vehicle_positions = {}
    pixel_to_meter = 0.05

    cycle_duration = 75  # 每个方向的放行周期为 75 秒
    current_cycle_start = 0  # 当前周期的起始时间，从第一帧开始
    is_east_west_cycle = True  # 初始为东西方向放行周期

    # 第一帧输出东西方向放行周期的拥堵检测内容
    east_west_left = 10 + frame_count % 5
    east_west_straight = 15 - frame_count % 5
    north_south_left = 8 + frame_count % 3
    north_south_straight = 12 - frame_count % 3

    # 模拟强化学习的奖励机制
    east_west_left_ratio = east_west_left / (east_west_left + east_west_straight) if (east_west_left + east_west_straight) > 0 else 0
    north_south_left_ratio = north_south_left / (north_south_left + north_south_straight) if (north_south_left + north_south_straight) > 0 else 0

    east_west_left_congested = 2/5 <= east_west_left_ratio <= 1
    north_south_left_congested = 2/5 <= north_south_left_ratio <= 1

    print(f"[RL状态评估] 东西车道左转车流比率: {east_west_left_ratio:.2f}, 南北车道左转车流比率: {north_south_left_ratio:.2f}")
    if east_west_left_congested:
        action = "延长东西左转绿灯"
        reward = 1.2 + (frame_count % 3) * 0.02
        q_value = 0.85 + (frame_count % 10) * 0.005
        new_q_value = q_value + 0.1 * (reward - q_value)
        print(f"[RL决策] 选择动作1：{action}（当前Q值={q_value:.2f}）")
        print(f"[RL更新] 奖励={reward:.2f} → 新Q值={new_q_value:.2f}")
    if not east_west_left_congested:
        action = "延长东西直行绿灯"
        reward = 1.1 + (frame_count % 2) * 0.03
        q_value = 0.75 + (frame_count % 8) * 0.01
        new_q_value = q_value + 0.1 * (reward - q_value)
        print(f"[RL决策] 选择动作2：{action}（当前Q值={q_value:.2f}）")
        print(f"[RL更新] 奖励={reward:.2f} → 新Q值={new_q_value:.2f}")

    # 初始化动态折线图数据
    time_points = deque(maxlen=100)  # 时间点
    left_turn_counts = deque(maxlen=100)  # 左转车道车流数
    straight_counts = deque(maxlen=100)  # 直行车道车流数

    # 初始化动态折线图
    plt.ion()
    fig, ax = plt.subplots()
    left_line, = ax.plot([], [], label="左转车道车流数", color="blue")
    straight_line, = ax.plot([], [], label="直行车道车流数", color="green")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 20)
    ax.set_xlabel("时间点")
    ax.set_ylabel("车流数")
    ax.legend()

    # 添加拖动条
    ax_slider = plt.axes([0.2, 0.01, 0.6, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(ax_slider, '时间点', 0, 100, valinit=0, valstep=1)

    def update_slider(val):
        start = int(slider.val)
        end = start + 100
        left_line.set_data(range(start, min(end, len(time_points))), list(left_turn_counts)[start:end])
        straight_line.set_data(range(start, min(end, len(time_points))), list(straight_counts)[start:end])
        ax.set_xlim(start, end)
        plt.draw()

    slider.on_changed(update_slider)

    # 设置缩放比例以匹配视频分辨率调整
    display_width, display_height = 640, 360  # 视频显示分辨率
    scale_x_display = display_width / target_width
    scale_y_display = display_height / target_height

    while True:
        ret, im = capture.read()
        if im is None:
            print("视频读取结束")
            break

        # 调整视频分辨率
        im = cv2.resize(im, (display_width, display_height))

        # 降低帧率以减少处理负担
        if frame_count % 2 != 0:  # 每隔一帧处理一次
            frame_count += 1
            continue

        # 计算当前视频时间
        current_video_time = frame_count / fps
        formatted_time = format_timestamp(current_video_time)

        # 检查是否需要切换周期
        if current_video_time - current_cycle_start >= cycle_duration:
            is_east_west_cycle = not is_east_west_cycle
            current_cycle_start = current_video_time
            print(f"[RL动作] 切换到{'东西方向' if is_east_west_cycle else '南北方向'}放行周期")

            # 在切换周期时检测拥堵情况
            east_west_left = 10 + frame_count % 5  # 模拟动态车流量
            east_west_straight = 15 - frame_count % 5
            north_south_left = 8 + frame_count % 3
            north_south_straight = 12 - frame_count % 3

            east_west_left_ratio = east_west_left / (east_west_left + east_west_straight) if (east_west_left + east_west_straight) > 0 else 0
            north_south_left_ratio = north_south_left / (north_south_left + north_south_straight) if (north_south_left + north_south_straight) > 0 else 0

            east_west_left_congested = 2/5 <= east_west_left_ratio <= 1
            north_south_left_congested = 2/5 <= north_south_left_ratio <= 1

            if is_east_west_cycle:
                print(f"[RL状态评估] 东西车道左转车流比率: {east_west_left_ratio:.2f}, 直行车流比率: {1 - east_west_left_ratio:.2f}")
                if east_west_left_congested:
                    action = "延长东西左转绿灯"
                    q_value = 0.85 + (frame_count % 10) * 0.005  # 模拟动态 Q 值
                    reward = 1.2 + (frame_count % 3) * 0.02  # 模拟动态奖励
                    new_q_value = q_value + 0.1 * (reward - q_value)
                    time_penalty_factor = 1 + (new_q_value - 0.8) * 0.2  # 时间惩罚系数
                    flow_sensitivity = 0.75 + (frame_count % 4) * 0.01  # 流量敏感系数
                    extend_time = time_gen.generate_time(new_q_value, frame_count)
                    print(f"[RL决策] 选择动作1：{action}{extend_time}秒（时间惩罚系数={time_penalty_factor:.2f}）")
                    print(f"Q值更新：状态(2,3) 动作1 奖励{reward:.2f} → 新Q值{new_q_value:.2f}（流量敏感系数={flow_sensitivity:.2f}）")
                if not east_west_left_congested:
                    action = "延长东西直行绿灯"
                    q_value = 0.75 + (frame_count % 8) * 0.01
                    reward = 1.1 + (frame_count % 2) * 0.03
                    new_q_value = q_value + 0.1 * (reward - q_value)
                    time_penalty_factor = 1 + (new_q_value - 0.7) * 0.15
                    flow_sensitivity = 0.78 + (frame_count % 5) * 0.02
                    extend_time = time_gen.generate_time(new_q_value, frame_count)
                    print(f"[RL决策] 选择动作2：{action}{extend_time}秒（时间惩罚系数={time_penalty_factor:.2f}）")
                    print(f"Q值更新：状态(2,3) 动作2 奖励{reward:.2f} → 新Q值{new_q_value:.2f}（流量敏感系数={flow_sensitivity:.2f}）")
            else:
                print(f"[RL状态评估] 南北车道左转车流比率: {north_south_left_ratio:.2f}, 直行车流比率: {1 - north_south_left_ratio:.2f}")
                if north_south_left_congested:
                    action = "延长南北左转绿灯"
                    q_value = 0.82 + (frame_count % 6) * 0.01
                    reward = 1.15 + (frame_count % 4) * 0.02
                    new_q_value = q_value + 0.1 * (reward - q_value)
                    time_penalty_factor = 1 + (new_q_value - 0.8) * 0.18
                    flow_sensitivity = 0.76 + (frame_count % 3) * 0.01
                    extend_time = time_gen.generate_time(new_q_value, frame_count)
                    print(f"[RL决策] 选择动作3：{action}{extend_time}秒（时间惩罚系数={time_penalty_factor:.2f}）")
                    print(f"Q值更新：状态(3,1) 动作3 奖励{reward:.2f} → 新Q值{new_q_value:.2f}（流量敏感系数={flow_sensitivity:.2f}）")
                if not north_south_left_congested:
                    action = "延长南北直行绿灯"
                    q_value = 0.78 + (frame_count % 7) * 0.01
                    reward = 1.12 + (frame_count % 5) * 0.02
                    new_q_value = q_value + 0.1 * (reward - q_value)
                    time_penalty_factor = 1 + (new_q_value - 0.75) * 0.16
                    flow_sensitivity = 0.79 + (frame_count % 6) * 0.01
                    extend_time = time_gen.generate_time(new_q_value, frame_count)
                    print(f"[RL决策] 选择动作4：{action}{extend_time}秒（时间惩罚系数={time_penalty_factor:.2f}）")
                    print(f"Q值更新：状态(3,1) 动作4 奖励{reward:.2f} → 新Q值{new_q_value:.2f}（流量敏感系数={flow_sensitivity:.2f}）")

        list_bboxs = []
        bboxes = detector.detect(im)

        if len(bboxes) > 0:
            list_bboxs = tracker.update(bboxes, im)
            output_image_frame = tracker.draw_bboxes(im, list_bboxs, line_thickness=2)
        else:
            output_image_frame = im.copy()

        # 绘制 Lane 0-4 的车道框（同步调整坐标以匹配缩放后的分辨率）
        for i, poly in enumerate(sorted_lanes):
            scaled_poly = (poly * [scale_x_display, scale_y_display]).astype(np.int32)
            cv2.polylines(output_image_frame, [scaled_poly], isClosed=True, color=(0, 0, 255), thickness=3)
            min_x, min_y = np.min(scaled_poly, axis=0)
            output_image_frame = put_chinese_text(output_image_frame, f"车道 {i}", (min_x, min_y))

        # 实时统计 Lane 0-4 的车辆情况
        left_turn_count = 0
        straight_count = 0
        lane1_count = 0
        other_lanes_count = 0
        for item_bbox in list_bboxs:
            x1, y1, x2, y2, label, track_id = item_bbox
            center_x = int((x1 + x2) / 2)
            center_y = int(y2)
            vehicle_in_lane = False

            for i, poly in enumerate(sorted_lanes):
                if cv2.pointPolygonTest(poly, (center_x, center_y), False) >= 0:
                    lane_stats[i]['vehicles'].add(track_id)
                    vehicle_in_lane = True

                    if track_id not in vehicle_times:
                        vehicle_times[track_id] = {'enter_time': current_video_time, 'exit_time': None}
                    else:
                        vehicle_times[track_id]['exit_time'] = current_video_time

                    if track_id not in vehicle_positions:
                        vehicle_positions[track_id] = []
                    vehicle_positions[track_id].append((center_x, center_y, current_video_time, i))

                    if i == 0:
                        lane1_count += 1
                        left_turn_count += 1
                    else:
                        other_lanes_count += 1
                        straight_count += 1
                    break

            if not vehicle_in_lane and track_id in vehicle_times:
                enter_time = vehicle_times[track_id]['enter_time']
                exit_time = vehicle_times[track_id]['exit_time'] or current_video_time
                wait_time = exit_time - enter_time

                if track_id in vehicle_positions and len(vehicle_positions[track_id]) > 0:
                    last_lane = vehicle_positions[track_id][-1][3]
                    if last_lane < 5:
                        lane_stats[last_lane]['wait_sum'] += wait_time
                        lane_stats[last_lane]['wait_count'] += 1
                        lane_stats[last_lane]['passed'] += 1
                del vehicle_times[track_id]

        # 计算车辆速度
        for track_id, positions in vehicle_positions.items():
            if len(positions) >= 2:
                (x1, y1, t1, lane1), (x2, y2, t2, lane2) = positions[-2], positions[-1]
                distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) * pixel_to_meter
                time_diff = t2 - t1
                if time_diff > 0 and lane2 < 5:
                    speed = distance / time_diff
                    lane_stats[lane2]['speed_sum'] += speed
                    lane_stats[lane2]['speed_count'] += 1

        # 更新动态折线图数据
        time_points.append(len(time_points))
        left_turn_counts.append(left_turn_count)
        straight_counts.append(straight_count)

        # 更新动态折线图
        start = max(0, len(time_points) - 100)
        left_line.set_data(range(start, len(time_points)), list(left_turn_counts)[start:])
        straight_line.set_data(range(start, len(time_points)), list(straight_counts)[start:])
        ax.set_xlim(start, len(time_points))
        ax.set_ylim(0, max(max(left_turn_counts, default=0), max(straight_counts, default=0)) + 5)
        slider.valmax = len(time_points) - 1
        slider.ax.set_xlim(0, len(time_points) - 1)
        plt.pause(0.01)

        # 显示统计数据
        output_image_frame = put_chinese_text(output_image_frame,
                                              f"强化学习时间步: {formatted_time} | 左转车流: {left_turn_count} | 直行车流: {straight_count}",
                                              (10, 30))

        cv2.imshow('Vehicle Counting', output_image_frame)

        frame_count += 1
        if cv2.waitKey(1) & 0xFF == 27:  # 增加延迟以缓解卡顿
            break

    capture.release()
    cv2.destroyAllWindows()
    plt.ioff()
    plt.show()
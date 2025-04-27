import base64
import cv2
import os
import json
import time
import numpy as np
import torch
import supervision as sv
from ultralytics import YOLO
from PIL import Image

def load_models():
    # 加载车辆检测模型
    model1 = YOLO("weights/car.pt").to('cuda')
    # 加载车道线检测模型
    model2 = YOLO("weights/lane.pt").to('cuda')

    # 预热模型
    dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
    _ = model1.predict(source=dummy_img, imgsz=640, verbose=False)
    _ = model2.predict(source=dummy_img, imgsz=640, verbose=False)

    # 转换为半精度
    model1 = model1.half()
    model2 = model2.half()
    
    return model1, model2

# 车道类别与颜色映射
def get_lane_mappings():
    lane_classes = {0: "left_turn", 1: "others", 2: "others"}
    lane_colors = {"left_turn": [0, 255, 0], "others": [255, 0, 0]}
    return lane_classes, lane_colors

# 加载车道坐标
def load_lane_polygons():
    try:
        with open('lanes_coordinates.json', 'r') as f:
            lane_data = json.load(f)
            lane_polygons = []
            for lane in lane_data['lanes']:
                lane_polygons.append(np.array(lane, np.int32))
        print("成功加载车道坐标")
        return lane_polygons
    except Exception as e:
        print(f"加载车道坐标失败: {str(e)}")
        lane_polygons = [
            np.array([[100, 400], [100, 500], [200, 500], [200, 400]], np.int32),
            np.array([[250, 400], [250, 500], [350, 500], [350, 400]], np.int32),
            np.array([[400, 400], [400, 500], [500, 500], [500, 400]], np.int32),
            np.array([[550, 400], [550, 500], [650, 500], [650, 400]], np.int32),
            np.array([[700, 400], [700, 500], [800, 500], [800, 400]], np.int32)
        ]
        print("使用默认车道坐标")
        return lane_polygons

# 初始化统计数据
def init_stats(lane_polygons):
    stats = {i: {'vehicles': set(), 'wait_sum': 0.0, 'wait_count': 0,
                 'speed_sum': 0.0, 'speed_count': 0, 'passed': 0} 
             for i in range(len(lane_polygons))}
    return stats

# 处理单帧图像
def process_image(image, model1, model2, lane_polygons, 
                 stats, vehicle_times, vehicle_positions, 
                 frame_count, pixel_to_meter=0.05, include_stats_on_image=False):
    # 获取车道类别与颜色映射
    lane_classes, lane_colors = get_lane_mappings()
    
    # 并行调用两个模型的推理
    with torch.no_grad():
        results1 = model1.predict(
            source=image,
            imgsz=640,
            device='cuda',
            verbose=False,
            augment=False
        )
        results2 = model2.predict(
            source=image,
            imgsz=640,
            device='cuda',
            verbose=False,
            augment=False
        )
    
    # 处理图像
    annotated_frame = image.copy()
    
    # 处理车道分割结果
    resized_masks = []
    lane_cls_ids = []
    if results2[0].masks is not None:
        masks = results2[0].masks.data.cpu().numpy()
        lane_cls_ids = results2[0].boxes.cls.cpu().numpy().astype(int)
        
        # 将每个分割掩码缩放回原始图像尺寸
        for mask in masks:
            mask_resized = cv2.resize(mask, (image.shape[1], image.shape[0]),
                                  interpolation=cv2.INTER_NEAREST)
            resized_masks.append(mask_resized)
        
        # 绘制车道分割掩码
        for mask, lane_id in zip(resized_masks, lane_cls_ids):
            lane_type = lane_classes.get(int(lane_id), "others")
            color = lane_colors[lane_type]
            overlay = np.zeros_like(image, dtype=np.uint8)
            overlay[mask > 0] = color
            annotated_frame = cv2.addWeighted(annotated_frame, 1.0, overlay, 0.3, 0)
    
    # 处理车辆检测结果并统计
    vehicle_count = 0
    current_time = time.time()
    car_boxes = []
    
    if results1[0].boxes is not None:
        car_boxes = results1[0].boxes.xyxy.cpu().numpy()
        vehicle_count = len(car_boxes)
        
        for box in car_boxes:
            x1, y1, x2, y2 = map(int, box)
            
            # 为每个检测框分配一个跟踪ID
            track_id = frame_count * 1000 + len(car_boxes)
            
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            
            # 计算中心点
            center_x = int((x1 + x2) / 2)
            center_y = int(y2)
            
            # 检查车辆是否在某车道内
            vehicle_in_lane = False
            for mask, lane_id in zip(resized_masks, lane_cls_ids):
                lane_type = lane_classes.get(int(lane_id), "others")
                if 0 <= center_x < image.shape[1] and 0 <= center_y < image.shape[0]:
                    # 检查中心点是否在车道掩码内
                    if mask[center_y, center_x] > 0:
                        # 确定在哪个车道多边形内
                        for i, poly in enumerate(lane_polygons):
                            if cv2.pointPolygonTest(poly, (center_x, center_y), False) >= 0:
                                stats[i]['vehicles'].add(track_id)
                                vehicle_in_lane = True
                                
                                # 更新车辆时间和位置信息
                                if track_id not in vehicle_times:
                                    vehicle_times[track_id] = {'enter_time': current_time, 'exit_time': None}
                                else:
                                    vehicle_times[track_id]['exit_time'] = current_time
                                    
                                if track_id not in vehicle_positions:
                                    vehicle_positions[track_id] = []
                                vehicle_positions[track_id].append((center_x, center_y, current_time, i))
                                break
    
    # 车辆与车道匹配计数（基于车道分割掩码）
    lane_vehicle_count = {"left_turn": 0, "others": 0}
    for mask, lane_id in zip(resized_masks, lane_cls_ids):
        lane_type = lane_classes.get(int(lane_id), "others")
        for box in car_boxes:
            x1, y1, x2, y2 = map(int, box)
            # 车辆框中心点 x
            cx = int((x1 + x2) / 2)
            # 车辆框中心点 y
            cy = int((y1 + y2) / 2)
            # 确保中心点在图像范围内
            if 0 <= cx < image.shape[1] and 0 <= cy < image.shape[0]:
                # 检查中心点是否在车道掩码内
                if mask[cy, cx] > 0:
                    lane_vehicle_count[lane_type] += 1
    
    # 计算车辆速度
    for track_id, positions in vehicle_positions.items():
        if len(positions) >= 2:
            (x1, y1, t1, lane1), (x2, y2, t2, lane2) = positions[-2], positions[-1]
            distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) * pixel_to_meter
            time_diff = t2 - t1
            if time_diff > 0:
                speed = distance / time_diff
                if lane2 < len(lane_polygons):
                    stats[lane2]['speed_sum'] += speed
                    stats[lane2]['speed_count'] += 1
    
    # 图像上显示统计信息
    if include_stats_on_image:
        # 显示总车辆数
        cv2.putText(annotated_frame, f"Total Vehicles: {vehicle_count}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 显示左转车道和其他车道车辆数
        y_pos = 60
        for lane_type, count in lane_vehicle_count.items():
            cv2.putText(annotated_frame, f"{lane_type}: {count}", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            y_pos += 30
    
    return annotated_frame, vehicle_count, stats, lane_vehicle_count, len(resized_masks)

# 处理静态图像
def process_static_image(img_path, model1, model2):
    # 获取数据源
    img = cv2.imread(img_path)
    if img is None:
        img = Image.open(img_path)
        img = np.array(img)
    
    # 获取车道类别与颜色映射
    lane_classes, lane_colors = get_lane_mappings()
    
    # 加载车道坐标
    lane_polygons = load_lane_polygons()
    
    # 第一个模型推理（车辆检测）
    results1 = model1.predict(
        source=img,
        imgsz=640,
        device='cuda',
        verbose=False,
        augment=False
    )
    
    # 第二个模型推理（车道线检测）
    results2 = model2.predict(
        source=img,
        imgsz=640,
        device='cuda',
        verbose=False,
        augment=False
    )
    
    # 保存处理后的图片
    res_img = results1[0].orig_img  # 使用第一个模型的原始图像
    
    # 处理车道分割结果
    annotated_frame = res_img.copy()
    resized_masks = []
    lane_cls_ids = []
    
    if results2[0].masks is not None:
        masks = results2[0].masks.data.cpu().numpy()
        lane_cls_ids = results2[0].boxes.cls.cpu().numpy().astype(int)
        # 将每个分割掩码缩放回原始图像尺寸
        for mask in masks:
            mask_resized = cv2.resize(mask, (res_img.shape[1], res_img.shape[0]),
                                  interpolation=cv2.INTER_NEAREST)
            resized_masks.append(mask_resized)
        
        # 绘制车道分割掩码
        for mask, lane_id in zip(resized_masks, lane_cls_ids):
            lane_type = lane_classes.get(int(lane_id), "others")
            color = lane_colors[lane_type]
            overlay = np.zeros_like(res_img, dtype=np.uint8)
            overlay[mask > 0] = color
            annotated_frame = cv2.addWeighted(annotated_frame, 1.0, overlay, 0.3, 0)
    
    # 处理车辆检测结果
    vehicle_count = 0
    # 各车道统计信息
    lane_stats = {}
    car_boxes = []
    
    # 在图像上绘制车道
    for i, poly in enumerate(lane_polygons):
        cv2.polylines(annotated_frame, [poly], isClosed=True, color=(0, 0, 255), thickness=2)
        min_x, min_y = np.min(poly, axis=0)
        cv2.putText(annotated_frame, f"Lane {i}", (min_x, min_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        lane_stats[i] = {'count': 0}
        
    if results1[0].boxes is not None:
        car_boxes = results1[0].boxes.xyxy.cpu().numpy()
        vehicle_count = len(car_boxes)
        
        for box in car_boxes:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            
            # 确定车辆所在车道
            center_x = int((x1 + x2) / 2)
            center_y = int(y2)
            
            # 检查车辆是否在某车道内
            for i, poly in enumerate(lane_polygons):
                if cv2.pointPolygonTest(poly, (center_x, center_y), False) >= 0:
                    lane_stats[i]['count'] += 1
                    # 在图像上标注车辆所在车道
                    cv2.putText(annotated_frame, f"In Lane {i}", (x1, y1-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                    break
    
    # 车辆与车道匹配计数（基于车道分割掩码）
    lane_vehicle_count = {"left_turn": 0, "others": 0}
    for mask, lane_id in zip(resized_masks, lane_cls_ids):
        lane_type = lane_classes.get(int(lane_id), "others")
        for box in car_boxes:
            x1, y1, x2, y2 = map(int, box)
            # 车辆框中心点 x
            cx = int((x1 + x2) / 2)
            # 车辆框中心点 y
            cy = int((y1 + y2) / 2)
            # 确保中心点在图像范围内
            if 0 <= cx < res_img.shape[1] and 0 <= cy < res_img.shape[0]:
                # 检查中心点是否在车道掩码内
                if mask[cy, cx] > 0:
                    lane_vehicle_count[lane_type] += 1
    
    # 在图像上显示总体统计信息
    cv2.putText(annotated_frame, f"Total Vehicles: {vehicle_count}", (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # 显示左转车道和其他车道车辆数
    y_pos = 60
    for lane_type, count in lane_vehicle_count.items():
        cv2.putText(annotated_frame, f"{lane_type}: {count}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y_pos += 30
    
    # 显示各车道车辆数
    y_pos += 10
    for lane_id, stats in lane_stats.items():
        cv2.putText(annotated_frame, f"Lane {lane_id}: {stats['count']} vehicles", 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y_pos += 30
    
    # 生成标签
    labels = []
    if results1[0].boxes is not None:
        boxes = results1[0].boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            x, y = float(box.xyxy[0][0]), float(box.xyxy[0][1])
            labels.append(f"CLASS: {model1.model.names[cls_id]} CF: {conf:.2f} x:{x:.1f} y:{y:.1f}")
    
    if results2[0].masks is not None:
        for i, mask in enumerate(results2[0].masks):
            cls_id = int(results2[0].boxes.cls[i])
            labels.append(f"LANE: {model2.model.names[cls_id]}")
    
    # 添加车辆计数和车道统计信息
    labels.append(f"总车辆数: {vehicle_count}")
    
    # 添加左转车道和其他车道车辆数
    for lane_type, count in lane_vehicle_count.items():
        labels.append(f"{lane_type}: {count}")
    
    # 添加各车道车辆数
    for lane_id, stats in lane_stats.items():
        labels.append(f"车道 {lane_id}: {stats['count']} 辆车")
    
    # 构建交通统计数据
    traffic_stats = []
    for lane_id, stats in lane_stats.items():
        traffic_stats.append({
            'lane_id': lane_id,
            'vehicle_count': stats['count'],
            'avg_wait_time': 0.0,
            'avg_speed': 0.0,
            'passed_count': 0
        })
    
    return annotated_frame, labels, traffic_stats

# 重置统计数据
def reset_stats(lane_polygons):
    return {i: {'vehicles': set(), 'wait_sum': 0.0, 'wait_count': 0,
               'speed_sum': 0.0, 'speed_count': 0, 'passed': 0} 
           for i in range(len(lane_polygons))} 
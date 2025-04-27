import base64
import cv2
import os
import json
import time
import random
import string
import threading
import re
import logging
import torch
import numpy as np
import supervision as sv
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image
from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, emit
from pprint import pprint

# 设置日志输出
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

from classes.sql_connect import SQLManager
from ultralytics import YOLO
from utils.flask_utils import *

# 导入预测和计算相关的工具函数
import detection_utils as det_utils
# 导入强化学习交通控制器
from rf_learning_utils import TrafficRLController
# 导入交通指标可视化工具
import traffic_metrics_utils as tmu
# 导入交通信号灯分析工具
from traffic_tl_utils_new import TrafficLightAnalyzer

#配置
load_dotenv(override=True, dotenv_path='config/end-back.env')
# 服务器配置
HOST_NAME = os.environ['HOST_NAME']
PORT = int(os.environ['PORT'])
# 超时限制
TOLERANT_TIME_ERROR = int(os.environ['TOLERANT_TIME_ERROR'])
# 获取当前文件夹的路径
current_dir = os.getcwd()
# 拼接文件夹路径
BEFORE_IMG_PATH = os.path.join(current_dir, 'static', os.environ['BEFORE_IMG_PATH'])
AFTER_IMG_PATH = os.path.join(current_dir, 'static', os.environ['AFTER_IMG_PATH'])
BEFORE_VIDEO_PATH = os.path.join(current_dir, 'static', os.environ['BEFORE_VIDEO_PATH'])
AFTER_VIDEO_PATH = os.path.join(current_dir, 'static', os.environ['AFTER_VIDEO_PATH'])

# 数据库配置
MYSQL_HOST = os.environ['MYSQL_HOST']
MYSQL_PORT = os.environ['MYSQL_PORT']
MYSQL_user = os.environ['MYSQL_user']
MYSQL_password = os.environ['MYSQL_password']
MYSQL_db = os.environ['MYSQL_db']
MYSQL_charset = os.environ['MYSQL_charset']
# 实例化数据库
db = SQLManager(host=MYSQL_HOST, port=eval(MYSQL_PORT), user=MYSQL_user,
				passwd=MYSQL_password, db=MYSQL_db, charset=MYSQL_charset)

# 加载模型
model1, model2 = det_utils.load_models()

box_annotator = sv.BoxAnnotator(
    thickness=2,
    text_thickness=1,
    text_scale=0.5
)

app = Flask(__name__, static_folder='static')
# 允许跨域请求
socketio = SocketIO(app, cors_allowed_origins="*")

# 创建全局RL控制器和线程锁
rl_controller = TrafficRLController(model=model1)
rl_results = []
rl_thread = None
rl_thread_lock = threading.Lock()
rl_processing = False

# session设置
app.config['SECRET_KEY'] = 'my-secret-key'  # 设置密钥
app.config['PERMANENT_SESSION_LIFETIME'] = 15 * 60 # session时间: 5分钟
# 拦截器白名单
whitelist = ['/', '/login', '/photo', '/recognize', '/recognizeVideo', '/map_point_click', '/api/congestion']
# 拦截器
@app.before_request
def interceptor():

    if request.path.startswith('/static/'):
        # 如果请求路径以 /static/ 开头，则放行
        return

    if request.path in whitelist:
        # 白名单放行
        return
    if not session.get('username'):
        # 检查是否已登录
        return wrap_unauthorized_return_value('Unauthorized')


# 添加header解决跨域
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    return response

@app.route("/")
def start_server():
    return "欢迎使用yolo系统！后端启动成功！(*^▽^*)"


@app.route('/login', methods=["POST"])
def login():
    try:
        # 获取 JSON 格式的数据
        data = request.json
        username = data.get('username').strip()
        password = data.get('password').strip()
        user_info = db.get_one("SELECT * FROM user WHERE username=%s", (username))
        if user_info and user_info['password'] == password:
            # 存储session
            session['username'] = username
            return wrap_ok_return_value({'id':user_info['id'],
                                         'avatar':user_info['avatar'],
                                         'username':user_info['username']})
        return wrap_error_return_value('错误的用户名或密码！')
    # 登陆失败
    except:
        return wrap_error_return_value('系统繁忙，请稍后再试！')

@app.route('/logOut', methods=["get"])
def log_out():
    session.clear()
    return wrap_ok_return_value('账号已退出！')

# 查询用户信息（分页查询）
@app.route('/usersList/<int:page>', methods=['GET'])
def get_user_list(page):
    page_from = int((page - 1) * 10)
    page_to = int(page)*10
    select_sql = f"select id, username, avatar, email, grade from user limit {page_from}, {page_to}"
    user_list = db.get_list(select_sql)
    # pprint(user_list)
    return wrap_ok_return_value(user_list)
# 修改用户信息
@app.route('/updateUser', methods=['POST'])
def update_user():
    user_data = request.json
    user_id = user_data.get('id')
    username = user_data.get('username')
    avatar = user_data.get('avatar')
    email = user_data.get('email')
    grade = user_data.get('grade')

    update_sql = f"UPDATE user SET username='{username}', email='{email}', grade='{grade}' WHERE id={user_id}"
    db.modify(update_sql)
    return wrap_ok_return_value('更新成功')
@app.route("/photo", methods=["POST"])
def recognize_base64():
    # 获取前端传递的 base64 图片数据
    photo_data = request.form.get('photo')
    # 去掉 base64 编码中的前缀
    photo_data = photo_data.replace('data:image/png;base64,', '')
    # 解码 base64 数据为二进制数据
    image_data = base64.b64decode(photo_data)
    # 保存为文件
    before_img_path = save_img_base64(image_data, path=BEFORE_IMG_PATH)
    # 返回结果
    return yolo_res(before_img_path=before_img_path)

# 上传视频文件
@app.route('/recognizeVideo', methods=['POST'])
def recognizeVideo():
    if 'file' not in request.files:
        return wrap_error_return_value('没有文件上传')
    file = request.files['file']
    # 如果文件不存在 或者 文件类型不是mp4
    if not file or not allowed_file(file.filename, {'mp4'}):
        return wrap_error_return_value('不支持该视频格式')
    video_url = save_file(file.filename, file, BEFORE_VIDEO_PATH)
    return wrap_ok_return_value(video_url)


@app.route("/recognize", methods=["POST"])
def recognize_photo():
    if 'file' not in request.files:
        return wrap_error_return_value('没有文件上传')
    file = request.files['file']
    # 如果文件不存在 或者 文件类型不是mp4
    if not file or not allowed_file(file.filename, {'jpg', 'png', 'jpeg'}):
        return wrap_error_return_value('不支持该图片格式')
    # 保存未处理的图片
    before_img_path = save_file(file.filename, file, BEFORE_IMG_PATH)
    # yolo处理图片
    return yolo_res(before_img_path)

# yolo 处理图片
def yolo_res(before_img_path):
    try:
        # 处理静态图像（调用detection_utils中的函数）
        annotated_frame, labels, traffic_stats = det_utils.process_static_image(before_img_path, model1, model2)
        # 生成唯一的文件名
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        random_suffix = ''.join(random.choice(string.ascii_lowercase) for i in range(5))
        result_filename = f"{timestamp}_{random_suffix}.jpg"
        # 保存结果图片
        after_img_path = os.path.join(AFTER_IMG_PATH, result_filename)
        cv2.imwrite(after_img_path, annotated_frame)
        # 返回相对路径
        relative_path = os.path.join('static', os.environ['AFTER_IMG_PATH'], result_filename)
        return wrap_ok_return_value({
            'labels': labels,
            'after_img_path': relative_path,
            'traffic_stats': traffic_stats
        })
    except Exception as e:
        pprint(str(e))
        return wrap_error_return_value('服务器繁忙，请稍后再试！')

# ws视频处理
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Invalid request, missing 'message'"}), 400
    message = data['message']
    # 发送后端想发送的信息
    socketio.emit('message', message)
    return jsonify({"status": "message sent"}), 200

@socketio.on('connect')
def handle_connect():
    print(f'Client {request.sid} connected')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client {request.sid} disconnected')
    global cap
    if cap is not None:
        cap.release()
        cap = None
is_video_stop = False
is_video_pause = False
last_video_path = ''
cap = None
@socketio.on('start_video_detection')
def handle_start_video_detection(data):
    # 全局变量
    global last_video_path, is_video_pause, is_video_stop, cap
    if 'videoPath' not in data:
        emit('error', {'message': 'No video path provided'})
        return
    video_path = data['videoPath']
    # 如果视频路径与 last_video_path 一样 并且是 暂停状态 则继续预测
    if video_path == last_video_path and is_video_pause:
        is_video_pause = False
        print('继续预测')
        return
    # 如果视频路径与 last_video_path 一样 并且是 继续状态 则暂停预测
    if video_path == last_video_path and not is_video_pause:
        is_video_pause = True
        print('暂停预测')
        return
    # 如果视频路径与 last_video_path 不一样 （则释放视频，重新开始预测
    if video_path!= last_video_path:
        if cap is not None:
            cap.release()
        last_video_path = video_path
        cap = cv2.VideoCapture(video_path)
        socketio.start_background_task(process_video, request.sid)

def process_video(sid):
    global cap, is_video_pause
    if not cap.isOpened():
        socketio.emit('error', {'message': 'Failed to open video file'}, room=sid)
        return
    # 获取视频原始尺寸
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # 加载车道坐标
    lane_polygons = det_utils.load_lane_polygons()
    # 初始化统计数据
    stats = det_utils.init_stats(lane_polygons)
    vehicle_times = {}
    vehicle_positions = {}
    frame_count = 0
    try:
        while cap.isOpened():
            if is_video_pause:
                continue
            ret, frame = cap.read()
            if not ret:
                break

            # 处理单帧图像（调用detection_utils中的函数）
            annotated_frame, vehicle_count, stats, lane_vehicle_count, lane_types_count = det_utils.process_image(
                frame, model1, model2, lane_polygons, 
                stats, vehicle_times, vehicle_positions, 
                frame_count, include_stats_on_image=False
            )

            # 编码并发送结果
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            result, buffer = cv2.imencode('.jpg', annotated_frame, encode_param)
            jpg_as_text = base64.b64encode(buffer).decode()

            # 发送图像和统计数据
            detection_stats = {
                'total_vehicles': vehicle_count,
                'lane_stats': lane_vehicle_count,
                'lane_types': lane_types_count
            }

            socketio.emit('video_frame', {
                'image': jpg_as_text, 
                'stats': detection_stats
            }, room=sid)
            
            frame_count += 1
            
    except Exception as e:
        socketio.emit('error', {'message': str(e)}, room=sid)
    finally:
        cap.release()

# ws摄像头camera处理
# 全局变量
real_time_frame_count = 0

@socketio.on('frame')
def handle_frame(data):
    global real_time_frame_count
    
    sid = request.sid
    base64_image = data['imageData']
    image = base64.b64decode(base64_image)
    image = np.frombuffer(image, dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    
    # 加载车道坐标
    lane_polygons = det_utils.load_lane_polygons()
    
    # 如果没有初始化统计数据，就初始化
    stats = det_utils.init_stats(lane_polygons)
    vehicle_times = {}
    vehicle_positions = {}
    
    # 处理单帧图像（调用detection_utils中的函数）
    annotated_frame, vehicle_count, stats, lane_vehicle_count, lane_types_count = det_utils.process_image(
        image, model1, model2, lane_polygons, 
        stats, vehicle_times, vehicle_positions, 
        real_time_frame_count, include_stats_on_image=False
    )
    
    # 编码并发送结果
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, buffer = cv2.imencode('.jpg', annotated_frame, encode_param)
    jpg_as_text = base64.b64encode(buffer).decode()
    full_image_data = f"data:image/jpeg;base64,{jpg_as_text}"
    
    # 发送图像和统计数据
    detection_stats = {
        'total_vehicles': vehicle_count,
        'lane_stats': lane_vehicle_count,
        'lane_types': lane_types_count
    }
    
    emit('prediction', {
        'image': full_image_data, 
        'stats': detection_stats
    }, room=sid)
    
    real_time_frame_count += 1

# 添加WebSocket事件，用于RL输出
@socketio.on('start_rl_processing')
def handle_start_rl_processing(data=None):
    """处理前端发起的强化学习处理请求"""
    sid = request.sid
    print(f'Client {sid} requested RL processing')
    
    video_path = None
    # 从前端传递的数据中获取视频路径
    if data and 'videoPath' in data:
        video_path = data['videoPath']
        print(f'接收到前端指定的视频路径: {video_path}')
    
    # 调用rl_process_video函数并传入sid和视频路径
    result = rl_process_video_with_sid(sid, video_path)

# 强化学习交通控制(WebSocket)
def rl_process_video_with_sid(sid, video_path=None):
    """使用WebSocket方式处理强化学习视频并实时发送结果"""
    global rl_thread, rl_results, rl_processing
    
    # 检查是否已经有处理在进行
    with rl_thread_lock:
        if rl_processing:
            socketio.emit('rl_processing_status', 
                         {'status': 'error', 'message': '已有强化学习处理任务在进行中'}, 
                         room=sid)
            return False
    
    # 确保视频目录存在
    if not os.path.exists(BEFORE_VIDEO_PATH):
        os.makedirs(BEFORE_VIDEO_PATH, exist_ok=True)
        socketio.emit('rl_processing_status', 
                     {'status': 'warning', 'message': '视频目录不存在，已创建新目录'}, 
                     room=sid)

    if not video_path:
        # 查找可用的视频文件
        print(f"未提供视频路径，查找视频文件，路径: {BEFORE_VIDEO_PATH}")
        all_files = os.listdir(BEFORE_VIDEO_PATH)
        print(f"目录中所有文件: {all_files}")
        
        video_files = [f for f in all_files if f.lower().endswith(('.mp4', '.avi', '.mov'))]
        if not video_files:
            error_msg = '没有可用的视频文件，请先上传视频'
            print(error_msg)
            socketio.emit('rl_processing_status', 
                         {'status': 'error', 'message': error_msg}, 
                         room=sid)
            return False
        
        # 按修改时间排序，获取最新的视频
        video_files.sort(key=lambda x: os.path.getmtime(os.path.join(BEFORE_VIDEO_PATH, x)), reverse=True)
        video_path = os.path.join(BEFORE_VIDEO_PATH, video_files[0])
        print(f"使用最新上传的视频: {video_path}")
    else:
        # 验证前端传递的视频路径是否存在
        if not os.path.exists(video_path) or not os.access(video_path, os.R_OK):
            error_msg = f'指定的视频文件不存在或无法读取: {video_path}'
            print(error_msg)
            socketio.emit('rl_processing_status', 
                         {'status': 'error', 'message': error_msg}, 
                         room=sid)
            return False
        print(f"使用前端指定的视频路径: {video_path}")
    
    # 检查视频文件大小和属性
    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    print(f"视频文件大小: {file_size_mb:.2f} MB")
    
    # 预先确定视频处理参数
    frame_process_params = {
        'process_every_n_frames': 1,
        'max_frames': None,
        'resize_factor': 1.0,
    }
    
    # 视频大小和属性检测，为大视频调整处理参数
    try:
        # 打开视频获取属性
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("无法打开视频文件")
            
        # 获取基本属性
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        # 关闭视频
        cap.release()
        
        print(f"视频属性: {width}x{height}, {fps} FPS, {duration:.2f}秒, {frame_count}帧")
        
        # 优化处理参数
        frame_process_params['process_every_n_frames'] = 2
            
        # 1. 文件大小超过50MB
        if file_size_mb > 50:
            frame_process_params['process_every_n_frames'] = 3
            
        # 2. 视频时长超过1分钟
        if duration > 60:
            frame_process_params['process_every_n_frames'] = 4
            
        # 3. 超高分辨率视频
        if width * height > 1280 * 720:
            frame_process_params['resize_factor'] = 1280 / max(width, 1)
            
        # 4. 超长视频（超过3分钟）
        if duration > 180:
            frame_process_params['max_frames'] = int(fps * 120)  # 只处理前2分钟
            
        # 对于特别大的视频（同时满足多个条件）
        if file_size_mb > 300 and duration > 120 and width * height > 1280 * 720:
            frame_process_params['process_every_n_frames'] = 6
            frame_process_params['resize_factor'] = 960 / max(width, 1)
            
        # 输出优化信息
        optimization_msg = []
        if frame_process_params['process_every_n_frames'] > 1:
            optimization_msg.append(f"每隔{frame_process_params['process_every_n_frames']}帧分析一帧")
        if frame_process_params['resize_factor'] < 1.0:
            new_width = int(width * frame_process_params['resize_factor'])
            new_height = int(height * frame_process_params['resize_factor'])
            optimization_msg.append(f"降低分辨率到{new_width}x{new_height}")
        if frame_process_params['max_frames'] is not None:
            max_seconds = frame_process_params['max_frames'] / fps
            optimization_msg.append(f"处理前{max_seconds:.1f}秒的内容")
            
        if optimization_msg:
            socketio.emit('rl_processing_status', 
                        {'status': 'info', 'message': f'视频较大({file_size_mb:.1f}MB, {duration:.1f}秒), 已优化处理策略: ' + ', '.join(optimization_msg)}, 
                        room=sid)
            
    except Exception as e:
        # 使用默认参数继续处理
        print(f"视频属性检测失败: {str(e)}")

    print(f"使用视频文件: {video_path}, 处理参数: {frame_process_params}")
    socketio.emit('rl_processing_status', 
                 {'status': 'info', 'message': f'使用视频: {os.path.basename(video_path)}'}, 
                 room=sid)
    
    # 清空之前的结果
    rl_results.clear()
    
    # 设置心跳间隔（秒）
    heartbeat_interval = 5
    last_heartbeat_time = time.time()
    
    # 定义回调函数，用于实时发送RL输出
    def rl_output_callback(output, is_efficiency_data=False):
        # 检查是否需要发送心跳
        nonlocal last_heartbeat_time
        current_time = time.time()
        if current_time - last_heartbeat_time >= heartbeat_interval:
            health_check(sid)
            last_heartbeat_time = current_time
        
        # 处理不同类型的输出
        if is_efficiency_data and isinstance(output, dict):
            # 发送效率数据到前端
            print(f"发送效率数据到客户端 {sid}: {output}")
            socketio.emit('rl_efficiency_data', output, room=sid)
        else:
            # 发送普通文本输出
            print(f"发送RL输出到客户端 {sid}: {output[:30]}...")
            socketio.emit('rl_output', {'message': output}, room=sid)
    
    # 创建并启动新线程处理视频
    def process_video_thread(video_path, process_params):
        global rl_results, rl_processing
        try:
            # 设置处理中标志
            with rl_thread_lock:
                rl_processing = True
            
            socketio.emit('rl_processing_status', 
                         {'status': 'processing', 'message': f'开始处理视频: {os.path.basename(video_path)}'}, 
                         room=sid)
            
            # 发送初始心跳
            health_check(sid)
                
            # 创建一个新的RL控制器，传入回调函数和处理参数
            controller = TrafficRLController(callback=rl_output_callback, process_params=process_params)
            
            # 调用RL控制器处理视频
            results = controller.process_video(video_path, show_video=False, save_output=True)
            
            # 更新结果
            with rl_thread_lock:
                rl_results = results
                
            # 处理完成通知
            socketio.emit('rl_complete', 
                         {'status': 'completed', 'message': '强化学习分析完成'}, 
                         room=sid)
        except Exception as e:
            print(f"RL处理异常: {str(e)}")
            socketio.emit('rl_processing_status', 
                         {'status': 'error', 'message': f'处理出错: {str(e)}'}, 
                         room=sid)
        finally:
            health_check(sid)
            # 处理完成，清除标志
            with rl_thread_lock:
                rl_processing = False
    
    # 启动线程
    rl_thread = threading.Thread(target=process_video_thread, args=(video_path, frame_process_params))
    # 设置为守护线程，防止阻塞主线程
    rl_thread.daemon = True
    rl_thread.start()
    
    socketio.emit('rl_processing_status', 
                 {'status': 'started', 'message': '强化学习视频处理已在后台启动'}, 
                 room=sid)
    return True

# 强化学习交通控制(HTTP API)
@app.route('/rl_process_video', methods=['POST'])
def rl_process_video():
    global rl_thread, rl_results, rl_processing
    
    # 获取请求的sid用于WebSocket通信
    sid = request.headers.get('X-Socket-ID')
    
    # 获取视频路径
    data = request.json
    video_path = data.get('video_path')
    
    if sid:
        # 如果有socket ID，使用WebSocket方式
        success = rl_process_video_with_sid(sid, video_path)
        if success:
            return wrap_ok_return_value('强化学习视频处理已在后台启动')
        else:
            return wrap_error_return_value('强化学习处理启动失败')
    else:
        # 检查是否已经有处理在进行
        with rl_thread_lock:
            if rl_processing:
                return wrap_error_return_value('已有强化学习处理任务在进行中')
        
        # 如果前端没有提供路径，使用最新上传的视频
        if not video_path:
            # 获取BEFORE_VIDEO_PATH文件夹中最新的视频文件
            video_files = [f for f in os.listdir(BEFORE_VIDEO_PATH) if f.lower().endswith(('.mp4', '.avi', '.mov'))]
            if not video_files:
                return wrap_error_return_value('没有可用的视频文件')
            
            # 按修改时间排序，获取最新的视频
            video_files.sort(key=lambda x: os.path.getmtime(os.path.join(BEFORE_VIDEO_PATH, x)), reverse=True)
            video_path = os.path.join(BEFORE_VIDEO_PATH, video_files[0])
        else:
            # 验证前端传递的视频路径
            if not os.path.exists(video_path) or not os.access(video_path, os.R_OK):
                return wrap_error_return_value(f'指定的视频文件不存在或无法读取: {video_path}')
        
        # 清空之前的结果
        rl_results.clear()
        
        # 启动线程
        process_params = {
            'process_every_n_frames': 1,
            'max_frames': None,
            'resize_factor': 1.0,
        }
        
        rl_thread = threading.Thread(target=process_video_thread, args=(video_path, process_params))
        rl_thread.daemon = True
        rl_thread.start()
        
        return wrap_ok_return_value('强化学习视频处理已在后台启动')

# 获取强化学习处理结果
@app.route('/rl_results', methods=['GET'])
def get_rl_results():
    global rl_results, rl_processing
    
    with rl_thread_lock:
        processing = rl_processing
        current_results = rl_results.copy()
    
    return wrap_ok_return_value({
        'processing': processing,
        'results': current_results
    })

# 检查强化学习处理状态
@app.route('/rl_status', methods=['GET'])
def get_rl_status():
    global rl_processing
    
    with rl_thread_lock:
        processing = rl_processing
    
    return wrap_ok_return_value({
        'processing': processing
    })

@app.route('/map_point_click', methods=['POST'])
def map_point_click():
    try:
        data = request.json
        index = data.get('index')
        print(f"收到地图点击事件，点击的索引为: {index}")
        
        # 获取训练指标数据
        try:
            training_metrics = tmu.get_training_metrics_data()
            print(f"成功获取训练指标数据")
        except Exception as e:
            print(f"获取训练指标数据出错: {str(e)}")
            # 提供一个最小化的图表结构，
            training_metrics = {
                'title': {'text': ''},
                'xAxis': {'type': 'category', 'data': []},
                'yAxis': {'type': 'value'},
                'series': []
            }
        
        # 如果提供了索引，则获取对应路口的数据
        intersection_data = None
        traffic_light_data = None
        
        if index is not None:
            try:
                # 获取路口数据
                try:
                    intersection_data = tmu.get_intersection_data(index)
                    print(f"成功获取路口 {index} 数据")
                    
                    # 单独提取改善数据
                    improvement_data = None
                    if 'improvement_data' in intersection_data:
                        improvement_data = intersection_data['improvement_data']
                        # 强制重新计算
                        try:
                            current_dir = os.path.dirname(os.path.abspath(__file__))
                            log_file = os.path.join(current_dir, 'data', 'model_eva.log')

                            if os.path.exists(log_file):
                                # 导入traffic_metrics_utils中的函数进行直接计算
                                from traffic_metrics_utils import calculate_improvement, softplus_transform
                                
                                # 重新计算改善数据
                                pattern = re.compile(
                                    r"Test step:\d+/\d+,\s*travel time\s*:\s*([\d\.]+),.*?queue:\s*([\d\.]+),\s*delay:\s*([\d\.]+),\s*throughput:\s*(\d+)"
                                )
                                
                                # 分配权重
                                w1 = {'speed':0.1, 'flow':0.1, 'low_delay':0.6, 'throughput':0.2}
                                w2 = {'low_delay':0.50, 'total_delay':0.50}
                                
                                with open(log_file, 'r', encoding='utf-8') as f:
                                    lines = f.readlines()
                                    
                                prev = {'tt':None, 'q':None, 'd':None, 'tp':None}
                                results = []
                                
                                for line in lines:
                                    m = pattern.search(line)
                                    if not m:
                                        continue
                                        
                                    curr = {
                                        'tt': float(m.group(1)),
                                        'q': float(m.group(2)),
                                        'd': float(m.group(3)),
                                        'tp': int(m.group(4))
                                    }
                                    
                                    if prev['tt'] is not None:

                                        prev_speed = 1/prev['tt'] if prev['tt']>0 else 0
                                        curr_speed = 1/curr['tt'] if curr['tt']>0 else 0
                                        prev_flow = 1/prev['q'] if prev['q']>0 else 0
                                        curr_flow = 1/curr['q'] if curr['q']>0 else 0
                                        prev_ld = 1/prev['d'] if prev['d']>0 else 0
                                        curr_ld = 1/curr['d'] if curr['d']>0 else 0
                                        

                                        imp = {
                                            'speed': calculate_improvement(prev_speed, curr_speed, False),
                                            'flow': calculate_improvement(prev_flow, curr_flow, False),
                                            'low_delay': calculate_improvement(prev_ld, curr_ld, False),
                                            'throughput': calculate_improvement(prev['tp'], curr['tp'], False),
                                        }
                                        

                                        prev_td = prev['q'] * prev['d']
                                        curr_td = curr['q'] * curr['d']
                                        imp['total_delay'] = calculate_improvement(prev_td, curr_td, True)
                                        

                                        raw_old = sum(imp[k] * w1[k] for k in w1)
                                        raw_new = sum(imp[k] * w2[k] for k in w2)
                                        

                                        old_overall = softplus_transform(raw_old, beta=2.0, offset=0.0)
                                        new_overall = softplus_transform(raw_new, beta=2.0, offset=0.0)
                                        

                                        results.append({
                                            'congestion_decrease': old_overall,
                                            'delay_decrease': new_overall
                                        })
                                    
                                    prev = curr

                                # 如果有结果，使用最新的作为当前显示值
                                if results:
                                    # 保存最新的结果作为当前显示值
                                    improvement_data = results[-1]
                                    print(f"计算得到 {len(results)} 组改善数据，用于前端循环显示")
                                else:
                                    print("未计算出任何改善数据")
                        except Exception as e:
                            print(f"重新计算改善数据失败: {str(e)}")
                            pass
                except Exception as e:
                    print(f"获取路口数据失败: {str(e)}")
                    intersection_data = None
                
                # 获取信号灯数据
                try:
                    # 获取SUMO配置文件路径
                    net_file = os.path.join(os.path.dirname(__file__), 'data','hangzhou_net.xml')
                    log_file = os.path.join(os.path.dirname(__file__), 'data', 'tl.log')
                    
                    # 检查文件是否存在
                    if not os.path.exists(log_file) or not os.path.exists(net_file):
                        print(f"错误：信号灯配置文件或日志文件不存在")
                        traffic_light_data = {"error": "信号灯数据不可用：配置文件不存在"}
                    else:
                        # 创建分析器并获取信号灯数据
                        analyzer = TrafficLightAnalyzer(net_file, log_file)
                        traffic_light_data = analyzer.get_intersection_light_data(int(index))
                        print(f"成功获取路口 {index} 信号灯数据")

                        if 'time_steps' in traffic_light_data:
                            print(f"信号灯数据包含 {len(traffic_light_data['time_steps'])} 个时间步")
                        
                except Exception as e:
                    print(f"获取信号灯数据失败: {str(e)}")
                    traffic_light_data = {"error": f"获取信号灯数据失败: {str(e)}"}
            except Exception as e:
                print(f"获取路口数据失败: {str(e)}")
                # 提供一个最小化的图表结构
                intersection_data = {
                    'title': {'text': ''},
                    'xAxis': {'type': 'category', 'data': []},
                    'yAxis': {'type': 'value'},
                    'series': []
                }
        
        # 构建响应
        response_data = {
            'code': 200,
            'message': 'success',
            'data': {
                'training_metrics': training_metrics if index is None else None,
                'intersection_data': intersection_data,
                'traffic_light_data': traffic_light_data,
                'improvement_data': improvement_data if 'improvement_data' in locals() and improvement_data else None,
                'all_improvement_data': results if 'results' in locals() and results and len(results) > 0 else [{'congestion_decrease': 0, 'delay_decrease': 0}]
            }
        }
        
        # 打印发送给前端的数据量
        if 'results' in locals() and results:
            print(f"发送给前端 {len(results)} 组改善数据")
        
        return jsonify(response_data)
    except Exception as e:
        print(f"处理地图点击事件失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'处理失败: {str(e)}',
            'data': None
        })

# 验证ECharts数据格式
def verify_echarts_data(data):
    # 检查基本结构
    if not isinstance(data, dict):
        raise ValueError("图表数据必须是字典类型")
    
    # 确保存在必要的字段
    if 'series' not in data:
        data['series'] = []
    
    if len(data['series']) == 0:
        data['series'] = [{
            'name': '示例数据',
            'type': 'line',
            'data': [5, 10, 15, 20, 25, 30]
        }]
    
    # 确保x轴数据存在
    if 'xAxis' not in data:
        data['xAxis'] = {'type': 'category', 'data': [0, 1, 2, 3, 4, 5]}
    elif not isinstance(data['xAxis'], dict):
        data['xAxis'] = {'type': 'category', 'data': [0, 1, 2, 3, 4, 5]}
    elif 'data' not in data['xAxis'] or not data['xAxis']['data']:
        data['xAxis']['data'] = [0, 1, 2, 3, 4, 5]
    
    # 确保y轴定义存在
    if 'yAxis' not in data:
        data['yAxis'] = {'type': 'value'}
    
    # 确保标题存在
    if 'title' not in data:
        data['title'] = {'text': '数据图表'}
    
    # 确保每个系列的数据都不为空
    for series in data['series']:
        if 'data' not in series or not series['data']:
            series['data'] = [0, 0, 0, 0, 0]
        if 'type' not in series:
            series['type'] = 'line'

@app.route('/get_all_charts_data', methods=['GET'])
def get_all_charts_data():
    """获取所有图表数据的API端点，包括训练指标和所有路口数据"""
    try:
        # 获取所有图表数据
        all_data = tmu.get_all_metrics_data()
        print("成功获取所有图表数据")
        
        return wrap_ok_return_value(all_data)
    except Exception as e:
        print(f"获取所有图表数据失败: {str(e)}")
        return wrap_error_return_value(f'获取图表数据失败: {str(e)}')

# 添加全局缓存
_log_cache = {
    "episodes": None,
    "last_modified": 0,
    "log_path": "./data/model_eva.log"
}

@app.route("/api/congestion", methods=["GET"])
def get_congestion():
    """支持按episode索引请求数据"""
    # 确保设置正确的响应头
    response = None
    
    try:
        episode_index = request.args.get("episode", type=int, default=0)
        all_episodes = parse_log()
        total = len(all_episodes)

        if total == 0:
            response_data = {
                "data": [],
                "total": 0,
                "current": 0
            }
        else:
            episode_index = episode_index % total
            response_data = {
                "data": all_episodes[episode_index],
                "total": total,
                "current": episode_index
            }
            
        response = jsonify(response_data)
    except Exception as e:
        print(f"获取拥堵数据异常: {str(e)}")
        # 确保即使发生错误也返回可解析的JSON
        response = jsonify({
            "error": str(e),
            "data": [],
            "total": 0,
            "current": 0
        })
    
    # 添加CORS头
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    return response

def parse_log(log_path=None):
    """
    按episode分组解析日志文件
    返回格式: [[{id,mean_queue}], ...] (每个列表元素为一个episode的16个路口数据)
    使用缓存避免重复解析
    """
    global _log_cache
    
    if log_path is None:
        log_path = _log_cache["log_path"]
    
    # 确保日志文件路径是绝对路径
    if not os.path.isabs(log_path):
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_path)
    
    try:
        # 检查文件是否存在
        if not os.path.exists(log_path):
            print(f"警告: 日志文件不存在 {log_path}")
            # 返回空数据，而不是模拟数据
            return []
        
        # 获取文件最后修改时间
        file_modified_time = os.path.getmtime(log_path)
        
        # 检查缓存是否有效
        if (_log_cache["episodes"] is not None and 
            _log_cache["last_modified"] >= file_modified_time):
            return _log_cache["episodes"]
        
        # 缓存无效，需要重新解析
        print(f"重新解析日志文件: {log_path}")
        
        episodes = []
        current_episode = []
        
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # 检测新episode开始
                if line.startswith("episode:"):
                    if current_episode:  # 保存上一个episode
                        episodes.append(current_episode)
                        current_episode = []
                # 提取路口数据
                elif line.startswith("intersection:"):
                    match = re.search(r"intersection:(\d+).*mean_queue:([\d.]+)", line)
                    if match:
                        id = int(match.group(1))
                        mean_queue = float(match.group(2))
                        current_episode.append({"id": id, "mean_queue": mean_queue})
            # 添加最后一个episode
            if current_episode:
                episodes.append(current_episode)
        
        # 更新缓存
        _log_cache["episodes"] = episodes
        _log_cache["last_modified"] = file_modified_time
        _log_cache["log_path"] = log_path
        
        print(f"成功解析日志文件，共{len(episodes)}个episode，每个包含{len(episodes[0]) if episodes else 0}个路口数据")
        return episodes
    except Exception as e:
        print(f"日志解析失败: {str(e)}")
        # 出错时返回空数据
        return []

# 添加心跳机制，保持连接活跃
@socketio.on('heartbeat')
def handle_heartbeat():
    """处理前端发送的心跳，并回复保持连接活跃"""
    emit('heartbeat_response', {'status': 'alive', 'timestamp': time.time()})

def health_check(sid):
    """定期检查连接状态，发送心跳"""
    try:
        socketio.emit('server_heartbeat', {'status': 'checking', 'timestamp': time.time()}, room=sid)
    except Exception as e:
        print(f"健康检查发送失败: {str(e)}")

if __name__ == "__main__":
    socketio.run(app, host=HOST_NAME, port=PORT, debug=True)

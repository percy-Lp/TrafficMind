import supervision as sv
from ultralytics import YOLO
from ultralytics.yolo.data.dataloaders.stream_loaders import LoadStreams
from ultralytics.yolo.engine.predictor import BasePredictor
from ultralytics.yolo.utils import DEFAULT_CFG, SETTINGS
from ultralytics.yolo.utils.torch_utils import smart_inference_mode
from ultralytics.yolo.utils.files import increment_path
from ultralytics.yolo.cfg import get_cfg
from ultralytics.yolo.utils.checks import check_imshow

from PySide6.QtCore import Signal, QObject

from pathlib import Path
import datetime
import numpy as np
import time
import cv2
import os

from classes.paint_trail import draw_trail

x_axis_time_graph = []
y_axis_count_graph = []
video_id_count = 0


class YoloPredictor(BasePredictor, QObject):
    yolo2main_trail_img = Signal(np.ndarray)  # 轨迹图像信号
    yolo2main_box_img = Signal(np.ndarray)  # 绘制了标签与锚框的图像的信号
    yolo2main_status_msg = Signal(str)  # 检测/暂停/停止/测试完成等信号
    yolo2main_fps = Signal(str)  # fps

    yolo2main_labels = Signal(dict)  # 检测到的目标结果（每个类别的数量）
    yolo2main_progress = Signal(int)  # 进度条
    yolo2main_class_num = Signal(int)  # 当前帧类别数
    yolo2main_target_num = Signal(int)  # 当前帧目标数



    def __init__(self, cfg=DEFAULT_CFG, overrides=None):
        super(YoloPredictor, self).__init__()
        QObject.__init__(self)

        try:
            self.args = get_cfg(cfg, overrides)
        except:
            pass
        project = self.args.project or Path(SETTINGS['runs_dir']) / self.args.task
        name = f'{self.args.mode}'
        self.save_dir = increment_path(Path(project) / name, exist_ok=self.args.exist_ok)
        self.done_warmup = False
        if self.args.show:
            self.args.show = check_imshow(warn=True)

        # GUI args
        self.used_model_name = None  # 使用过的检测模型名称
        self.new_model_name = None  # 新更改的模型

        self.source = ''  # 输入源str
        self.progress_value = 0  # 进度条的值

        self.stop_dtc = False  # 终止bool
        self.continue_dtc = True  # 暂停bool


        # config
        self.iou_thres = 0.45  # iou
        self.conf_thres = 0.25  # conf
        self.speed_thres = 0.01  # delay, ms （缓冲）

        self.save_res = False  # 保存MP4
        self.save_txt = False  # 保存txt
        self.show_labels = True  # 显示图像标签bool


        # 运行时候的参数放这里
        self.start_time = None  # 拿来算FPS的计数变量
        self.count = None
        self.sum_of_count = None
        self.class_num = None
        self.total_frames = None
        self.lock_id = None

        # 设置线条样式
        self.box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=1,
            text_scale=0.5
        )

    # 点击开始检测按钮后的检测事件
    @smart_inference_mode()  # 一个修饰器，用来开启检测模式：如果torch>=1.9.0，则执行torch.inference_mode()，否则执行torch.no_grad()
    def run(self):
        # try:
        LoadStreams.capture = ''

        global video_id_count

        self.yolo2main_status_msg.emit('正在加载模型...')

        # 检查保存路径
        if self.save_txt:
            if not os.path.exists('labels'):
                os.mkdir('labels')
        if self.save_res:
            if not os.path.exists('pred_result'):
                os.mkdir('pred_result')

        self.count = 0  # 拿来参与算FPS的计数变量
        self.start_time = time.time()  # 拿来算FPS的计数变量


        if self.continue_dtc:  # 暂停与继续的切换

            if self.used_model_name != self.new_model_name:
                self.setup_model(self.new_model_name)
                self.used_model_name = self.new_model_name

            self.yolo2main_status_msg.emit('正在加载模型...')
            # 加载模型
            model = YOLO(self.new_model_name)

            # 获取数据源 （不同的类型获取不同的数据源）
            iter_model = iter(
                model.track(source=self.source, show=False, stream=True, iou=self.iou_thres, conf=self.conf_thres))


            # 折线图数据初始化
            global x_axis_time_graph, y_axis_count_graph
            x_axis_time_graph = []
            y_axis_count_graph = []

            self.yolo2main_status_msg.emit('检测中...')

            # 使用OpenCV读取视频——获取进度条
            if 'mp4' in self.source or 'avi' in self.source or 'mkv' in self.source or 'flv' in self.source or 'mov' in self.source:
                cap = cv2.VideoCapture(self.source)
                self.total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                cap.release()

            # 如果保存，则创建写入对象
            img_res, result, height, width = self.recognize_res(iter_model)
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = None  # 视频写出变量
            if self.save_res:
                out = cv2.VideoWriter(f'pred_result/video_result_{video_id_count}.avi', fourcc, 25,
                                      (width, height), True)  # 保存检测视频的路径

            # 开始死循环检测
            while True:
                try:
                    # 暂停与开始
                    if self.continue_dtc:
                        # 调用 recognize_res 方法并传入迭代器
                        img_res, result, height, width = self.recognize_res(iter_model)

                        self.res_address(img_res, result, height, width, model, out)

                    # 终止
                    if self.stop_dtc:
                        if self.save_res:
                            if out:
                                out.release()
                                video_id_count += 1
                        self.source = None
                        self.yolo2main_status_msg.emit('检测终止')
                        LoadStreams.capture = 'release'  # 这里是为了终止使用摄像头检测函数的线程，改了yolo源码
                        break


                # 检测截止（本地文件检测）
                except StopIteration:
                    if self.save_res:
                        out.release()
                        video_id_count += 1
                        print('writing complete')
                    self.yolo2main_status_msg.emit('检测完成')
                    self.yolo2main_progress.emit(1000)
                    cv2.destroyAllWindows()  # 单目标追踪停止！
                    self.source = None

                    break
            try:
                out.release()
            except:
                pass

    # 进行识别——并返回所有结果
    def res_address(self, img_res, result, height, width, model, out):
            # 复制一份
            img_box = np.copy(img_res)  # 右边的图
            img_trail = np.zeros((height, width, 3), dtype='uint8')  # 左边的轨迹

            # 如果没有识别的：
            if result.boxes.id is None:
                # 目标都是0
                self.sum_of_count = 0
                self.class_num = 0
                labels_write = "暂未识别到目标！"
            # 如果有识别的
            else:
                detections = sv.Detections.from_yolov8(result)
                detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)

                class_num_arr = []
                for each in detections.class_id:
                    if each not in class_num_arr:
                        class_num_arr.append(each)

                # id 、位置、目标总数
                self.class_num = len(class_num_arr)  # 类别数
                id = detections.tracker_id  # id
                xyxy = detections.xyxy  # 位置
                self.sum_of_count = len(id)  # 目标总数

                # 轨迹绘制部分 @@@@@@@@@@@@@@@@@@@@@@@@@@@@
                identities = id
                grid_color = (255, 255, 255)
                line_width = 1
                grid_size = 100
                for y in range(0, height, grid_size):
                    cv2.line(img_trail, (0, y), (width, y), grid_color, line_width)
                for x in range(0, width, grid_size):
                    cv2.line(img_trail, (x, 0), (x, height), grid_color, line_width)
                draw_trail(img_trail, xyxy, model.model.names, id, identities)

                # 要画出来的信息
                labels_draw = [
                    f"ID: {tracker_id} " \
                    f"CLASS: {model.model.names[class_id]} " \
                    f"CF: {confidence:0.2f}"
                    for _, _, confidence, class_id, tracker_id in detections
                ]
                '''
                如果Torch装的是cuda版本的话：302行的代码需改成：
                  labels_draw = [
                    f"OBJECT-ID: {tracker_id} CLASS: {model.model.names[class_id]} CF: {confidence:0.2f}"
                    for _,confidence,class_id,tracker_id in detections
                ]
                '''
                # 存储labels里的信息
                labels_write = [
                    f"目标ID: {tracker_id} 目标类别: {model.model.names[class_id]} 置信度: {confidence:0.2f}"
                    for _, _, confidence, class_id, tracker_id in detections
                ]
                '''
                  如果Torch装的是cuda版本的话：314行的代码需改成：
                  labels_write = [
                    f"OBJECT-ID: {tracker_id} CLASS: {model.model.names[class_id]} CF: {confidence:0.2f}"
                    for _,confidence,class_id,tracker_id in detections
                ]
                '''
                # 如果显示标签 （要有才可以画呀！）---否则就是原图
                if (self.show_labels == True) and (self.class_num != 0):
                    img_box = self.box_annotator.annotate(scene=img_res, detections=detections, labels=labels_draw)

            # 存储labels里的信息
            if self.save_txt:
                with open('labels/result.txt', 'a') as f:
                    f.write('当前时刻屏幕信息:' +
                            str(labels_write) +
                            f'检测时间: {datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")}' +
                            f' 路段通过的目标总数: {self.sum_of_count}')
                    f.write('\n')
            # 预测写入本地
            if self.save_res:
                out.write(img_box)




            # 添加 折线图数据
            now = datetime.datetime.now()
            new_time = now.strftime("%Y-%m-%d %H:%M:%S")
            if new_time not in x_axis_time_graph:  # 防止同一秒写入
                x_axis_time_graph.append(new_time)
                y_axis_count_graph.append(self.sum_of_count)


            # 抠锚框里的图  （单目标追踪）
            if self.lock_id is not None:
                self.lock_id = int(self.lock_id)
                self.open_target_tracking(detections=detections, img_res=img_res)

            # 传递信号给主窗口
            self.emit_res(img_trail, img_box)

    # 识别结果处理
    def recognize_res(self, iter_model):
            # 检测 ---然后获取有用的数据
            result = next(iter_model)  # 这里是检测的核心，每次循环都会检测一帧图像,可以自行打印result看看里面有哪些key可以用
            img_res = result.orig_img  # 原图
            height, width, _ = img_res.shape

            return img_res, result, height, width

    # 单目标检测窗口开启
    def open_target_tracking(self, detections, img_res):
        try:
            # 单目标追踪 ！！！！！
            result_cropped = self.single_object_tracking(detections, img_res)
            # print(result_cropped)
            cv2.imshow(f'OBJECT-ID:{self.lock_id}', result_cropped)
            cv2.moveWindow(f'OBJECT-ID:{self.lock_id}', 0, 0)
            # press esc to quit
            if cv2.waitKey(5) & 0xFF == 27:
                self.lock_id = None
                cv2.destroyAllWindows()
        except:
            cv2.destroyAllWindows()
            pass

    # 单目标跟踪
    def single_object_tracking(self, detections, img_box):
        store_xyxy_for_id = {}
        for xyxy, id in zip(detections.xyxy, detections.tracker_id):
            store_xyxy_for_id[id] = xyxy
            mask = np.zeros_like(img_box)
        try:
            if self.lock_id not in detections.tracker_id:
                cv2.destroyAllWindows()
                self.lock_id = None
            x1, y1, x2, y2 = int(store_xyxy_for_id[self.lock_id][0]), int(store_xyxy_for_id[self.lock_id][1]), int(
                store_xyxy_for_id[self.lock_id][2]), int(store_xyxy_for_id[self.lock_id][3])
            cv2.rectangle(mask, (x1, y1), (x2, y2), (255, 255, 255), -1)
            result_mask = cv2.bitwise_and(img_box, mask)
            result_cropped = result_mask[y1:y2, x1:x2]
            result_cropped = cv2.resize(result_cropped, (256, 256))
            return result_cropped

        except:
            cv2.destroyAllWindows()
            pass

    # 信号发送区
    def emit_res(self, img_trail, img_box):

        time.sleep(self.speed_thres/1000)  # 缓冲
        # 轨迹图像（左边）
        self.yolo2main_trail_img.emit(img_trail)
        # 标签图（右边）
        self.yolo2main_box_img.emit(img_box)
        # 总类别数量 、 总目标数
        self.yolo2main_class_num.emit(self.class_num)
        self.yolo2main_target_num.emit(self.sum_of_count)
        # 进度条
        self.progress_value = int(self.count / self.total_frames * 1000)
        self.yolo2main_progress.emit(self.progress_value)
        # 计算FPS
        self.count += 1
        if self.count % 3 == 0 and self.count >= 3:  # 计算FPS
            self.yolo2main_fps.emit(str(int(3 / (time.time() - self.start_time))))
            self.start_time = time.time()


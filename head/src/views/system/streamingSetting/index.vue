<template>
  <div class="dashboard-container">
    <!-- 左侧数据统计组件 -->
    <div class="chart-wrapper">
      <div class="content row-layout">
        <!-- 左侧数据统计组件 -->
        <Statistics
          :stats="detectionStats"
          :is-detecting="isVideoProcessing"
          :efficiency-data="efficiencyData"
        />

        <!-- 右侧内容区域 -->
        <div class="right-column">
          <!-- 右侧结果卡片 -->
          <div class="card card-float card-main">
            <div class="card-header">
              <div class="card-title">检测结果</div>
              <div class="card-badge">✨ YOLOv11</div>
            </div>

            <div class="result-container">
              <img :src="after_img_path" class="result-img" ref="imageRef" />
              <div
                class="result-overlay"
                v-if="!imageRef?.src || imageRef?.src === afterImgPath"
              >
                <div class="overlay-content">
                  <div class="overlay-icon">🔍</div>
                  <div class="overlay-text">请选择检测模式并上传内容</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 控制面板区域 -->
          <div class="control-area">
            <!-- 左侧强化学习调控 -->
            <div class="card card-float card-rl">
              <div class="card-header">
                <div class="card-title">强化学习调控</div>
                <div class="card-badge">🤖 RL分析</div>
              </div>
              <div class="rl-wrapper">
                <RLOutput
                  ref="rlOutputRef"
                  @efficiency-data-updated="handleEfficiencyDataUpdate"
                />
              </div>
            </div>

            <!-- 右侧控制面板卡片 -->
            <div class="card card-float card-control">
              <div class="card-header">
                <div class="card-title">控制面板</div>
                <div class="card-badge">🎮 视频控制</div>
              </div>

              <!-- 视频控制按钮 -->
              <div class="control-panel">
                <!-- 上传视频按钮 -->
                <el-button
                  type="primary"
                  plain
                  size="large"
                  :loading="uploading"
                  @click="selectVideo"
                  class="action-btn white-bg-btn"
                >
                  <el-icon class="el-icon--left"><upload-filled /></el-icon>
                  {{ uploading ? "上传中..." : "上传视频" }}
                </el-button>

                <!-- 摄像头按钮 -->
                <el-button
                  type="primary"
                  plain
                  size="large"
                  @click="toggleCamera"
                  class="action-btn white-bg-btn"
                >
                  <el-icon class="el-icon--left"><camera /></el-icon>
                  {{ isCameraActive ? "关闭摄像头" : "开启摄像头" }}
                </el-button>

                <!-- 处理视频按钮 -->
                <el-button
                  :type="isVideoProcessing ? 'danger' : 'success'"
                  plain
                  size="large"
                  @click="toggleVideoProcessing"
                  class="action-btn white-bg-btn"
                >
                  <el-icon class="el-icon--left">
                    <video-play v-if="!isVideoProcessing" />
                    <video-pause v-else />
                  </el-icon>
                  {{ isVideoProcessing ? "暂停检测" : "开始检测" }}
                </el-button>

                <!-- 隐藏的文件输入框 -->
                <input
                  ref="fileInput"
                  type="file"
                  accept="video/mp4,video/avi,video/quicktime,video/x-matroska"
                  style="display: none"
                  @change="handleFileChange"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
const route = useRoute();
import { ElMessage } from "element-plus";
import { ref, onMounted, watch, onUnmounted } from "vue";
import io from "socket.io-client";
import {
  UploadFilled,
  VideoPlay,
  VideoPause,
  Camera,
} from "@element-plus/icons-vue";

import { Label } from "@/model/index";
import Myupload from "./upload.vue";
import Mycamera from "./camera.vue";
import Myvideo from "./video.vue";
import Statistics from "./statistics.vue";
import RLOutput from "@/components/RLOutput/index.vue";


import afterImgPath from "@/assets/images/yolo.png";

const radio1 = ref("3");

// 视频上传相关
const uploading = ref(false);
const videoPath = ref("");
const isVideoProcessing = ref(false);
const fileInput = ref<HTMLInputElement | null>(null);

// 打开文件选择对话框
const selectVideo = () => {
  fileInput.value?.click();
};

// 处理文件选择
const handleFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (!target.files || target.files.length === 0) return;

  const file = target.files[0];

  // 创建FormData对象并上传视频
  const formData = new FormData();
  formData.append("file", file);

  try {
    uploading.value = true;

    // 使用fetch API发送请求
    const response = await fetch("http://127.0.0.1:5500/recognizeVideo", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (result.code === 200) {
      ElMessage.success("视频上传成功");
      videoPath.value = result.data;
    } else {
      ElMessage.error(result.msg || "上传失败");
    }
  } catch (error) {
    ElMessage.error("上传过程中发生错误");
    console.error("上传错误:", error);
  } finally {
    uploading.value = false;
    // 清空文件输入框，允许重复选择同一文件
    if (fileInput.value) fileInput.value.value = "";
  }
};

// 视频和摄像头模式的检测统计数据
const detectionStats = ref({
  total_vehicles: 0,
  lane_types: 0,
  lane_stats: {
    left_turn: 0,
    others: 0,
  },
});

// 添加帧率控制变量
const lastFrameTime = ref(0);
// 目标帧率
const targetFPS = 30;
const frameInterval = 1000 / targetFPS;

// 照相机组件引用
const cameraRef = ref<any>(null);
const isCameraActive = ref(false);
const socket = ref<any>(null);

// 照相机自定义事件处理函数，用于接收子组件传递的信息
const cameraHandleMessage = (info: any) => {
  // 如果info.type=detection
  if (info.type == "detection") {
    // 设置图片路径
    if (imageRef.value) {
      imageRef.value.src = info.data;
    }
    return;
  }

  // 预测图片事件处理
  clickEven(info);
};

// 视频组件引用
const videoRef = ref<any>(null);

// 监听模式切换，当模式改变时重置检测
watch(radio1, (newValue, oldValue) => {
  // 如果切换了模式，重置右侧预览图
  resetPreviewImage();

  // 如果之前是摄像头模式
  if (oldValue === "2") {
    // 尝试调用摄像头组件的停止方法
    if (cameraRef.value && typeof cameraRef.value.stopCamera === "function") {
      cameraRef.value.stopCamera();
    }
  }

  // 如果之前是视频模式
  if (oldValue === "3") {
    // 断开Socket连接
    disconnectSocket();
  }

  // 显示模式切换提示
  ElMessage({
    message: `已切换到${
      newValue === "1" ? "上传图片" : newValue === "2" ? "摄像模式" : "上传视频"
    }模式`,
    type: "info",
    duration: 2000,
  });
});

// 重置预览图像
const resetPreviewImage = (resetImageSrc = true) => {
  if (imageRef.value && resetImageSrc) {
    imageRef.value.src = afterImgPath;
  }

  // 确保overlay显示
  const overlay = document.querySelector(".result-overlay") as HTMLElement;
  if (overlay && resetImageSrc) {
    overlay.style.display = "flex";
  }

  // 重置统计数据
  detectionStats.value = {
    total_vehicles: 0,
    lane_types: 0,
    lane_stats: {
      left_turn: 0,
      others: 0,
    },
  };
};

// 断开Socket连接
const disconnectSocket = () => {
  if (socket.value && isConnected) {
    socket.value.disconnect();
    isConnected = false;
    console.log("Socket连接已断开");
  }
};

let after_img_path: string = afterImgPath;
let labels: any[];

// 后端的图片数据处理
const clickEven = (val: { code: number; data: any; msg: string }) => {
  if (val.data == "照片中没有目标物体哟！") {
    ElMessage({
      message: "照片中没有目标物体哟！",
      type: "warning",
      duration: 5 * 1000,
    });

    // 设置默认统计数据
    detectionStats.value = {
      total_vehicles: 0,
      lane_types: 0,
      lane_stats: {
        left_turn: 0,
        others: 0,
      },
    };
    return;
  }

  if (val.msg == "服务器繁忙，请稍后再试！") {
    ElMessage({
      message: "服务器繁忙，请稍后再试！",
      type: "error",
      duration: 5 * 1000,
    });

    // 设置默认统计数据
    detectionStats.value = {
      total_vehicles: 0,
      lane_types: 0,
      lane_stats: {
        left_turn: 0,
        others: 0,
      },
    };
    return;
  }

  if (val.msg == "执行成功！") {
    ElMessage({
      message: "识别成功！",
      type: "success",
      duration: 5 * 1000,
    });
  }

  // 设置图片路径
  if (imageRef.value) {
    imageRef.value.src = val.data.after_img_path;
  }

  // 将traffic_stats转换为detectionStats格式
  if (val.data.traffic_stats) {
    // 提取总车辆数
    const totalVehicles = val.data.traffic_stats.reduce(
      (sum, lane) => sum + lane.vehicle_count,
      0
    );

    // 创建车道统计数据
    const laneStats = {};
    val.data.traffic_stats.forEach((lane, index) => {
      const laneType = index === 0 ? "left_turn" : "others";
      laneStats[laneType] = lane.vehicle_count;
    });

    // 设置检测统计数据
    detectionStats.value = {
      total_vehicles: totalVehicles,
      lane_types: val.data.traffic_stats.length,
      lane_stats: laneStats,
    };
  } else {
    // 如果没有统计数据，设置默认值
    detectionStats.value = {
      total_vehicles: 0,
      lane_types: 0,
      lane_stats: {
        left_turn: 0,
        others: 0,
      },
    };
  }

  labels = val.data.labels;
};

// 后端的视频数据处理（子组件会发过来的视频地址）
const socketConnect = (videoPath: any) => {
  // 确保之前的连接已关闭
  disconnectSocket();

  socket.value = io("http://127.0.0.1:5500");
  socket.value.on("connect", () => {
    isConnected = true;
    console.log("Socket连接成功");

    // 连接成功后立即发送开始检测信号
    if (isVideoProcessing.value) {
      console.log("Socket连接成功后发送开始检测信号");
      socket.value.emit("start_video_detection", {
        videoPath: videoPath.value,
      });
    }
  });

  // 监听视频帧数据
  socket.value.on("video_frame", (data: any) => {
    // 如果当前不是视频模式或未在检测状态，忽略接收到的帧
    if (radio1.value !== "3" || !isVideoProcessing.value) {
      return;
    }

    // 帧率控制
    const currentTime = performance.now();
    if (currentTime - lastFrameTime.value < frameInterval) {
      return;
    }
    lastFrameTime.value = currentTime;

    // 接收到后端发送的视频帧数据
    if (imageRef.value) {
      // 使用 requestAnimationFrame 优化渲染
      requestAnimationFrame(() => {
        imageRef.value.src = "data:image/jpeg;base64," + data.image;
      });
    }

    // 使用防抖更新统计数据
    if (data.stats) {
      // 只在数据发生变化时更新
      if (JSON.stringify(detectionStats.value) !== JSON.stringify(data.stats)) {
        detectionStats.value = data.stats;
      }
    }
  });

  // 监听预测结果
  socket.value.on("prediction", (data: any) => {
    // 只在数据发生变化时更新
    if (
      data.stats &&
      JSON.stringify(detectionStats.value) !== JSON.stringify(data.stats)
    ) {
      detectionStats.value = data.stats;
    }
  });

  // 监听连接错误事件
  socket.value.on("connect_error", (error: Error) => {
    console.error("Socket连接错误:", error);
    ElMessage({
      message: "连接失败，请稍后再试！",
      type: "error",
      duration: 5 * 1000,
    });

    isVideoProcessing.value = false;
  });
};

// 图片自适应
const imageRef = ref<HTMLImageElement | null>(null);
const resultContainer = ref<HTMLElement | null>(null);

// 添加图片加载优化
const optimizeImageLoad = () => {
  if (imageRef.value) {
    imageRef.value.style.transform = "translateZ(0)";
    imageRef.value.style.willChange = "transform";
  }
};

// 在组件挂载时优化图片加载
onMounted(() => {
  optimizeImageLoad();
});

// 切换摄像头状态
const toggleCamera = () => {
  if (isCameraActive.value) {
    // 关闭摄像头
    closeCamera();
  } else {
    // 打开摄像头
    openCamera();
  }
};

// 打开摄像头
const openCamera = () => {
  // 重置检测状态
  isVideoProcessing.value = false;

  // 只重置统计数据，不重置图像源
  resetPreviewImage(false);

  try {
    // 创建隐藏的video元素用于显示摄像头画面
    if (!cameraVideo.value) {
      cameraVideo.value = document.createElement("video");
      cameraVideo.value.autoplay = true;
      cameraVideo.value.muted = true;
      cameraVideo.value.playsInline = true;
      cameraVideo.value.style.display = "none";
      document.body.appendChild(cameraVideo.value);
    }

    // 访问摄像头
    navigator.mediaDevices
      .getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      })
      .then((stream) => {
        // 保存视频流
        cameraStream.value = stream;

        // 设置视频源
        cameraVideo.value.srcObject = stream;

        // 创建Canvas用于绘制视频帧
        if (!cameraCanvas.value) {
          cameraCanvas.value = document.createElement("canvas");
          cameraCanvas.value.width = 1280;
          cameraCanvas.value.height = 720;
          cameraCanvas.value.style.display = "none";
          document.body.appendChild(cameraCanvas.value);
        }

        // 确保视频开始播放后再进行渲染
        cameraVideo.value.onloadedmetadata = () => {
          cameraVideo.value
            .play()
            .then(() => {
              console.log("摄像头视频已开始播放");
              // 更新UI状态
              isCameraActive.value = true;
              // 立即将视频流显示在结果区域
              renderCameraToResultArea();
              ElMessage.success("摄像头已开启");
            })
            .catch((err) => {
              console.error("视频播放失败:", err);
              ElMessage.error("视频播放失败，请检查浏览器权限");
            });
        };
      })
      .catch((err) => {
        console.error("无法开启摄像头:", err);
        ElMessage.error("无法开启摄像头，请检查权限");
      });
  } catch (error) {
    console.error("摄像头初始化错误:", error);
    ElMessage.error("摄像头初始化失败");
  }
};

// 关闭摄像头
const closeCamera = () => {
  // 停止视频流
  if (cameraStream.value) {
    cameraStream.value.getTracks().forEach((track) => track.stop());
    cameraStream.value = null;
  }

  // 停止帧渲染
  if (cameraFrameInterval.value) {
    clearInterval(cameraFrameInterval.value);
    cameraFrameInterval.value = null;
  }

  // 停止检测
  if (isVideoProcessing.value) {
    stopDetection();
  }

  // 重置UI
  isCameraActive.value = false;

  // 恢复默认图像
  resetPreviewImage(true);

  ElMessage.success("摄像头已关闭");
};

// 将摄像头视频渲染到结果区域
const renderCameraToResultArea = () => {
  // 清除之前的渲染间隔
  if (cameraFrameInterval.value) {
    clearInterval(cameraFrameInterval.value);
  }

  // 立即执行一次渲染，以便立即显示摄像头画面
  if (cameraVideo.value && cameraCanvas.value && imageRef.value) {
    const ctx = cameraCanvas.value.getContext("2d");
    if (ctx) {
      try {
        // 绘制视频帧到Canvas
        ctx.drawImage(
          cameraVideo.value,
          0,
          0,
          cameraCanvas.value.width,
          cameraCanvas.value.height
        );

        // 将Canvas内容转换为图像
        const imgUrl = cameraCanvas.value.toDataURL("image/jpeg");

        // 更新结果区域图像
        imageRef.value.src = imgUrl;

        // 确保overlay不会遮挡摄像头内容
        const overlay = document.querySelector(
          ".result-overlay"
        ) as HTMLElement;
        if (overlay) {
          overlay.style.display = "none";
        }
      } catch (error) {
        console.error("初次渲染摄像头画面失败:", error);
      }
    }
  }

  // 设置新的渲染间隔
  cameraFrameInterval.value = setInterval(() => {
    if (!cameraVideo.value || !cameraCanvas.value || !imageRef.value) return;

    const ctx = cameraCanvas.value.getContext("2d");
    if (!ctx) return;

    try {
      // 绘制视频帧到Canvas
      ctx.drawImage(
        cameraVideo.value,
        0,
        0,
        cameraCanvas.value.width,
        cameraCanvas.value.height
      );

      // 将Canvas内容转换为图像
      const imgUrl = cameraCanvas.value.toDataURL("image/jpeg");

      // 更新结果区域图像
      imageRef.value.src = imgUrl;
    } catch (error) {
      console.error("渲染摄像头画面失败:", error);
    }
  }, 1000 / 30); // 30fps
};

// 实现视频处理逻辑的修改
const toggleVideoProcessing = () => {
  if (isVideoProcessing.value) {
    // 停止检测
    stopDetection();
  } else {
    // 开始检测
    startDetection();
  }
};

// 开始检测
const startDetection = () => {
  // 如果是摄像头模式
  if (isCameraActive.value && cameraVideo.value) {
    // 建立WebSocket连接
    socket.value = io("http://127.0.0.1:5500");

    socket.value.on("connect", () => {
      console.log("已连接到服务器，开始发送摄像头数据");

      // 更新状态
      isVideoProcessing.value = true;

      // 设置发送帧的间隔
      cameraDetectionInterval.value = setInterval(() => {
        if (!cameraCanvas.value || !cameraVideo.value) return;

        const ctx = cameraCanvas.value.getContext("2d");
        if (!ctx) return;

        // 绘制视频帧到Canvas
        ctx.drawImage(
          cameraVideo.value,
          0,
          0,
          cameraCanvas.value.width,
          cameraCanvas.value.height
        );

        // 转换为base64并发送
        const imgData = cameraCanvas.value
          .toDataURL("image/jpeg")
          .split(",")[1];
        socket.value.emit("frame", { imageData: imgData });
      }, 1000 / 8);
    });

    // 处理服务器返回的检测结果
    socket.value.on("prediction", (data) => {
      // 更新检测结果图像
      if (imageRef.value) {
        imageRef.value.src = data.image;
      }

      // 更新统计数据
      if (data.stats) {
        detectionStats.value = data.stats;
      }
    });

    // 处理错误
    socket.value.on("error", (error) => {
      console.error("检测错误:", error);
      ElMessage.error(`检测错误: ${error.message}`);
      stopDetection();
    });

    ElMessage.success("已开始实时检测");
  } else if (videoPath.value) {
    // 如果是视频模式，使用原有逻辑
    isVideoProcessing.value = true;

    // 重置帧时间
    lastFrameTime.value = 0;

    // 确保socket连接并发送开始信号
    let lastUploadedVideoPath = videoPath.value;

    // 如果socket未连接或路径变化，重新连接
    if (!socket.value || lastUploadedVideoPath !== videoPath.value) {
      socketConnect(videoPath);
    }

    // 发送开始检测信号
    if (socket.value) {
      socket.value.emit("start_video_detection", {
        videoPath: videoPath.value,
      });
    }

    // 触发强化学习处理
    if (rlOutputRef.value) {

      rlOutputRef.value.triggerRLProcessing(videoPath.value);
    }

    ElMessage.success("已开始视频检测");
  } else {
    ElMessage.warning("请先开启摄像头或上传视频");
  }
};

// 停止检测
const stopDetection = () => {
  // 关闭WebSocket连接
  if (socket.value) {
    socket.value.close();
    socket.value = null;
  }

  // 清除检测间隔
  if (cameraDetectionInterval.value) {
    clearInterval(cameraDetectionInterval.value);
    cameraDetectionInterval.value = null;
  }

  // 如果是摄像头模式，恢复显示原始摄像头画面
  if (isCameraActive.value) {
    renderCameraToResultArea();
  }

  // 更新状态
  isVideoProcessing.value = false;

  ElMessage.success("已停止检测");
};

// 添加必要的ref变量
const cameraVideo = ref<HTMLVideoElement | null>(null);
const cameraCanvas = ref<HTMLCanvasElement | null>(null);
const cameraStream = ref<MediaStream | null>(null);
const cameraFrameInterval = ref<number | null>(null);
const cameraDetectionInterval = ref<number | null>(null);
const rlOutputRef = ref<any>(null);

// 存储效率数据
const efficiencyData = ref({
  trafficEfficiencyImprovement: 0,
  waitingTimeReduction: 0,
});

// 接收强化学习效率数据
const handleEfficiencyDataUpdate = (data) => {
  console.log("接收到效率数据:", data);
  efficiencyData.value = data;
};

// 组件卸载时清理资源
onUnmounted(() => {
  // 关闭摄像头
  if (isCameraActive.value) {
    closeCamera();
  }

  // 移除创建的DOM元素
  if (cameraVideo.value) {
    document.body.removeChild(cameraVideo.value);
  }

  if (cameraCanvas.value) {
    document.body.removeChild(cameraCanvas.value);
  }
});
</script>

<style scoped>
:deep(html),
:deep(body),
:deep(#app) {
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.dashboard-container {
  width: 100%;
  min-height: 100vh;
  padding: 0;
  margin: 0;
  overflow: hidden;
  position: relative;
  background-color: #f5f7fa;
}

.chart-wrapper {
  width: 100%;
  height: calc(100vh - 0px);
  overflow: hidden;
}

.content {
  width: 100%;
  height: 100%;
  display: flex;
  margin: 0 auto;
  gap: 0;
  padding: 0 20px 0 0;
}

.row-layout {
  flex-direction: row;
  gap: 24px;
  width: 100%;
  height: 100%;
}

/* 右侧内容区域样式 */
.right-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 75%;
  height: 100%;
  padding: 20px 0 20px 0;
  overflow-y: auto;
  box-sizing: border-box;
}

/* 卡片基础样式 */
.card {
  background-color: #fff;
  border-radius: 14px;
  overflow: visible;
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  border: 1px solid #e2e8f0;
  padding: 1rem;
  transition: all 0.3s ease-in-out;
}

.card-float:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(37, 99, 235, 0.1);
  border-color: #3b82f6;
}

.card-main {
  flex: 7;
  display: flex;
  flex-direction: column;
  min-height: 400px;
}

/* 卡片头部样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0.5rem;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid #dbeafe;
  width: 100%;
  z-index: 2;
  background-color: #fff;
  position: relative;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1d4ed8;
}

.card-badge {
  background-color: #dbeafe;
  color: #2563eb;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

/* 结果容器样式 */
.result-container {
  position: relative;
  width: 100%;
  overflow: hidden;
  border-radius: 10px;
  background-color: #f8fafc;
  margin-bottom: 20px;
  flex: 3;
  min-height: 400px;
}

.result-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* 统计数据摘要样式 (恢复) */
.stats-summary {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.stat-box {
  flex: 1;
  background-color: #f1f5f9;
  border-radius: 10px;
  padding: 10px;
  text-align: center;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.85rem;
  color: #64748b;
}

.stat-box.left-turn {
  background-color: #f1f5f9;
}

.stat-box.left-turn .stat-value {
  color: #0f172a;
}

.stat-box.others {
  background-color: #f1f5f9;
}

.stat-box.others .stat-value {
  color: #0f172a;
}

.result-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(241, 245, 249, 0.9);
}

.overlay-content {
  text-align: center;
}

.overlay-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #94a3b8;
}

.overlay-text {
  font-size: 1.1rem;
  color: #64748b;
}

/* 控制面板区域样式 */
.control-area {
  display: flex;
  gap: 20px;
  margin-bottom: 0;
  flex-shrink: 0;
  flex: 3;
  min-height: 200px;
}

/* 强化学习调控卡片样式 */
.card-rl {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
  min-height: 200px;
  overflow: visible;
  position: relative;
}

.rl-wrapper {
  overflow: hidden;
  flex: 1;
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  height: calc(100% - 50px);
}

/* 控制面板卡片样式 */
.card-control {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
  min-height: 200px;
  position: relative;
  padding-bottom: 1rem;
  overflow: visible;
}

.control-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-around;
  gap: 8px;
  padding: 8px 0;
  width: 100%;
  margin-top: 0;
  flex: 1;
  position: relative;
  z-index: 1;
}

.video-status {
  background-color: #f1f5f9;
  border-radius: 10px;
  padding: 15px;
  width: 100%;
  text-align: center;
  border: 1px solid #e2e8f0;
  margin-top: 10px;
  transition: all 0.3s ease;
}

.video-status:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.status-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.status-text {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.action-btn {
  width: 85%;
  height: 38px;
  font-size: 0.95rem;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  margin: 4px auto;
  position: relative;
  z-index: 2;
}

.action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 白底按钮样式 */
.white-bg-btn {
  background-color: white !important;
  border-width: 1px !important;
}

.white-bg-btn:hover {
  background-color: #f9fafb !important;
}

.white-bg-btn.el-button--primary {
  color: #3b82f6 !important;
  border-color: #3b82f6 !important;
}

.white-bg-btn.el-button--success {
  color: #3b82f6 !important;
  border-color: #3b82f6 !important;
}

.white-bg-btn.el-button--danger {
  color: #ef4444 !important;
  border-color: #ef4444 !important;
}

.white-bg-btn.el-button--warning {
  color: #3b82f6 !important;
  border-color: #3b82f6 !important;
}

/* 媒体查询 */
@media (max-width: 1200px) {
  .content {
    flex-direction: column;
  }

  .right-column {
    width: 100%;
    padding: 15px;
  }

  .card-main,
  .control-area {
    flex: none;
  }

  .card-main {
    min-height: 350px;
  }

  .control-area {
    min-height: 220px;
  }

  .result-container {
    min-height: 350px;
  }

  .card-rl,
  .card-control {
    min-height: 220px;
  }
}

@media (max-width: 768px) {
  .video-control-container {
    flex-direction: column;
    gap: 1rem;
  }

  .control-panel {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
  }

  .chart-wrapper {
    height: auto;
    min-height: 100vh;
  }

  .row-layout {
    gap: 15px;
  }
}

.stats-item {
  background-color: #f8fafc;
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid #e2e8f0;
  flex: 1;
  margin: 0 6px;
}

.stats-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border-color: #3b82f6;
}

.stats-item.left-turn {
  background-color: #f8fafc;
}

.stats-item.others {
  background-color: #f8fafc;
}

/* 大屏幕字体放大 */
@media (min-width: 1800px) {
  .card-title {
    font-size: 1.4rem;
  }

  .card-badge {
    font-size: 0.95rem;
    padding: 0.3rem 0.85rem;
  }

  .overlay-icon {
    font-size: 3.5rem;
  }

  .overlay-text {
    font-size: 1.3rem;
  }

  .status-icon {
    font-size: 28px;
  }

  .status-text {
    font-size: 16px;
  }

  .action-btn {
    height: 44px;
    font-size: 1.1rem;
  }
}

/* 超大屏幕进放大 */
@media (min-width: 2400px) {
  .card-title {
    font-size: 1.7rem;
  }

  .card-badge {
    font-size: 1.1rem;
    padding: 0.4rem 1rem;
  }

  .overlay-icon {
    font-size: 4rem;
  }

  .overlay-text {
    font-size: 1.5rem;
  }

  .status-icon {
    font-size: 32px;
  }

  .status-text {
    font-size: 18px;
  }

  .action-btn {
    height: 50px;
    font-size: 1.25rem;
  }
}
</style>

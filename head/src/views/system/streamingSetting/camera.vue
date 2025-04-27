<template>
  <div class="camera-container">
    <!-- 拍照 -->
    <div class="camera-card">
      <div class="camera-video-wrapper">
        <!-- 摄像头调用 -->
        <video
          ref="videoCamera"
          class="camera-feed"
          :width="videoWidth"
          :height="videoHeight"
          autoplay
        ></video>

        <!-- 用绘制canvas-转换给img -->
        <canvas
          style="display: none"
          ref="canvasCamera"
          :width="videoWidth"
          :height="videoHeight"
        ></canvas>
      </div>
    </div>

    <!-- 3个按钮 -->
    <div class="camera-controls">
      <el-button @click="getCompetence()" type="primary" class="btn_photo"
        >开启</el-button
      >
      <el-button @click="stopNavigator()" type="danger" class="btn_photo"
        >关闭</el-button
      >
      <el-button @click="setImage()" type="success" class="btn_photo"
        >拍照</el-button
      >
      <el-button @click="cameraDetection()" type="warning" class="btn_photo"
        >实时</el-button
      >
      <el-button @click="stopCameraDetection()" type="danger" class="btn_photo"
        >终止</el-button
      >
    </div>

    <!-- 拍照结果 -->
    <div v-if="imgSrc" class="preview-container">
      <div class="preview-title">拍摄预览</div>
      <img :src="imgSrc" alt class="preview-image" />
    </div>

    <!-- 上传按钮 -->
    <div v-if="imgSrc" class="preview-controls">
      <el-button type="danger" class="btn_photo" @click="cancelPreview"
        >取消</el-button
      >
      <el-button type="warning" class="btn_photo">分享</el-button>
      <el-button
        type="success"
        @click="sendPhotoToServer(this.imgSrc)"
        class="btn_photo"
        >上传</el-button
      >
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from "vue";
import axios from "axios"; // 导入axios
import { io } from "socket.io-client";

export default defineComponent({
  data() {
    return {
      videoWidth: 500,
      videoHeight: 300,
      imgSrc: "",
      thisCanvas: null as HTMLCanvasElement | null,
      thisContext: null as CanvasRenderingContext2D | null,
      thisVideo: null as HTMLVideoElement | null,
      openVideo: false,
      info: "",

      socket: null,
      intervalId: null,
    };
  },
  mounted() {
    this.getCompetence();

    this.updateVideoSize();

    // 监听窗口大小变化，动态更新 videoWidth 和 videoHeight
    window.addEventListener("resize", this.updateVideoSize);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.updateVideoSize);
  },
  methods: {
    // 实时预测
    cameraDetection() {
      console.log("开始实时预测");
      // 建立 WebSocket 连接
      this.socket = io("http://127.0.0.1:5500");

      this.socket.on("connect", () => {
        console.log("已连接到服务器");

        // 从视频流中获取帧数据
        const video = this.$refs.videoCamera as HTMLVideoElement;
        const canvas = this.$refs.canvasCamera as HTMLCanvasElement;
        const context = canvas.getContext("2d");
        if (!context) {
          console.error("无法获取画布上下文");
          return;
        }

        // 设置一个定时器，不断获取视频帧并发送到服务器
        this.intervalId = setInterval(() => {
          context.drawImage(video, 0, 0, canvas.width, canvas.height);
          const imageData = canvas.toDataURL("image/jpeg");
          // 提取 base64 编码部分
          const base64Data = imageData.split(",")[1];
          // 发送帧数据到服务器
          this.socket.emit("frame", { imageData: base64Data });
          console.log("发送帧数据到服务器");
        }, 1000 / 8); // 每秒发送 8 帧
      });

      this.socket.on("prediction", (data) => {
        // console.log('接收到预测结果:', data);
        // 把 data 传给父组件
        this.$emit("cameraMessage", { data: data.image, type: "detection" });
      });

      this.socket.on("disconnect", () => {
        console.log("与服务器断开连接");
      });
    },
    stopCameraDetection() {
      if (this.socket) {
        this.socket.close();
        this.socket = null;
      }
      if (this.intervalId) {
        clearInterval(this.intervalId);
        this.intervalId = null;
      }
    },

    // 更新video大小
    updateVideoSize() {
      const screenWidth = window.innerWidth;
      if (screenWidth < 600) {
        this.videoWidth = 300;
        this.videoHeight = 200;
        return;
      }
      this.videoWidth = 500;
      this.videoHeight = 300;
      console.log(this.videoWidth);
    },

    // 上传照片
    sendPhotoToServer(photoData: string) {
      // 后端接口地址
      const url = "http://127.0.0.1:5500/photo";
      console.log(photoData);

      // 构造请求参数
      const params = new FormData();
      params.append("photo", photoData);

      // 使用 axios 发送 POST 请求
      axios
        .post(url, params)
        .then((response) => {
          console.log("照片上传成功:", response);
          this.info = response;
          // 处理后端返回的响应
          this.$emit("cameraMessage", response.data);
        })
        .catch((error) => {
          // 处理后端返回的响应
          this.$emit("cameraMessage", response.data);
          console.error("照片上传失败", error);
        });
    },

    // 调用权限（打开摄像头功能）
    getCompetence() {
      const thisCanvas = this.$refs.canvasCamera as HTMLCanvasElement;
      const thisContext = thisCanvas.getContext("2d");
      const thisVideo = this.$refs.videoCamera as HTMLVideoElement;
      this.thisCanvas = thisCanvas;
      this.thisContext = thisContext;
      this.thisVideo = thisVideo;
      this.thisVideo.style.display = "block";
      // 获取媒体属性，旧版本浏览器可能不支持 mediaDevices，我们首先设置一个空对象
      if (navigator.mediaDevices === undefined) {
        navigator.mediaDevices = {} as any;
      }
      // 一些浏览器实现了部分 mediaDevices，我们不能只分配一个对象
      // 使用 getUserMedia，因为它会覆盖现有的属性。
      // 这里，如果缺少 getUserMedia 属性，就添加它。
      if (navigator.mediaDevices.getUserMedia === undefined) {
        navigator.mediaDevices.getUserMedia = function (
          constraints: MediaStreamConstraints
        ) {
          // 首先获取现存的 getUserMedia（如果存在）
          const getUserMedia =
            navigator.webkitGetUserMedia ||
            navigator.mozGetUserMedia ||
            navigator.getUserMedia;
          // 有些浏览器不支持，会返回错误信息
          // 保持接口一致
          if (!getUserMedia) {
            // 不存在则报错
            return Promise.reject(
              new Error("getUserMedia is not implemented in this browser")
            );
          }
          // 否则，使用 Promise 将调用包装到旧的 navigator.getUserMedia
          return new Promise(function (resolve, reject) {
            getUserMedia.call(navigator, constraints, resolve, reject);
          });
        };
      }
      const constraints: MediaStreamConstraints = {
        audio: false,
        video: {
          width: this.videoWidth,
          height: this.videoHeight,
          // transform: "scaleX(-1)",
        },
      };
      navigator.mediaDevices
        .getUserMedia(constraints)
        .then((stream) => {
          // 旧的浏览器可能没有 srcObject
          if ("srcObject" in this.thisVideo!) {
            (this.thisVideo! as any).srcObject = stream;
          } else {
            // 避免在新的浏览器中使用它，因为它正在被弃用。
            (this.thisVideo! as any).src = window.URL.createObjectURL(stream);
          }
          this.thisVideo!.onloadedmetadata = function (e) {
            (this! as any).play();
          };
        })
        .catch((err) => {
          console.log(err);
        });
    },
    // 绘制图片（拍照功能）
    setImage() {
      // canvas 画图
      this.thisContext!.drawImage(
        this.thisVideo!,
        0,
        0,
        this.videoWidth,
        this.videoHeight
      );
      // 获取图片 base64 链接
      const image = this.thisCanvas!.toDataURL("image/png");
      this.imgSrc = image; // 赋值并预览图片
    },
    // 关闭摄像头
    stopNavigator() {
      (this.thisVideo!.srcObject as MediaStream).getTracks()[0].stop();
    },
    // 取消预览图片
    cancelPreview() {
      // 清空图片，隐藏预览区域
      this.imgSrc = "";

      // 检查摄像头状态，如果已关闭则重新启动
      if (this.thisVideo && this.thisVideo.srcObject) {
        const stream = this.thisVideo.srcObject as MediaStream;
        const tracks = stream.getTracks();

        // 如果没有活跃的视频轨道或轨道已结束，重新启动摄像头
        if (tracks.length === 0 || tracks[0].readyState === "ended") {
          this.getCompetence();
        }
      } else {
        // 如果摄像头对象不存在或没有视频流，重新启动摄像头
        this.getCompetence();
      }
    },
  },
});
</script>

<style scoped>
.camera-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  gap: 10px;
}

.camera-card {
  width: 100%;
  position: relative;
}

.camera-video-wrapper {
  width: 100%;
  aspect-ratio: 16/9;
  position: relative;
  background-color: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.camera-feed {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.camera-controls {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 15px;
  flex-wrap: wrap;
}

.btn_photo {
  font-size: 14px;
  padding: 8px 16px;
}

.preview-container {
  width: 100%;
  margin-top: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.preview-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #333;
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.preview-controls {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  justify-content: center;
}

/* 大屏幕字体放大 */
@media (min-width: 1800px) {
  .btn_photo {
    font-size: 16px;
    padding: 10px 20px;
  }

  .preview-title {
    font-size: 18px;
  }
}

/* 超大屏幕进放大 */
@media (min-width: 2400px) {
  .btn_photo {
    font-size: 18px;
    padding: 12px 24px;
  }

  .preview-title {
    font-size: 20px;
  }
}
</style>

<template>
  <div class="rl-output-container">
    <div class="rl-header">
      <!-- 删除标题和按钮 -->
    </div>
    <div class="rl-content" ref="outputContent">
      <div
        v-if="rlResults.length === 0 && !processing && !error"
        class="rl-empty"
      >
        <!-- 移除提示信息 -->
      </div>
      <div v-else-if="error" class="rl-error">
        <el-alert :title="error" type="error" :closable="false" show-icon />
        <el-button
          v-if="error.includes('没有可用的视频文件')"
          type="primary"
          size="small"
          class="retry-btn"
          @click="goToVideoUpload"
        >
          去上传视频
        </el-button>
        <el-button
          v-else
          type="primary"
          size="small"
          class="retry-btn"
          @click="retryConnection"
        >
          重试连接
        </el-button>
      </div>
      <div v-else-if="processingStatus" class="rl-status">
        <el-alert
          :title="processingStatus.message"
          :type="getAlertType(processingStatus.status)"
          :closable="false"
          show-icon
        />
      </div>
      <div v-else class="rl-messages">
        <div
          v-for="(message, index) in rlResults"
          :key="index"
          class="rl-message"
          :class="{
            'rl-decision': message.includes('[RL决策]'),
            'rl-update': message.includes('[RL更新]'),
            'rl-assessment': message.includes('[RL状态评估]'),
            'rl-action': message.includes('[RL动作]'),
          }"
        >
          {{ message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { io } from "socket.io-client";

export default {
  name: "RLOutput",
  data() {
    return {
      rlResults: [],
      processing: false,
      loading: false,
      socket: null,
      error: null,
      connectionAttempts: 0,
      maxConnectionAttempts: 3,
      processingStatus: null,
      efficiencyData: {
        trafficEfficiencyImprovement: 0,
        waitingTimeReduction: 0,
      },
      videoPath: null,
      heartbeatErrorCount: 0,
      heartbeatInterval: null,
    };
  },
  methods: {
    startRLProcessing() {
      if (this.processing) {
        return; // 如果已经在处理中，则不重复触发
      }

      this.error = null;
      this.processingStatus = {
        status: "info",
        message: "正在启动强化学习处理...",
      };
      this.loading = true;

      try {
        // 确保Socket连接已经建立
        if (!this.socket || !this.socket.connected) {
          this.connectSocket();
        }

        if (this.socket && this.socket.connected) {
          // 从父组件获取视频路径，如果有的话
          let videoPath =
            this.videoPath || (this.$parent && this.$parent.videoPath);

          // 直接通过Socket.IO触发强化学习处理，并发送视频路径
          console.log("通过Socket.IO触发RL处理，视频路径:", videoPath);
          this.socket.emit("start_rl_processing", { videoPath: videoPath });
          this.processing = true;
        } else {
          // 如果Socket.IO连接失败，尝试使用HTTP API
          console.log("Socket.IO连接不可用，尝试HTTP API");
          this.startRLProcessingViaHTTP();
        }
      } catch (error) {
        console.error("启动强化学习处理失败:", error);
        this.error = "启动处理失败，请稍后重试";
        this.processingStatus = null;
      } finally {
        this.loading = false;
      }
    },

    async startRLProcessingViaHTTP() {
      try {
        // 从父组件获取视频路径
        let videoPath =
          this.videoPath || (this.$parent && this.$parent.videoPath);

        const response = await axios.post("/rl_process_video", {
          video_path: videoPath,
        });
        if (response.data.code === 200) {
          this.processing = true;
          this.processingStatus = {
            status: "success",
            message: "强化学习处理已在后台启动（HTTP模式）",
          };
          this.$message.info("已启动强化学习处理（HTTP模式）");
        } else {
          this.error = response.data.msg || "启动失败";
          this.processingStatus = null;
          this.$message.error(this.error);
        }
      } catch (error) {
        console.error("HTTP API调用失败:", error);
        this.error = "服务器连接失败，请检查网络并刷新页面";
        this.processingStatus = null;
        this.$message.error(this.error);
      }
    },

    connectSocket() {
      if (this.socket && this.socket.connected) return; // 如果已经连接，则不重复连接

      // 如果已经超过最大连接尝试次数，不再尝试
      if (this.connectionAttempts >= this.maxConnectionAttempts) {
        console.error(`已达到最大连接尝试次数(${this.maxConnectionAttempts})`);
        this.error = "Socket连接失败，请刷新页面重试";
        this.processingStatus = null;
        return;
      }

      this.connectionAttempts++;

      // 先断开旧连接
      if (this.socket) {
        this.socket.disconnect();
        this.socket = null;
      }

      // 创建Socket.IO连接，使用确切的服务器地址
      const serverUrl = "http://127.0.0.1:5500"; // 服务器URL，与后端一致
      console.log(
        `尝试连接Socket.IO (${this.connectionAttempts}/${this.maxConnectionAttempts}):`,
        serverUrl
      );

      this.socket = io(serverUrl, {
        transports: ["websocket", "polling"], // 添加polling作为备选
        reconnectionAttempts: 10, // 增加重连次数
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000, // 添加最大重连延迟
        timeout: 30000, // 增加超时时间到30秒
        forceNew: true, // 强制创建新连接
        autoConnect: true, // 自动连接
      });

      // 连接成功事件
      this.socket.on("connect", () => {
        console.log("Socket连接成功", this.socket.id);
        this.error = null;
        this.connectionAttempts = 0; // 重置连接尝试次数
        this.startHeartbeat(); // 开始心跳检测
      });

      // 监听处理状态
      this.socket.on("rl_processing_status", (data) => {
        console.log("RL处理状态:", data);
        this.processingStatus = data;

        if (data.status === "error") {
          this.error = data.message;
          this.processing = false;
          this.$message.error(data.message);
        } else if (data.status === "processing") {
          this.processing = true;
          this.error = null;
          this.$message.info(data.message);
        } else if (data.status === "started") {
          this.processing = true;
          this.error = null;
          this.$message.success(data.message);
        }
      });

      // 监听RL输出消息
      this.socket.on("rl_output", (data) => {
        console.log("收到RL输出");
        if (data.message) {
          this.rlResults.push(data.message);
          this.processingStatus = null; // 收到输出后隐藏状态提示

          // 滚动到底部显示最新消息
          this.$nextTick(() => {
            if (this.$refs.outputContent) {
              this.$refs.outputContent.scrollTop =
                this.$refs.outputContent.scrollHeight;
            }
          });
        }
      });

      // 监听效率数据（保留逻辑，但不在UI中显示）
      this.socket.on("rl_efficiency_data", (data) => {
        console.log("收到效率数据:", data);
        if (data.traffic_efficiency_improvement !== undefined) {
          this.efficiencyData.trafficEfficiencyImprovement =
            data.traffic_efficiency_improvement;
        }
        if (data.waiting_time_reduction !== undefined) {
          this.efficiencyData.waitingTimeReduction =
            data.waiting_time_reduction;
        }
        // 触发父组件事件，传递效率数据
        this.$emit("efficiency-data-updated", this.efficiencyData);
      });

      // 监听处理完成事件
      this.socket.on("rl_complete", (data) => {
        console.log("RL处理完成:", data);
        this.processing = false;
        this.processingStatus = {
          status: "success",
          message: data.message || "强化学习分析完成",
        };
        this.$message.success(data.message || "强化学习分析完成");
      });

      // 服务器心跳响应
      this.socket.on("heartbeat_response", (data) => {
        console.log("收到服务器心跳响应:", data);
        // 心跳成功，重置错误计数
        this.heartbeatErrorCount = 0;
      });

      // 服务器主动发送心跳
      this.socket.on("server_heartbeat", (data) => {
        console.log("收到服务器主动心跳:", data);
        // 回复心跳
        this.socket.emit("heartbeat");
      });

      // 连接错误处理
      this.socket.on("connect_error", (error) => {
        console.error(
          `Socket连接错误 (${this.connectionAttempts}/${this.maxConnectionAttempts}):`,
          error
        );
        if (this.connectionAttempts >= this.maxConnectionAttempts) {
          this.error = "无法连接到服务器，请检查网络并刷新页面";
          this.processingStatus = null;
        }
      });

      // 添加断开连接处理
      this.socket.on("disconnect", (reason) => {
        console.warn(`Socket连接断开: ${reason}`);

        // 如果不是客户端主动关闭，尝试重连
        if (reason !== "io client disconnect") {
          console.log("尝试自动重连...");
          setTimeout(() => {
            if (!this.socket.connected) {
              this.connectSocket();
            }
          }, 2000);
        }
      });

      // 添加重连成功处理
      this.socket.on("reconnect", (attemptNumber) => {
        console.log(`Socket重连成功，尝试次数: ${attemptNumber}`);
        this.error = null;

        // 如果正在处理中，尝试恢复状态
        if (this.processing) {
          this.checkRLStatus();
        }
      });
    },

    // 启动心跳机制
    startHeartbeat() {
      if (this.heartbeatInterval) {
        clearInterval(this.heartbeatInterval);
      }

      this.heartbeatErrorCount = 0;

      // 每10秒发送一次心跳
      this.heartbeatInterval = setInterval(() => {
        if (this.socket && this.socket.connected) {
          console.log("发送心跳...");
          this.socket.emit("heartbeat");

          // 心跳错误处理 - 如果连续3次心跳失败，尝试重连
          setTimeout(() => {
            this.heartbeatErrorCount++;
            if (this.heartbeatErrorCount >= 3) {
              console.warn("心跳检测失败，尝试重新连接");
              this.retryConnection();
              this.heartbeatErrorCount = 0;
            }
          }, 3000); // 3秒内没有响应视为失败
        }
      }, 10000); // 10秒发送一次
    },

    // 停止心跳
    stopHeartbeat() {
      if (this.heartbeatInterval) {
        clearInterval(this.heartbeatInterval);
        this.heartbeatInterval = null;
      }
    },

    // 对外暴露的处理函数，由父组件调用
    triggerRLProcessing(videoPath) {
      // 如果传入了视频路径，更新组件内部变量
      if (videoPath) {
        this.videoPath = videoPath;
      }
      // 调用内部处理方法
      this.startRLProcessing();
    },

    // 检查RL处理状态
    async checkRLStatus() {
      try {
        const response = await axios.get("/rl_status");
        if (response.data.code === 200) {
          this.processing = response.data.data.processing;
          if (this.processing) {
            console.log("检测到RL处理正在进行中");
            this.processingStatus = {
              status: "info",
              message: "强化学习处理正在进行中...",
            };
          }
        }
      } catch (error) {
        console.warn("获取强化学习状态失败:", error);
        // 忽略错误，不影响用户体验
      }
    },

    // 重试连接
    retryConnection() {
      this.connectionAttempts = 0;
      this.error = null;
      this.processingStatus = {
        status: "info",
        message: "正在尝试重新连接...",
      };
      this.connectSocket();
    },

    // 跳转到视频上传页面
    goToVideoUpload() {
      // 这里应该根据你的应用实际情况进行路由跳转
      // 例如: this.$router.push('/video-upload')
      // 或者触发父组件提供的回调函数
      this.$emit("go-to-video-upload");
      this.$message.info("请上传视频文件后再尝试分析");
    },

    // 获取Alert组件的类型
    getAlertType(status) {
      const typeMap = {
        error: "error",
        warning: "warning",
        info: "info",
        success: "success",
        processing: "info",
        started: "success",
      };
      return typeMap[status] || "info";
    },
  },
  mounted() {
    // 组件加载时建立Socket连接
    this.connectSocket();

    // 检查是否有正在进行的处理
    this.checkRLStatus();
  },
  beforeUnmount() {
    // 组件销毁前断开Socket连接
    this.stopHeartbeat();
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  },
};
</script>

<style scoped>
.rl-output-container {
  display: flex;
  flex-direction: column;
  border: 1px solid #e2e8f0; /* 统一边框颜色 */
  border-radius: 10px; /* 增加圆角半径与其他卡片一致 */
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.05); /* 调整阴影效果与其他卡片一致 */
  height: 100%;
  transition: all 0.3s ease-in-out; /* 添加过渡效果 */
}

.rl-output-container:hover {
  transform: translateY(-2px); /* 添加悬浮效果 */
  box-shadow: 0 12px 20px rgba(0, 0, 0, 0.08);
  border-color: #3b82f6;
}

.rl-header {
  display: none; /* 隐藏头部区域 */
}

.rl-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  background-color: #f8fafc; /* 改为与检测结果框相同的浅蓝色背景 */
  color: #333; /* 深色文本适应浅蓝色背景 */
  font-family: Consolas, Monaco, monospace;
  font-size: 16px; /* 进一步增大默认字体大小 */
  line-height: 1.6; /* 调整行高 */
}

.rl-empty {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #64748b; /* 调整空状态文字颜色，更适合浅蓝色背景 */
}

.rl-tip {
  margin-top: 20px;
  width: 90%;
}

.tip-alert {
  margin-bottom: 10px;
}

.rl-error {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-align: center;
  padding: 0 20px;
  font-size: 15px; /* 调整错误信息的字体大小 */
}

.rl-status {
  margin-bottom: 15px;
  font-size: 15px; /* 调整状态信息的字体大小 */
}

.retry-btn {
  margin-top: 15px;
  font-size: 15px; /* 增大按钮字体 */
  padding: 8px 16px; /* 增大按钮内边距 */
}

.rl-messages {
  display: flex;
  flex-direction: column;
  padding: 5px;
}

.rl-message {
  padding: 8px 12px; /* 进一步增大内边距 */
  margin-bottom: 8px; /* 增大底部外边距 */
  white-space: pre-wrap;
  word-break: break-all;
  border-radius: 8px; /* 增大圆角 */
  background-color: rgba(255, 255, 255, 0.7); /* 添加半透明白色背景 */
  border-left: 4px solid #dcdfe6; /* 加粗左侧边框 */
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); /* 添加轻微阴影 */
}

.rl-decision {
  color: #16a34a;
  border-left-color: #16a34a;
  font-weight: 500; /* 添加轻微加粗 */
}

.rl-update {
  color: #ca8a04;
  border-left-color: #ca8a04;
  font-weight: 500; /* 添加轻微加粗 */
}

.rl-assessment {
  color: #2563eb;
  border-left-color: #2563eb;
  font-weight: 500; /* 添加轻微加粗 */
}

.rl-action {
  color: #dc2626;
  border-left-color: #dc2626;
  font-weight: 500; /* 添加轻微加粗 */
}

/* 大屏幕字体放大 */
@media (min-width: 1800px) {
  .rl-content {
    font-size: 18px; /* 进一步增大大屏幕字体大小 */
    line-height: 1.7;
  }

  .rl-message {
    padding: 6px 8px; /* 增大内边距 */
  }

  .retry-btn {
    font-size: 16px;
  }
}

/* 超大屏幕进一步放大 */
@media (min-width: 2400px) {
  .rl-content {
    font-size: 20px; /* 进一步增大超大屏幕字体大小 */
    line-height: 1.8;
  }

  .rl-message {
    padding: 7px 10px; /* 增大内边距 */
  }

  .retry-btn {
    font-size: 18px;
  }
}
</style>

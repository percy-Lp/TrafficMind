<template>
  <div class="upload-component-container">
    <!-- 上传区域 -->
    <el-upload
      v-model:file-list="fileList"
      action="http://127.0.0.1:5500/recognizeVideo"
      drag
      scoped-slot
      :on-success="handleSuccess"
      :on-error="handleError"
      :on-exceed="handleExceed"
      :auto-upload="false"
      ref="uploadRef"
      :limit="1"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        Drop file here or <em>click to upload</em>
      </div>

      <template #tip>
        <div class="el-upload__tip">支持上传mp4格式视频</div>
      </template>
    </el-upload>

    <!-- 预测按钮 -->
    <div class="button-container">
      <el-popover
        placement="bottom"
        title="提示"
        :width="200"
        trigger="click"
        :visible="uploadVisible"
        :content="uploadContent"
      >
        <template #reference>
          <el-button
            class=""
            :type="loading ? 'info' : 'success'"
            :loading="loading"
            @click="submitUpload"
            style="width: 130px; margin: 10px"
          >
            {{ loading ? "正在上传..." : "上传视频" }}
          </el-button>
        </template>
      </el-popover>

      <el-popover
        placement="bottom"
        title="提示"
        :width="200"
        trigger="click"
        :visible="removeVisible"
        :content="removeContent"
      >
        <template #reference>
          <el-button
            class=""
            type="danger"
            @click="handleRemove"
            style="width: 130px; margin: 10px"
          >
            移除视频
          </el-button>
        </template>
      </el-popover>

      <el-popover title="预测视频">
        <span> 预测结果在右边进行展示 </span>
        <template #reference>
          <el-button
            class=""
            v-show="uploaded"
            :type="videoDetectionButtonType"
            @click="submitVideoDetection"
            style="width: 130px; margin: 10px"
          >
            {{ videoDetectionButtonText }}
          </el-button>
        </template>
      </el-popover>
    </div>
  </div>

  <el-dialog v-model="dialogVisible">
    <img w-full :src="dialogImageUrl" alt="Preview Image" />
  </el-dialog>
</template>

<style scoped>
.upload-component-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.button-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

/* 大屏幕字体放大 */
@media (min-width: 1800px) {
  .el-button {
    font-size: 16px !important;
    padding: 10px 20px !important;
    height: auto !important;
  }
}

/* 超大屏幕进放大 */
@media (min-width: 2400px) {
  .el-button {
    font-size: 18px !important;
    padding: 12px 24px !important;
    height: auto !important;
  }
}
</style>

<script lang="ts" setup>
import { Ref, ref } from "vue";
import { Delete, Download, Plus, ZoomIn } from "@element-plus/icons-vue";

import type { UploadInstance, UploadFile, UploadUserFile } from "element-plus";

const fileList = ref<UploadUserFile[]>([]);
const uploadVisible = ref(false);
const removeVisible = ref(false);
const removeContent = ref("");
const uploadContent = ref("");
const loading = ref(false);
const uploaded = ref(false);
const videoPath = ref("");
let timer: ReturnType<typeof setTimeout> | null = null;

const showUploadVisible = (
  visible: Ref<boolean>,
  timer: ReturnType<typeof setTimeout> | null,
  time: number | 1000
) => {
  if (timer) {
    clearTimeout(timer);
    timer = null;
  }
  visible.value = true;
  timer = setTimeout(() => {
    visible.value = false;
    timer = null;
  }, time);
};

// 上传事件
const uploadRef = ref<UploadInstance>();
const submitUpload = () => {
  if (fileList.value.length == 0) {
    uploadContent.value = "您还没有上传视频哟！";
    showUploadVisible(uploadVisible, timer, 1000);
    return;
  }
  console.log("上传！！！");
  uploadRef.value!.submit();
  loading.value = true;
};

const dialogImageUrl = ref("");
const dialogVisible = ref(false);
const disabled = ref(false);
const videoDetectionButtonText = ref("开始预测");
const videoDetectionButtonType = ref("warning");
const is_video_pause = ref(false);
// 预测视频
const submitVideoDetection = () => {
  //传递path给父组件，都会传输视频路径，又父组件判断是暂停，还是继续
  emit("videoChild", videoPath);
  // 如果不是暂停，则修改按钮的文本和类型为暂停， 视频继续
  if (!is_video_pause.value) {
    // 修改按钮的文本和类型
    videoDetectionButtonText.value = "暂停预测";
    videoDetectionButtonType.value = "danger";
    // 暂停
    is_video_pause.value = true;
    console.log("继续！！！");
    return;
  }

  // 如果是暂停，则修改按钮的文本和类型，视频暂停
  if (is_video_pause.value) {
    // 修改按钮的文本和类型
    videoDetectionButtonText.value = "开始预测";
    videoDetectionButtonType.value = "warning";
    is_video_pause.value = false;
    console.log("暂停！！！");
    return;
  }
};

// 移除视频
const handleRemove = (file: UploadFile) => {
  console.log(file);
  const index = fileList.value.indexOf(file);
  if (fileList.value.length == 1) {
    fileList.value.splice(index, 1);
    // 调用
    removeContent.value = "移除成功(*^▽^*)";
    showUploadVisible(removeVisible, timer, 1000);
    return;
  }
  // 调用
  removeContent.value = "您还没有上传视频哟！";
  showUploadVisible(removeVisible, timer, 1000);
};

// 执行超出限制时的逻辑操作
const handleExceed = (files: File[], uploadFiles: UploadUserFile[]) => {
  uploadContent.value = "上传文件数超出限制";
  showUploadVisible(uploadVisible, timer, 1000);
};

import { defineEmits } from "vue";
// 使用defineEmits创建名称，接受一个数组
const emit = defineEmits(["videoChild"]);

const handleSuccess = (response: any, uploadFile: any, uploadFiles: any) => {
  // 在这里获取上传后的返回数据
  console.log("上传结果", response);

  if (response.code == 200) {
    loading.value = false;
    uploaded.value = true;
    uploadContent.value = "上传成功";
    videoPath.value = response.data;

    videoDetectionButtonText.value = "开始预测";
    videoDetectionButtonType.value = "warning";
    showUploadVisible(uploadVisible, timer, 1000);

    // 移除
    fileList.value = [];
    return;
  }
  if (response.code == 500) {
    loading.value = false;
    uploadContent.value = response.msg;
    showUploadVisible(uploadVisible, timer, 1000);
    fileList.value = [];
    return;
  }
};

const handleError = (response: any, uploadFile: any, uploadFiles: any) => {
  // 在这里获取上传失败后的返回数据
  console.log("上传失败", response);

  loading.value = false;

  uploadContent.value = "上传失败";
  showUploadVisible(uploadVisible, timer, 1000);

  // 移除
  fileList.value = [];
};

// 预览图片
const handlePictureCardPreview = (file: UploadFile) => {
  dialogImageUrl.value = file.url!;
  dialogVisible.value = true;
};

// 下载图片
const handleDownload = (file: UploadFile) => {
  console.log(file);
};
</script>

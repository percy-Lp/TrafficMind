<template>
  <div
    class="login-container"
    :style="{ 'background-image': 'url(' + Img_1 + ')' }"
  >
    <div class="login-card">
      <div class="login-header">
        <h3 class="login-title">TrafficMind</h3>
        <div class="login-badge">✨ 智能识别</div>
      </div>

      <el-form
        ref="ruleFormRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            type="text"
            size="large"
            placeholder="请输入账号"
            class="login-input"
          >
            <template #prefix
              ><svg-icon icon-class="user" class="input-icon"></svg-icon
            ></template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            show-password
            size="large"
            placeholder="请输入密码"
            class="login-input"
            @keyup.enter="handleLogin(ruleFormRef)"
          >
            <template #prefix
              ><svg-icon icon-class="password" class="input-icon"></svg-icon
            ></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button
            :loading="loading"
            type="primary"
            @click.prevent="handleLogin(ruleFormRef)"
            class="login-button"
          >
            <span v-if="!loading">登 录</span>
            <span v-else>登 录 中...</span>
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    <!--  底部  -->
    <div class="login-footer">
      <span>Copyright © 2025 刘</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from "element-plus";
import Img_1 from "@/assets/images/my3.jpg";
import router from "@/router";
import useStore from "@/store";
import { FormInstance, FormRules } from "element-plus";
import { reactive, ref } from "vue";
const { user } = useStore();
const ruleFormRef = ref<FormInstance>();
const loading = ref(false);
const loginForm = reactive({
  username: "pan",
  password: "123456",
});
const rules = reactive<FormRules>({
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码不能少于6位", trigger: "blur" },
  ],
});
const handleLogin = async (formEl: FormInstance | undefined) => {
  if (!formEl) return;
  await formEl.validate((valid) => {
    if (valid) {
      loading.value = true;
      user
        .LogIn(loginForm)
        .then((data: any) => {
          // 如果登录成功
          console.log(data);
          if (data.code === 200) {
            ElMessage({
              message: "登录成功",
              type: "success",
              duration: 0.75 * 1000,
              onClose: () => {
                window.location.reload();
              },
            });
            router.replace({ path: "/" });
          }
          loading.value = false;
        })
        .catch(() => {
          loading.value = false;
        });
    } else {
      loading.value = false;
      return false;
    }
  });
};
</script>

<style scoped>
:root {
  --primary-color: #2563eb;
  --primary-dark: #1d4ed8;
  --primary-light: #dbeafe;
  --secondary-color: #0f172a;
  --accent-color: #3b82f6;
  --text-primary: #1e293b;
  --text-secondary: #475569;
  --bg-primary: #f8fafc;
  --bg-secondary: #f1f5f9;
  --bg-card: #ffffff;
  --border-color: #e2e8f0;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.05);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.05);
}

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  background-size: cover;
  background-position: center;
  position: relative;
}

.login-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(15, 23, 42, 0.6);
  z-index: 1;
}

.login-card {
  height: 34vh;
  width: 25vw;
  min-width: 300px;
  min-height: 400px;
  background-color: #ffffff;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
  position: relative;
  z-index: 2;
  transform: translateY(-30px);
  transition: all 0.3s ease;
  padding: 1.5rem;
}

.login-card:hover {
  transform: translateY(-35px);
  box-shadow: 0 25px 30px -5px rgba(0, 0, 0, 0.15),
    0 10px 10px -5px rgba(0, 0, 0, 0.05);
}

.login-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #dbeafe;
  margin-bottom: 1.2rem;
  padding-bottom: 0.8rem;
}

.login-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1d4ed8;
  margin: 0;
}

.login-badge {
  background-color: #dbeafe;
  color: #2563eb;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.login-form {
  margin-top: 0.8rem;
}

.login-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  padding: 0.6rem 0.8rem;
}

.login-input :deep(.el-input__wrapper:focus-within) {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.input-icon {
  font-size: 18px;
  color: #64748b;
}

.login-button {
  width: 100%;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 8px;
  background-color: #2563eb !important;
  border-color: #2563eb !important;
  transition: all 0.3s ease;
  height: 2.8rem;
  margin-top: 0.8rem;
}

.login-button:hover {
  background-color: #1d4ed8 !important;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
  transform: translateY(-2px);
}

.login-footer {
  position: fixed;
  bottom: 1.5rem;
  width: 100%;
  text-align: center;
  font-size: 0.875rem;
  color: #ffffff;
  font-weight: 500;
  letter-spacing: 1px;
  z-index: 2;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* 标准宽度屏幕 */
@media (max-width: 1600px) {
  .login-card {
    width: 30vw;
  }

  .login-title {
    font-size: 1.3rem;
  }

  .login-badge {
    font-size: 0.7rem;
  }

  .input-icon {
    font-size: 16px;
  }

  .login-button {
    height: 2.6rem;
    font-size: 0.95rem;
  }
}

/* 小屏幕 */
@media (max-width: 1200px) {
  .login-card {
    width: 40vw;
    height: 38vh;
  }

  .login-header {
    margin-bottom: 1rem;
    padding-bottom: 0.6rem;
  }

  .login-input :deep(.el-input__wrapper) {
    padding: 0.5rem 0.7rem;
  }
}

/* 更小屏幕 */
@media (max-width: 768px) {
  .login-card {
    width: 85vw;
    height: auto;
    padding: 1.2rem;
  }

  .login-title {
    font-size: 1.2rem;
  }

  .login-badge {
    padding: 0.2rem 0.6rem;
    font-size: 0.65rem;
  }

  .login-footer {
    font-size: 0.8rem;
  }
}

/* 大屏幕字体放大 */
@media (min-width: 1800px) {
  .login-card {
    padding: 2rem;
  }

  .login-title {
    font-size: 1.8rem;
  }

  .login-badge {
    font-size: 0.9rem;
    padding: 0.3rem 0.85rem;
  }

  .login-input :deep(.el-input__wrapper) {
    padding: 0.7rem 1rem;
  }

  .input-icon {
    font-size: 20px;
  }

  .login-button {
    height: 3.2rem;
    font-size: 1.1rem;
    margin-top: 1rem;
  }

  .login-footer {
    font-size: 1rem;
  }
}

/* 超大屏幕进一步放大 */
@media (min-width: 2400px) {
  .login-card {
    padding: 2.5rem;
  }

  .login-title {
    font-size: 2.2rem;
  }

  .login-badge {
    font-size: 1.1rem;
    padding: 0.4rem 1rem;
  }

  .login-input :deep(.el-input__wrapper) {
    padding: 0.9rem 1.2rem;
  }

  .login-input :deep(.el-input__inner) {
    font-size: 1.2rem;
  }

  .input-icon {
    font-size: 24px;
  }

  .login-button {
    height: 3.8rem;
    font-size: 1.3rem;
    margin-top: 1.5rem;
  }

  .login-footer {
    font-size: 1.2rem;
  }
}
</style>

<style>
div#app {
  height: 100%;
}

/* 修改Element Plus组件默认样式 */
.el-form-item__error {
  color: #ef4444 !important;
  font-size: 0.75rem !important;
  font-weight: 500 !important;
  margin-top: 4px !important;
}

.el-message {
  border-radius: 8px !important;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
}

.el-message--success {
  background-color: #ecfdf5 !important;
  border-color: #d1fae5 !important;
}

.el-message__content {
  font-weight: 500 !important;
}
</style>

<template>
  <div class="nav-header-container">
    <!-- 系统标识 -->
    <div class="system-logo">
      <img src="@/assets/car.png" alt="系统Logo" class="logo-image" />
      <div class="system-title">YOLOv11系统</div>
    </div>

    <!-- 导航按钮 -->
    <div class="nav-buttons-wrapper">
      <div class="nav-buttons-container">
        <router-link to="/index" class="nav-button">
          <span class="nav-text">系统首页</span>
        </router-link>
        <div class="nav-button dropdown-container">
          <span class="nav-text">检测模式</span>
          <div class="dropdown-menu">
            <router-link to="/setting" class="dropdown-item"
              >YOLO检测</router-link
            >
            <router-link to="/coil" class="dropdown-item">线圈检测</router-link>
          </div>
        </div>
        <router-link to="/user" class="nav-button">
          <span class="nav-text">用户管理</span>
        </router-link>
      </div>
    </div>

    <!-- 占位空间，与左侧系统标识对称 -->
    <div class="space-placeholder"></div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();
</script>

<style scoped>
/* 导航头部容器 */
.nav-header-container {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  padding: 1rem 2rem;
  margin: 1.5rem 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 1px solid #eaeaea;
  width: 100%;
}

/* 系统标识样式 */
.system-logo {
  display: flex;
  align-items: center;
  justify-self: start;
}

.logo-image {
  width: 40px;
  height: 40px;
  margin-right: 1rem;
}

.system-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
  background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* 占位空间 */
.space-placeholder {
  justify-self: end;
}

/* 按钮包装容器 */
.nav-buttons-wrapper {
  justify-self: center;
}

/* 导航按钮样式 */
.nav-buttons-container {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
}

.nav-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 1.5rem;
  background: transparent;
  border-radius: 12px;
  transition: all 0.3s ease;
  text-decoration: none;
  min-width: 80px;
  position: relative;
}

.nav-button:hover {
  transform: translateY(-5px);
  background-color: #f8f9fa;
}

.nav-button.router-link-active {
  background: transparent;
  color: #2c3e50;
}

.nav-text {
  font-weight: 600;
  color: #2c3e50;
}

.nav-button.router-link-active .nav-text {
  color: #2c3e50;
}

/* 下拉菜单样式 */
.dropdown-container {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0.5rem 0;
  min-width: 120px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(10px);
  transition: all 0.3s ease;
  z-index: 1000;
}

.dropdown-container:hover .dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: block;
  padding: 0.5rem 1rem;
  color: #2c3e50;
  text-decoration: none;
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
  color: #4361ee;
}

@media (max-width: 768px) {
  .nav-header-container {
    display: flex;
    flex-direction: column;
    padding: 1rem;
  }

  .system-logo {
    width: 100%;
    margin-bottom: 1rem;
    justify-content: center;
  }

  .nav-buttons-wrapper {
    width: 100%;
  }

  .space-placeholder {
    display: none;
  }

  .nav-buttons-container {
    width: 100%;
    justify-content: space-around;
  }

  .nav-button {
    flex-direction: row;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
  }

  .nav-text {
    font-size: 0.9rem;
  }

  .dropdown-menu {
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(10px);
  }

  .dropdown-container:hover .dropdown-menu {
    transform: translateX(-50%) translateY(0);
  }
}
</style>

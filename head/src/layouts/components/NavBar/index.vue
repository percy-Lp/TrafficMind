<template>
  <div
    class="navbar"
    :class="{
      'navbar-hidden': isNavbarHidden,
      'navbar-transparent': isHomePage,
    }"
  >
    <!-- 左侧系统信息 -->
    <div class="left-menu">
      <div class="system-info">
        <img src="@/assets/car.png" alt="Logo" class="system-logo" />
        <span class="system-title">TrafficMind</span>
      </div>
    </div>
    <!-- 中间导航按钮 -->
    <div class="center-menu">
      <el-button
        v-for="item in navItems"
        :key="item.path"
        :class="[
          'nav-button',
          {
            active:
              currentPath === item.path ||
              (item.children &&
                item.children.some((child) => child.path === currentPath)),
          },
        ]"
        @click="item.children ? null : handleNavClick(item.path)"
      >
        <div class="dropdown-container" v-if="item.children">
          <div class="nav-button-content">
            {{ item.title }}
            <el-icon class="dropdown-icon"><arrow-down /></el-icon>
          </div>
          <div class="custom-dropdown-menu">
            <div
              v-for="child in item.children"
              :key="child.path"
              class="dropdown-item"
              @click.stop="handleNavClick(child.path)"
            >
              {{ child.title }}
            </div>
          </div>
        </div>
        <span v-else>{{ item.title }}</span>
      </el-button>
    </div>
    <!-- 右侧用户信息 -->
    <div class="right-menu">
      <el-dropdown
        @command="handleCommand"
        class="avatar-container right-menu-item hover-effect"
        trigger="click"
      >
        <!-- 头像 -->
        <div class="avatar-wrapper">
          <img :src="user.avatar" class="user-avatar" />
          <span class="user-name">SQDZWC</span>
          <el-icon class="dropdown-icon">
            <caret-bottom />
          </el-icon>
        </div>
        <!-- 选项 -->
        <template #dropdown>
          <el-dropdown-menu class="custom-dropdown">
            <el-dropdown-item command="setLayout">
              <el-icon class="dropdown-item-icon"><setting /></el-icon>
              <span>布局设置</span>
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon class="dropdown-item-icon"><switch-button /></el-icon>
              <span>退出登录</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>

  <teleport to="body">
    <div
      v-if="activeDropdown"
      class="global-dropdown-menu"
      :style="dropdownPosition"
    >
      <div
        v-for="child in activeDropdown.children"
        :key="child.path"
        class="global-dropdown-item"
        @click="handleDropdownItemClick(child.path)"
      >
        {{ child.title }}
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import useStore from "@/store";
import { messageConfirm } from "@/utils/modal";
import { computed, ref, onMounted, onUnmounted } from "vue";
import { Setting, SwitchButton, ArrowDown } from "@element-plus/icons-vue";
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();
const { app, user } = useStore();

const device = computed(() => app.device);
const currentPath = computed(() => route.path);
const isNavbarHidden = ref(false);
// 判断是否在首页
const isHomePage = computed(() => currentPath.value === "/index");
let lastScrollTop = 0;

// 处理下拉菜单
const activeDropdown = ref(null);
const dropdownPosition = ref({
  top: "0px",
  left: "0px",
});

// 监听滚动事件
const handleScroll = () => {
  const currentScrollTop =
    window.pageYOffset || document.documentElement.scrollTop;

  // 向下滚动并超过50px时，隐藏导航栏
  if (currentScrollTop > lastScrollTop && currentScrollTop > 50) {
    isNavbarHidden.value = true;
  } else {
    // 向上滚动或在顶部时，显示导航栏
    isNavbarHidden.value = false;
  }

  lastScrollTop = currentScrollTop;
};

onMounted(() => {
  window.addEventListener("scroll", handleScroll);
});

onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll);
});

const navItems = [
  { title: "系统首页", path: "/index" },
  {
    title: "检测模式",
    path: "/setting",
    children: [
      { title: "智视单控", path: "/setting" },
      { title: "智网联控", path: "/coil" },
    ],
  },
  { title: "用户管理", path: "/user" },
];

const handleNavClick = (path: string) => {
  router.push(path);
};

const handleCommand = (command: string) => {
  switch (command) {
    case "setLayout":
      setLayout();
      break;
    case "logout":
      logout();
      break;
    default:
      break;
  }
};
const logout = () => {
  messageConfirm("确定退出系统吗？")
    .then(() => {
      user.LogOut().then(() => {
        location.href = "/login";
      });
    })
    .catch(() => {});
};
const emits = defineEmits(["setLayout"]);
const setLayout = () => {
  emits("setLayout");
};
</script>

<style lang="scss" scoped>
.navbar {
  height: 64px;
  overflow: visible;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  background-color: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(5px);
  box-shadow: none;
  transition: all 0.3s ease;
  z-index: 9999999;
  padding: 0 24px;

  &.navbar-transparent {
  }

  &.navbar-hidden {
    transform: translateY(-100%);
  }

  .left-menu {
    display: flex;
    align-items: center;
    width: 25%;
    padding-left: 30px;

    .system-info {
      display: flex;
      align-items: center;
      gap: 12px;

      .system-logo {
        width: 32px;
        height: 32px;
        object-fit: contain;
      }

      .system-title {
        font-size: 24px;
        font-weight: 700;
        color: #fff;
        white-space: nowrap;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      }
    }
  }

  .center-menu {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 50%;
    gap: 16px;
    position: relative;
    z-index: 99999;

    .nav-button {
      padding: 8px 20px;
      font-size: 16px;
      font-weight: 600;
      color: #fff;
      background: transparent;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.3s ease;
      text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      display: flex;
      align-items: center;
      gap: 4px;
      position: relative;
      z-index: 99999;

      &:hover {
        color: #fff;
        background: rgba(255, 255, 255, 0.1);
      }

      &.active {
        color: #fff;
        background: rgba(255, 255, 255, 0.2);
      }

      .dropdown-container {
        position: relative;
        z-index: 99999;

        .nav-button-content {
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .dropdown-icon {
          font-size: 12px;
          transition: transform 0.3s;
        }

        .custom-dropdown-menu {
          position: absolute;
          top: 100%;
          left: 50%;
          transform: translateX(-50%) translateY(10px);
          background: #333333;
          backdrop-filter: blur(15px);
          border-radius: 8px;
          min-width: 180px;
          padding: 10px 0;
          margin-top: 10px;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
          opacity: 0;
          visibility: hidden;
          transition: all 0.3s ease;
          z-index: 99999999;

          &::before {
            content: "";
            position: absolute;
            top: -6px;
            left: 50%;
            transform: translateX(-50%);
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-bottom: 6px solid rgba(0, 0, 0, 0.95);
          }

          .dropdown-item {
            padding: 12px 20px;
            color: #fff;
            text-align: center;
            transition: all 0.2s ease;
            cursor: pointer;
            font-size: 15px;
            letter-spacing: 0.5px;

            &:hover {
              background: rgba(255, 255, 255, 0.2);
            }
          }
        }

        &:hover {
          .dropdown-icon {
            transform: rotate(180deg);
          }

          .custom-dropdown-menu {
            opacity: 1;
            visibility: visible;
            transform: translateX(-50%) translateY(0);
          }
        }
      }
    }
  }

  .right-menu {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    width: 25%;
    height: 100%;

    &:focus {
      outline: none;
    }

    .right-menu-item {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0 12px;
      height: 100%;
      font-size: 18px;
      color: #fff;
      cursor: pointer;
      transition: all 0.3s ease;

      &.hover-effect {
        &:hover {
          background: rgba(255, 255, 255, 0.1);
          color: #fff;
        }
      }
    }

    .avatar-container {
      margin-right: 16px;
      height: 100%;
      padding: 0 16px;

      .avatar-wrapper {
        display: flex;
        align-items: center;
        position: relative;

        .user-avatar {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          object-fit: cover;
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
          border: 2px solid #fff;
          transition: all 0.3s ease;

          &:hover {
            transform: scale(1.05);
            box-shadow: 0 3px 8px rgba(37, 99, 235, 0.2);
          }
        }

        .user-name {
          margin: 0 8px;
          font-size: 16px;
          font-weight: 600;
          color: #fff;
          text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .dropdown-icon {
          font-size: 12px;
          color: #fff;
          transition: all 0.3s ease;
        }

        &:hover .dropdown-icon {
          color: #fff;
          transform: translateY(2px);
        }
      }
    }
  }
}

:deep(.custom-dropdown) {
  min-width: 120px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);

  .el-dropdown-menu__item {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    font-size: 14px;
    line-height: 1.5;
    color: #334155;

    &:hover {
      background-color: rgba(37, 99, 235, 0.06);
      color: #2563eb;
    }

    &.is-disabled {
      color: #94a3b8;
    }

    .dropdown-item-icon {
      margin-right: 8px;
      font-size: 16px;
    }
  }
}

/* 桌面屏幕适配 */
@media screen and (min-width: 1024px) {
  .navbar {
    height: 70px;
    padding: 0 30px;

    .left-menu {
      padding-left: 40px;

      .system-info {
        gap: 14px;

        .system-logo {
          width: 38px;
          height: 38px;
        }

        .system-title {
          font-size: 26px;
        }
      }
    }

    .center-menu {
      gap: 24px;

      .nav-button {
        padding: 10px 28px;
        font-size: 18px;
        border-radius: 8px;

        .dropdown-container {
          .dropdown-icon {
            font-size: 14px;
          }

          .custom-dropdown-menu {
            min-width: 220px;
            padding: 14px 0;
            margin-top: 14px;
            border-radius: 10px;

            .dropdown-item {
              padding: 14px 24px;
              font-size: 17px;
            }
          }
        }
      }
    }

    .right-menu {
      .avatar-container {
        margin-right: 24px;
        padding: 0 20px;

        .avatar-wrapper {
          .user-avatar {
            width: 44px;
            height: 44px;
            border-width: 3px;
          }

          .user-name {
            font-size: 18px;
            margin: 0 12px;
          }

          .dropdown-icon {
            font-size: 14px;
          }
        }
      }
    }
  }

  :deep(.custom-dropdown) {
    min-width: 150px;

    .el-dropdown-menu__item {
      padding: 12px 20px;
      font-size: 16px;

      .dropdown-item-icon {
        font-size: 18px;
        margin-right: 10px;
      }
    }
  }
}

/* 大屏幕适配  */
@media screen and (min-width: 1800px) {
  .navbar {
    height: 80px;
    padding: 0 40px;

    .left-menu {
      padding-left: 50px;

      .system-info {
        gap: 18px;

        .system-logo {
          width: 48px;
          height: 48px;
        }

        .system-title {
          font-size: 30px;
        }
      }
    }

    .center-menu {
      gap: 30px;

      .nav-button {
        padding: 12px 32px;
        font-size: 20px;
        border-radius: 10px;

        .dropdown-container {
          .dropdown-icon {
            font-size: 16px;
          }

          .custom-dropdown-menu {
            min-width: 240px;
            padding: 16px 0;
            margin-top: 16px;

            .dropdown-item {
              padding: 16px 28px;
              font-size: 19px;
            }
          }
        }
      }
    }

    .right-menu {
      .avatar-container {
        margin-right: 30px;
        padding: 0 24px;

        .avatar-wrapper {
          .user-avatar {
            width: 52px;
            height: 52px;
            border-width: 3px;
          }

          .user-name {
            font-size: 20px;
            margin: 0 14px;
          }

          .dropdown-icon {
            font-size: 16px;
          }
        }
      }
    }
  }

  :deep(.custom-dropdown) {
    min-width: 180px;

    .el-dropdown-menu__item {
      padding: 14px 24px;
      font-size: 18px;

      .dropdown-item-icon {
        font-size: 20px;
        margin-right: 12px;
      }
    }
  }
}

/* 超大屏幕适配 */
@media screen and (min-width: 2400px) {
  .navbar {
    height: 100px;
    padding: 0 60px;

    .left-menu {
      padding-left: 60px;

      .system-info {
        gap: 20px;

        .system-logo {
          width: 60px;
          height: 60px;
        }

        .system-title {
          font-size: 36px;
        }
      }
    }

    .center-menu {
      gap: 36px;

      .nav-button {
        padding: 14px 38px;
        font-size: 24px;
        border-radius: 12px;

        .dropdown-container {
          .dropdown-icon {
            font-size: 18px;
          }

          .custom-dropdown-menu {
            min-width: 280px;
            padding: 18px 0;
            margin-top: 18px;

            .dropdown-item {
              padding: 18px 30px;
              font-size: 22px;
            }
          }
        }
      }
    }

    .right-menu {
      .avatar-container {
        margin-right: 36px;
        padding: 0 28px;

        .avatar-wrapper {
          .user-avatar {
            width: 64px;
            height: 64px;
            border-width: 4px;
          }

          .user-name {
            font-size: 24px;
            margin: 0 16px;
          }

          .dropdown-icon {
            font-size: 20px;
          }
        }
      }
    }
  }

  :deep(.custom-dropdown) {
    min-width: 220px;

    .el-dropdown-menu__item {
      padding: 16px 28px;
      font-size: 22px;

      .dropdown-item-icon {
        font-size: 24px;
        margin-right: 14px;
      }
    }
  }
}

/* 小屏幕适配 */
@media screen and (max-width: 1023px) {
  .navbar {
    padding: 0 15px;

    .center-menu {
      width: 60%;
      gap: 10px;

      .nav-button {
        padding: 6px 12px;
        font-size: 14px;
      }
    }

    .left-menu {
      width: 20%;
      padding-left: 5px;

      .system-info {
        .system-title {
          font-size: 20px;
        }

        .system-logo {
          width: 28px;
          height: 28px;
        }
      }
    }

    .right-menu {
      width: 20%;

      .avatar-container {
        margin-right: 5px;
        padding: 0 8px;

        .avatar-wrapper {
          .user-name {
            font-size: 14px;
            margin: 0 5px;
          }

          .user-avatar {
            width: 32px;
            height: 32px;
          }
        }
      }
    }
  }
}

/* 全局下拉菜单样式 */
.global-dropdown-menu {
  position: fixed;
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(15px);
  border-radius: 10px;
  min-width: 180px;
  padding: 10px 0;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.8);
  z-index: 99999999; /* 超高的z-index */
  animation: dropdownFadeIn 0.2s ease;
}

.global-dropdown-item {
  padding: 12px 20px;
  color: #fff;
  text-align: center;
  transition: all 0.2s ease;
  cursor: pointer;
  font-size: 15px;
  letter-spacing: 0.5px;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
}

@keyframes dropdownFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

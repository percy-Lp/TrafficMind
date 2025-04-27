<template>
  <div :class="{ 'has-logo': showLogo }" class="sidebar-container">
    <!-- 网站Logo -->
    <logo v-if="showLogo" :collapse="isCollapse" />
    <!-- 侧边栏 -->
    <el-scrollbar wrap-class="scrollbar-wrapper">
      <el-menu
        :default-active="activeMenu"
        :unique-opened="true"
        :collapse="isCollapse"
        :collapse-transition="false"
        :background-color="variables.menuBg"
        :text-color="variables.menuText"
        :active-text-color="variables.menuActiveText"
        class="sidebar-menu"
      >
        <sidebar-item
          v-for="route in routes"
          :item="route"
          :key="route.path"
          :base-path="route.path"
        />
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import variables from "@/assets/styles/variables.module.scss";
import useStore from "@/store";
import { computed } from "vue";
import { useRoute } from "vue-router";
import Logo from "./Logo.vue";
import SidebarItem from "./SidebarItem.vue";
const { app, setting, permission } = useStore();
const route = useRoute();
const isCollapse = computed(() => app.isCollapse);
const showLogo = computed(() => setting.sidebarLogo);
const activeMenu = computed(() => route.path);

const fakeRoutes = [
  {
    path: "/index",
    meta: { title: "系统首页", icon: "archives" },
  },
  {
    path: "/setting",
    meta: { title: "检测模式", icon: "dashboard" },
  },
  {
    path: "/user",
    meta: { title: "用户管理", icon: "user" },
  },
];

const routes = computed(() => fakeRoutes);
</script>

<style lang="scss" scoped>
.sidebar-container {
  /* 侧边栏容器样式 */
  :deep(.el-menu) {
    border-right: none;
  }

  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    text-align: center !important;
    padding: 18px 0 !important;
    height: auto !important;
    min-height: 70px !important;
    line-height: 1.5 !important;

    /* 折叠状态下的样式 */
    &.is-active {
      background-color: rgba(255, 255, 255, 0.15) !important;
      color: #ffffff !important;
      font-weight: 600;
    }

    .el-icon {
      margin: 0 auto 8px !important;
      font-size: 28px !important;

      :deep(svg) {
        width: 28px !important;
        height: 28px !important;
      }
    }

    .menu-title {
      display: block !important;
      text-align: center !important;
      margin: 0 !important;
      font-size: 1rem !important;
      font-family: "PingFang SC", "Microsoft YaHei", sans-serif !important;
    }
  }

  /* 处理折叠状态下的菜单 */
  :deep(.el-menu--collapse) {
    .el-menu-item,
    .el-sub-menu__title {
      .el-icon {
        margin: 0 !important;
        font-size: 28px !important;
      }
    }
  }
}

.sidebar-menu {
  padding: 16px 0;
}
</style>

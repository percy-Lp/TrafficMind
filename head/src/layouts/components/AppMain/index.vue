<template>
  <section class="app-main" :class="{ 'home-page': isHomePage }">
    <router-view v-slot="{ Component, route }">
      <transition name="fade-transform" mode="out-in">
        <keep-alive>
          <component :is="Component" :key="route.fullPath" />
        </keep-alive>
      </transition>
    </router-view>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const isHomePage = computed(() => route.path === "/index");
</script>

<style lang="scss" scoped>
.app-main {
  min-height: calc(100vh - 64px);
  width: 100%;
  position: relative;
  overflow: hidden;
  padding: 0;
  background-color: #f8fafc;
  transition: all 0.3s ease;
  margin-top: 64px;

  &.home-page {
    min-height: 100vh;
    margin-top: 0;
  }
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  > div {
    flex: 1;
    width: 100%;
  }

  &::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }

  &::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 10px;
  }

  &::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 10px;
  }
}

/* 整应用于不同屏幕尺寸 */
@media screen and (max-width: 1023px) {
  .app-main {
    min-height: calc(100vh - 54px);
    margin-top: 54px;
  }
}

@media screen and (min-width: 1024px) {
  .app-main {
    min-height: calc(100vh - 68px);
    margin-top: 68px;
  }
}

@media screen and (min-width: 1800px) {
  .app-main {
    min-height: calc(100vh - 84px);
    margin-top: 84px;
  }
}

@media screen and (min-width: 2400px) {
  .app-main {
    min-height: calc(100vh - 110px);
    margin-top: 110px;
  }
}

.fixed-header + .app-main {
  padding-top: 0;
}


.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.4s ease;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>

<style lang="scss">

.el-popup-parent--hidden {
  .fixed-header {
    padding-right: 17px;
  }
}

// 全局内容卡片样式
.content-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  padding: 20px;
  margin-bottom: 16px;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  }

  &__title {
    font-size: 18px;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 16px;
    border-bottom: 1px solid #f1f5f9;
    padding-bottom: 12px;
  }
}

// 表格统一样式
.el-table {
  --el-table-border-color: #eff6ff;
  --el-table-header-bg-color: #f8faff;
  --el-table-row-hover-bg-color: #f1f5f9;
  border-radius: 8px;
  overflow: hidden;

  .el-table__header {
    th {
      background-color: #f8faff;
      color: #334155;
      font-weight: 600;
      padding: 12px 0;
    }
  }

  .el-table__row {
    td {
      padding: 12px 0;
    }
  }
}

// 统一按钮样式
.el-button {
  &--primary {
    --el-button-bg-color: #2563eb;
    --el-button-border-color: #2563eb;
    --el-button-hover-bg-color: #1d4ed8;
    --el-button-hover-border-color: #1d4ed8;
    border-radius: 6px;
    font-weight: 500;

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
    }
  }
}
</style>

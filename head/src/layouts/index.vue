<template>
  <div :class="classObj" class="app-wrapper">
    <div
      v-if="device === 'mobile' && !app.isCollapse"
      class="drawer-bg"
      @click="handleClickOutside"
    />
    <div class="main-container">
      <div :class="{ 'fixed-header': fixedHeader }">
        <!-- 导航栏 -->
        <NavBar @setLayout="setLayout"></NavBar>
      </div>
      <AppMain></AppMain>
      <!-- 设置 -->
      <Settings ref="settingRef"></Settings>
    </div>
  </div>
</template>

<script setup lang="ts">
import Settings from "@/components/Settings/index.vue";
import useStore from "@/store";
import { useWindowSize } from "@vueuse/core";
import { computed, ref, watchEffect } from "vue";
import AppMain from "./components/AppMain/index.vue";
import NavBar from "./components/NavBar/index.vue";


const { app, setting } = useStore();
const { width } = useWindowSize();
const WIDTH = 992;
const settingRef = ref();

const device = computed(() => app.device);
const fixedHeader = computed(() => setting.fixedHeader);
const classObj = computed(() => ({
  hideSidebar: app.isCollapse,
  openSidebar: !app.isCollapse,
  mobile: device.value === "mobile",
}));

watchEffect(() => {
  if (width.value - 1 < WIDTH) {
    app.toggleDevice("mobile");
    app.changeCollapse(true);
  } else {
    app.toggleDevice("desktop");
  }
});

const handleClickOutside = () => {
  app.changeCollapse(true);
};

const setLayout = () => {
  settingRef.value.openSetting();
};
</script>

<style lang="scss" scoped>
@import "@/assets/styles/mixin.scss";
@import "@/assets/styles/variables.module.scss";

.app-wrapper {
  @include clearfix;
  position: relative;
  height: 100%;
  width: 100%;

  &.mobile.openSidebar {
    position: fixed;
    top: 0;
  }
}

.drawer-bg {
  background: #000;
  opacity: 0.3;
  width: 100%;
  top: 0;
  height: 100%;
  position: absolute;
  z-index: 999;
}

/* 修改主容器样式，使其占据整个宽度 */
.main-container {
  min-height: 100%;
  transition: margin-left 0.28s;
  margin-left: 0;
  position: relative;
  width: 100%;
}

.fixed-header {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 9999999;
  width: 100%;
  transition: width 0.28s;
}

.hideSidebar .fixed-header {
  width: 100%;
}

.sidebarHide .fixed-header {
  width: 100%;
}

.mobile .fixed-header {
  width: 100%;
}
</style>

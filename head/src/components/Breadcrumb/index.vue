<template>
  <div class="app-breadcrumb">
    <span class="page-title">{{ pageTitle }}</span>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { ref, watch, onMounted } from "vue";

const currentRoute = useRoute();
const pageTitle = ref('');

// 获取当前页面标题的函数
const updatePageTitle = () => {
  // 从当前路由的matched数组中获取最后一个匹配项
  if (currentRoute.matched && currentRoute.matched.length > 0) {
    const currentPage = currentRoute.matched[currentRoute.matched.length - 1];
    pageTitle.value = currentPage.meta.title as string || '未知页面';
  } else {
    pageTitle.value = '首页';
  }
};

// 监听路由变化
watch(() => currentRoute.path, () => {
  updatePageTitle();
});

// 组件挂载时初始化标题
onMounted(() => {
  updatePageTitle();
});
</script>

<style lang="scss" scoped>
.app-breadcrumb {
  display: inline-block;
  line-height: 50px;
  margin-left: 8px;
}

.page-title {
  font-size: 14px;
  color: #97a8be;
  font-weight: 400;
}
</style>

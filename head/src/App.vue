<template>
  <el-config-provider :locale="zhCn">
    <router-view />
  </el-config-provider>
</template>

<script setup lang="ts">
import useStore from "@/store";
import { ElConfigProvider } from "element-plus";
import zhCn from "element-plus/es/locale/lang/zh-cn";
import type { EpPropMergeType } from "element-plus/es/utils/vue/props/types";
import { computed, onMounted } from "vue";

const { app } = useStore();
const size = computed(
  () =>
    app.size as EpPropMergeType<
      StringConstructor,
      "default" | "small" | "large",
      never
    >
);

onMounted(() => {});
</script>

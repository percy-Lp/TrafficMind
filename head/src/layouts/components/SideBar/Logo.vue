<template>
    <div class="sidebar-logo-container" :class="{ collapse: isCollapse }">
        <router-link v-if="collapse" key="collapse" class="sidebar-logo-link" to="/">
            <img v-if="logo" :src="logo" class="sidebar-logo" />
            <h1 v-else class="sidebar-title">yolov11系统</h1>
        </router-link>
        <router-link v-else key="expand" class="sidebar-logo-link" to="/">
            <img v-if="logo" :src="logo" class="sidebar-logo" />
            <h1 class="sidebar-title">yolov11系统</h1>
        </router-link>
    </div>
</template>

<script setup lang="ts">
import { reactive, toRefs } from "vue";

const props = defineProps({
    collapse: {
        type: Boolean,
        required: true,
    },
});

const state = reactive({
    isCollapse: props.collapse,
    logo: new URL(`../../../assets/car.png`, import.meta.url).href,
});

const { logo, isCollapse } = toRefs(state);
</script>

<style lang="scss" scoped>
.sidebar-logo-container {
    position: relative;
    width: 100%;
    height: 64px;
    line-height: 64px;
    text-align: center;
    overflow: hidden;
    transition: all 0.3s ease;
    
    &::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 80%;
        height: 1px;
        background: rgba(255, 255, 255, 0.1);
    }

    & .sidebar-logo-link {
        height: 100%;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        padding: 0 1rem;
        transition: all 0.3s ease;

        &:hover {
            background: rgba(255, 255, 255, 0.05);
        }

        & .sidebar-logo {
            width: 32px;
            height: 32px;
            vertical-align: middle;
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }

        & .sidebar-title {
            display: inline-block;
            margin: 0;
            color: #fff;
            font-weight: 600;
            line-height: 64px;
            font-size: 1.125rem;
            font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
            vertical-align: middle;
            margin-left: 12px;
            letter-spacing: 0.5px;
            opacity: 0.95;
            white-space: nowrap;
            transition: all 0.3s ease;
        }
    }

    &.collapse {
        .sidebar-logo {
            margin-right: 0;
            transform: scale(0.9);
        }
        
        .sidebar-title {
            display: none;
        }
    }
}
</style>

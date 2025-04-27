<template>
    <div v-if="!item.meta || !item.meta.hidden" class="sidebar-item">
        <template v-if="
            hasOneShowingChild(item.children, item) &&
            (!onlyOneChild.children || onlyOneChild.noShowingChildren) &&
            (!item.alwaysShow)
        ">
            <app-link v-if="onlyOneChild.meta" :to="resolvePath(onlyOneChild.path)">
                <el-menu-item :index="resolvePath(onlyOneChild.path)" 
                             :class="{ 'submenu-title-noDropdown': !isNest }"
                             class="menu-item">
                    <el-icon class="menu-icon">
                        <svg-icon v-if="onlyOneChild.meta && onlyOneChild.meta.icon"
                            :icon-class="onlyOneChild.meta.icon" />
                    </el-icon>
                    <template #title>
                        <span class="menu-title">{{ onlyOneChild.meta.title }}</span>
                    </template>
                </el-menu-item>
            </app-link>
        </template>
        <el-sub-menu v-else :index="resolvePath(item.path)" class="sidebar-sub-menu">
            <template #title>
                <el-icon class="menu-icon">
                    <svg-icon v-if="item.meta && item.meta.icon" :icon-class="item.meta.icon" />
                </el-icon>
                <span class="menu-title">{{ item.meta.title }}</span>
            </template>
            <sidebar-item v-for="child in item.children" 
                         :key="child.path" 
                         :item="child" 
                         :is-nest="true"
                         :base-path="resolvePath(child.path)" 
                         class="nest-menu" />
        </el-sub-menu>
    </div>
</template>

<script setup lang="ts">
import SvgIcon from '@/components/SvgIcon/index.vue';
import { ref } from "vue";
import { RouteRecordRaw } from 'vue-router';
import AppLink from './Link.vue';

const onlyOneChild = ref();
const props = defineProps({
    item: {
        type: Object,
        required: true
    },
    isNest: {
        type: Boolean,
        required: false
    },
    basePath: {
        type: String,
        required: true
    }
});

const hasOneShowingChild = (children: RouteRecordRaw[], parent: any) => {
    if (!children) {
        children = [];
    }
    const showingChildren = children.filter((item) => {
        if (item.meta && item.meta.hidden) {
            return false;
        } else {
            onlyOneChild.value = item;
            return true;
        }
    });
    if (showingChildren.length === 1) {
        return true;
    }
    if (showingChildren.length === 0) {
        onlyOneChild.value = { ...parent, path: '', noShowingChildren: true };
        return true;
    }
    return false;
}

const resolvePath = (routePath: string) => {
    return getNormalPath(props.basePath + '/' + routePath)
}

const getNormalPath = (p: string) => {
    if (p.length === 0 || !p || p == 'undefined') {
        return p
    };
    let res = p.replace('//', '/')
    if (res[res.length - 1] === '/') {
        return res.slice(0, res.length - 1)
    }
    return res;
}
</script>

<style lang="scss" scoped>
.sidebar-item {
    .menu-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 14px 0;
        margin: 8px 0;
        border-radius: 6px;
        transition: all 0.3s ease;
        
        &:hover {
            background: rgba(255, 255, 255, 0.1);
        }
    }

    .menu-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        margin: 0 auto 8px;
        transition: all 0.3s ease;
        
        :deep(svg) {
            width: 28px;
            height: 28px;
        }
    }

    .menu-title {
        font-size: 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
        opacity: 0.9;
        text-align: center;
        font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
        
        &:hover {
            opacity: 1;
        }
    }
}

.sidebar-sub-menu {
    :deep(.el-sub-menu__title) {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 14px 0;
        margin: 8px 0;
        border-radius: 6px;
        transition: all 0.3s ease;
        
        &:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .el-icon {
            margin: 0 auto 8px !important;
            
            :deep(svg) {
                width: 28px;
                height: 28px;
            }
        }
        
        .menu-title {
            margin: 0 !important;
            font-size: 1rem;
        }
    }

    .nest-menu {
        .menu-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 14px 0 !important;
            background: transparent;
            
            &:hover {
                background: rgba(255, 255, 255, 0.05);
            }
        }
    }
}
</style>
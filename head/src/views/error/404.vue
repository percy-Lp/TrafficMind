<template>
    <div class="wscn-http404-container">
        <div class="wscn-http404">
            <div class="pic-404">
                <img class="pic-404__parent" src="@/assets/404_images/404.png" alt="404">
                <img class="pic-404__child left" src="@/assets/404_images/404_cloud.png" alt="404">
                <img class="pic-404__child mid" src="@/assets/404_images/404_cloud.png" alt="404">
                <img class="pic-404__child right" src="@/assets/404_images/404_cloud.png" alt="404">
            </div>
            <div class="bullshit">
                <div class="bullshit__oops">
                    404错误!
                </div>
                <div class="bullshit__headline">
                    {{ message }}
                </div>
                <div class="bullshit__info">
                    对不起，您正在寻找的页面不存在。尝试检查URL的错误，然后按浏览器上的刷新按钮或尝试在我们的应用程序中找到其他内容。
                </div>
                <router-link to="/index" class="bullshit__return-home">
                    返回首页
                </router-link>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
let message = computed(() => {
    return '找不到网页！'
})
</script>

<style lang="scss" scoped>
.wscn-http404-container {
    transform: translate(-50%, -50%);
    position: absolute;
    top: 40%;
    left: 50%;
    width: 100%;
    max-width: 1200px;
    padding: 2rem;
    box-sizing: border-box;
}

.wscn-http404 {
    position: relative;
    width: 100%;
    padding: 2rem;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
                0 10px 10px -5px rgba(0, 0, 0, 0.04);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;

    &:hover {
        transform: translateY(-5px);
        box-shadow: 0 25px 30px -5px rgba(0, 0, 0, 0.15);
    }

    .pic-404 {
        position: relative;
        float: left;
        width: 50%;
        overflow: hidden;
        padding: 1rem;

        &__parent {
            width: 100%;
            height: auto;
            filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
        }

        &__child {
            position: absolute;
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.05));

            &.left {
                width: 80px;
                top: 17px;
                left: 220px;
                opacity: 0;
                animation-name: cloudLeft;
                animation-duration: 2s;
                animation-timing-function: ease-in-out;
                animation-fill-mode: forwards;
                animation-delay: 1s;
            }

            &.mid {
                width: 46px;
                top: 10px;
                left: 420px;
                opacity: 0;
                animation-name: cloudMid;
                animation-duration: 2s;
                animation-timing-function: ease-in-out;
                animation-fill-mode: forwards;
                animation-delay: 1.2s;
            }

            &.right {
                width: 62px;
                top: 100px;
                left: 500px;
                opacity: 0;
                animation-name: cloudRight;
                animation-duration: 2s;
                animation-timing-function: ease-in-out;
                animation-fill-mode: forwards;
                animation-delay: 1s;
            }
        }
    }

    .bullshit {
        position: relative;
        float: left;
        width: 45%;
        padding: 2rem;
        overflow: hidden;

        &__oops {
            font-size: 2.5rem;
            font-weight: 700;
            line-height: 1.2;
            color: #2563eb;
            opacity: 0;
            margin-bottom: 1.5rem;
            animation-name: slideUp;
            animation-duration: 0.5s;
            animation-fill-mode: forwards;
            text-shadow: 0 2px 4px rgba(37, 99, 235, 0.1);
        }

        &__headline {
            font-size: 1.5rem;
            line-height: 1.4;
            color: #1e293b;
            font-weight: 600;
            opacity: 0;
            margin-bottom: 1rem;
            animation-name: slideUp;
            animation-duration: 0.5s;
            animation-delay: 0.1s;
            animation-fill-mode: forwards;
        }

        &__info {
            font-size: 1rem;
            line-height: 1.6;
            color: #64748b;
            opacity: 0;
            margin-bottom: 2rem;
            animation-name: slideUp;
            animation-duration: 0.5s;
            animation-delay: 0.2s;
            animation-fill-mode: forwards;
        }

        &__return-home {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: #2563eb;
            border-radius: 9999px;
            text-align: center;
            color: #ffffff;
            opacity: 0;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            animation-name: slideUp;
            animation-duration: 0.5s;
            animation-delay: 0.3s;
            animation-fill-mode: forwards;
            text-decoration: none;
            box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);

            &:hover {
                background: #1d4ed8;
                transform: translateY(-2px);
                box-shadow: 0 6px 8px rgba(37, 99, 235, 0.3);
            }
        }
    }
}

@media (max-width: 768px) {
    .wscn-http404 {
        padding: 1rem;
        
        .pic-404 {
            width: 100%;
            float: none;
            margin-bottom: 2rem;
        }
        
        .bullshit {
            width: 100%;
            float: none;
            padding: 1rem;
            text-align: center;
            
            &__return-home {
                display: block;
                margin: 0 auto;
                width: fit-content;
            }
        }
    }
}

@keyframes cloudLeft {
    0% {
        top: 17px;
        left: 220px;
        opacity: 0;
    }
    20% {
        top: 33px;
        left: 188px;
        opacity: 1;
    }
    80% {
        top: 81px;
        left: 92px;
        opacity: 1;
    }
    100% {
        top: 97px;
        left: 60px;
        opacity: 0;
    }
}

@keyframes cloudMid {
    0% {
        top: 10px;
        left: 420px;
        opacity: 0;
    }
    20% {
        top: 40px;
        left: 360px;
        opacity: 1;
    }
    70% {
        top: 130px;
        left: 180px;
        opacity: 1;
    }
    100% {
        top: 160px;
        left: 120px;
        opacity: 0;
    }
}

@keyframes cloudRight {
    0% {
        top: 100px;
        left: 500px;
        opacity: 0;
    }
    20% {
        top: 120px;
        left: 460px;
        opacity: 1;
    }
    80% {
        top: 180px;
        left: 340px;
        opacity: 1;
    }
    100% {
        top: 200px;
        left: 300px;
        opacity: 0;
    }
}

@keyframes slideUp {
    0% {
        transform: translateY(60px);
        opacity: 0;
    }
    100% {
        transform: translateY(0);
        opacity: 1;
    }
}
</style>

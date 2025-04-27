<template>
  <div class="container">
    <!-- 第一个视频背景区域 -->
    <section class="video-hero-section">
      <video
        ref="backgroundVideo"
        autoplay
        muted
        loop
        playsinline
        class="background-video"
      >
        <source src="@/assets/video/video4.mp4" type="video/mp4" />
      </video>
      <div class="video-overlay">
        <h1 class="hero-title">
          基于多源感知与协同强化学习的
          <br />
          智能交通信号灯调控系统
        </h1>
      </div>
    </section>

    <!-- 项目简介 -->
    <section class="section intro-section">
      <h2 class="section-title">项目概述</h2>
      <div class="intro-container">
        <div class="intro-content">
          <div class="pain-point-card">
            <div class="pain-icon">🔍</div>
            <div class="pain-content">
              <div class="intro-title">多源感知技术</div>
              <p>
                通过视频检测器与线圈检测器构建全域交通感知网络，实现毫秒级动态数据捕捉
              </p>
            </div>
          </div>
          <div class="pain-point-card">
            <div class="pain-icon">🧠</div>
            <div class="pain-content">
              <div class="intro-title">智能决策模型</div>
              <p>
                基于深度强化学习，以"全局等待时间最小化"为优化目标，突破传统静态配时局限
              </p>
            </div>
          </div>
          <div class="pain-point-card">
            <div class="pain-icon">📈</div>
            <div class="pain-content">
              <div class="intro-title">显著成效</div>
              <p>路口通行效率提升15%+，实现红绿灯相位与时长的自适应动态调控</p>
            </div>
          </div>
          <div class="pain-point-card">
            <div class="pain-icon">🏆</div>
            <div class="pain-content">
              <div class="intro-title">战略意义</div>
              <p>
                响应国家《交通强国建设纲要》，助力城市交通从被动响应迈向主动调控
              </p>
            </div>
          </div>
        </div>
        <div class="system-image">
          <img src="@/assets/images/system.png" alt="系统概述" />
        </div>
      </div>
    </section>

    <!-- 传统痛点 -->
    <section class="section pain-points-section">
      <h2 class="section-title">传统红绿灯的痛点</h2>
      <div class="pain-points-container">
        <div class="traffic-light-image">
          <img src="@/assets/images/traffic-light.png" alt="交通信号灯" />
        </div>
        <div class="pain-points-content">
          <div class="pain-point-card">
            <div class="pain-icon">⏱️</div>
            <div class="pain-content">
              <h3>反应迟缓</h3>
              <p>固定配时无法应对车流变化，导致部分路口空等红灯</p>
            </div>
          </div>
          <div class="pain-point-card">
            <div class="pain-icon">🚗</div>
            <div class="pain-content">
              <h3>交通拥堵</h3>
              <p>高峰期配时不合理造成车辆积压，加剧城市拥堵问题</p>
            </div>
          </div>
          <div class="pain-point-card">
            <div class="pain-icon">🚶</div>
            <div class="pain-content">
              <h3>安全隐患</h3>
              <p>无法感知特殊情况，行人与车辆冲突风险增加</p>
            </div>
          </div>
          <div class="pain-point-card">
            <div class="pain-icon">🌍</div>
            <div class="pain-content">
              <h3>环境影响</h3>
              <p>车辆频繁启停增加尾气排放，加剧环境污染</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 核心功能 -->
    <section class="section">
      <h2 class="section-title">核心功能</h2>
      <div class="core-features-container">
        <div class="feature-grid">
          <div class="feature-card">
            <div class="icon">🚗</div>
            <h3>实时车流感知</h3>
            <p>YOLOv11多目标跟踪，精度达98.6%</p>
          </div>
          <div class="feature-card">
            <div class="icon">🚦</div>
            <h3>智能信号调控</h3>
            <p>基于DQN算法的动态相位控制</p>
          </div>
          <div class="feature-card">
            <div class="icon">🌐</div>
            <h3>数字孪生仿真</h3>
            <p>多智能体协同 基于GAT的多智能体协同</p>
          </div>
        </div>
        <div class="core-image">
          <img src="@/assets/images/core.png" alt="核心技术" />
        </div>
      </div>
    </section>

    <!-- 技术优势 -->
    <section class="section">
      <h2 class="section-title">独特优势</h2>
      <div class="advantage-container">
        <div class="advantage-image left-image">
          <img src="@/assets/images/cpu.png" alt="处理器" />
        </div>
        <ul class="advantage-list">
          <li>✔️ 毫秒级车流识别响应</li>
          <li>✔️ 支持复杂天气条件检测</li>
          <li>✔️ 路口通行效率提升15%+</li>
          <li>✔️ 无需改造现有交通设施</li>
        </ul>
        <div class="advantage-image right-image">
          <img src="@/assets/images/city.png" alt="智慧城市" />
        </div>
      </div>
    </section>

    <!-- 底部移动的汽车 -->
    <div class="moving-bus" ref="movingBus">
      <img src="@/assets/images/bus.png" alt="移动的汽车" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated, onUnmounted } from "vue";

const backgroundVideo = ref(null);
const movingBus = ref(null);

// 播放视频的函数
const playVideo = () => {
  setTimeout(() => {
    if (backgroundVideo.value) {
      const playPromise = backgroundVideo.value.play();
      if (playPromise !== undefined) {
        playPromise
          .then(() => {})
          .catch((err) => {
            setTimeout(() => {
              backgroundVideo.value.play().catch(() => {});
            }, 1000);
          });
      }
    }
  }, 500);
};

// 控制底部汽车移动
const handleScroll = () => {
  if (movingBus.value) {
    const scrollPosition = window.scrollY;
    const documentHeight =
      document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercentage = Math.min(scrollPosition / documentHeight, 1);

    // 减去一部分距离，确保汽车不会完全移出视图
    const maxMove = window.innerWidth - 50;
    const moveDistance = scrollPercentage * maxMove;

    movingBus.value.style.transform = `translateX(${moveDistance}px)`;
  }
};

// 组件挂载时播放视频和添加滚动监听
onMounted(() => {
  playVideo();
  window.addEventListener("scroll", handleScroll);
  // 初始化汽车位置
  handleScroll();
});

// 组件卸载时移除滚动监听
onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll);
});

// 组件重新激活时播放视频
onActivated(() => {
  playVideo();
});
</script>

<style scoped>
.container {
  max-width: 100%;
  margin: 0;
  padding: 0;
  font-family: "Helvetica Neue", Arial, sans-serif;
  color: #333;
  background-color: #f8f9fa;
  box-shadow: none;
  border-radius: 0;
  position: relative;
  overflow-x: hidden;
}

.section {
  margin: 3rem 0;
  padding: 1.5rem;
  border-radius: 16px;
  background-color: white;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease;
  position: relative;
  z-index: 3;
}

@media (min-width: 768px) {
  .section {
    margin: 4rem 0;
    padding: 2rem;
  }
}

@media (min-width: 1440px) {
  .section {
    margin: 5rem 0;
    padding: 3rem;
  }
}

.section:hover {
  transform: translateY(-5px);
}

.intro-section {
  margin-top: 3rem;
  position: relative;
  z-index: 4;
  text-align: center;
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0.9),
    rgba(255, 255, 255, 0.8)
  );
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
}

.section-title {
  color: #2c3e50;
  font-size: 2rem;
  margin-bottom: 2.5rem;
  text-align: center;
  position: relative;
  padding-bottom: 10px;
}

.section-title:after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #4361ee, #3a0ca3);
  border-radius: 3px;
}

@media (min-width: 1440px) {
  .section-title {
    font-size: 2.5rem;
    margin-bottom: 3rem;
  }

  .section-title:after {
    width: 80px;
    height: 4px;
  }
}

.core-features-container {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.feature-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.core-image {
  flex: 0 0 auto;
  display: flex;
  justify-content: center;
  align-items: center;
}

.core-image img {
  width: 250px;
  height: auto;
  object-fit: contain;
  transition: transform 0.8s ease;
}

.core-image img:hover {
  transform: rotate(360deg);
}

@media (max-width: 1200px) {
  .core-features-container {
    flex-direction: column;
  }

  .feature-grid {
    width: 100%;
  }

  .core-image img {
    width: 200px;
    margin-top: 2rem;
  }
}

@media (min-width: 768px) {
  .feature-grid {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
  }
}

@media (min-width: 1440px) {
  .core-features-container {
    gap: 3rem;
  }

  .feature-grid {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2.5rem;
  }

  .core-image img {
    width: 300px;
  }
}

.feature-card {
  background: #f9f9f9;
  border-radius: 12px;
  padding: 2.5rem 2rem;
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid #eaeaea;
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
  border-color: #4361ee;
}

.feature-card h3 {
  color: #2c3e50;
  margin: 1rem 0;
  font-weight: 600;
}

@media (min-width: 1440px) {
  .feature-card {
    padding: 3rem 2.5rem;
  }

  .feature-card h3 {
    font-size: 1.5rem;
    margin: 1.2rem 0;
  }

  .feature-card p {
    font-size: 1.2rem;
  }
}

.icon {
  font-size: 3.5rem;
  margin-bottom: 1.5rem;
  display: inline-block;
  background: #f0f4f8;
  width: 80px;
  height: 80px;
  line-height: 80px;
  border-radius: 50%;
}

@media (min-width: 1440px) {
  .icon {
    font-size: 4rem;
    width: 100px;
    height: 100px;
    line-height: 100px;
    margin-bottom: 2rem;
  }
}

.advantage-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  margin: 2rem auto;
}

.advantage-image {
  flex: 0 0 auto;
  display: flex;
  justify-content: center;
  align-items: center;
}

.advantage-image img {
  width: 150px;
  height: auto;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.advantage-image img:hover {
  transform: translateY(-8px);
}

.advantage-list {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  max-width: 100%;
  margin: 0;
  padding: 0;
  list-style: none;
}

@media (min-width: 768px) {
  .advantage-list {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.8rem;
    max-width: 800px;
  }
}

@media (max-width: 768px) {
  .advantage-container {
    flex-direction: column;
  }

  .advantage-image img {
    width: 120px;
    margin: 1rem 0;
  }
}

@media (min-width: 1440px) {
  .advantage-container {
    gap: 3rem;
  }

  .advantage-image img {
    width: 180px;
  }

  .advantage-list {
    grid-template-columns: repeat(2, 1fr);
    gap: 2.5rem;
    max-width: 1200px;
  }
}

.advantage-list li {
  padding: 1rem 1.5rem;
  color: #2c3e50;
  line-height: 1.6;
  position: relative;
  background-color: #f0f4f8;
  border-radius: 8px;
  font-weight: 500;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

@media (min-width: 1440px) {
  .advantage-list li {
    padding: 1.5rem 2rem;
    font-size: 1.3rem;
    line-height: 1.7;
  }
}

.advantage-list li:hover {
  background-color: #e6eaef;
  transform: translateX(5px);
}

.pain-points-section {
  margin-top: 3rem;
}

.pain-points-container {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.traffic-light-image {
  flex: 0 0 auto;
  display: flex;
  justify-content: center;
  align-items: center;
}

.traffic-light-image img {
  width: 150px;
  height: auto;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.traffic-light-image img:hover {
  transform: translateY(-10px);
}

.pain-points-content {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.pain-point-card {
  display: flex;
  padding: 1.5rem;
  border-radius: 12px;
  background-color: #f8f9fa;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  border: 1px solid #eaeaea;
}

.pain-point-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  border-color: #4361ee;
}

.pain-icon {
  font-size: 2.2rem;
  background: #f0f4f8;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .pain-points-container {
    flex-direction: column;
  }

  .pain-points-content {
    grid-template-columns: 1fr;
  }

  .traffic-light-image img {
    width: 120px;
    margin-bottom: 1.5rem;
  }
}

@media (min-width: 1440px) {
  .pain-points-container {
    gap: 3rem;
  }

  .traffic-light-image img {
    width: 180px;
  }

  .pain-points-content {
    gap: 2rem;
  }
}

.pain-content h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-weight: 600;
}

.pain-content p {
  margin: 0;
  color: #5a6a7a;
  line-height: 1.6;
}

@media (min-width: 1440px) {
  .pain-content h3 {
    font-size: 1.5rem;
    margin-bottom: 0.8rem;
  }

  .pain-content p {
    font-size: 1.2rem;
    line-height: 1.7;
  }
}

.video-hero-section {
  position: relative;
  width: 100%;
  height: 110vh;
  overflow: hidden;
  margin-top: -64px;
  padding: 0;
}

.background-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.3) 80%,
    rgba(0, 0, 0, 0.1)
  );
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.video-overlay .hero-title {
  color: #fff;
  font-size: 2.5rem;
  font-weight: 700;
  text-align: center;
  line-height: 1.2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  margin: 0;
  padding: 0 20px;
  max-width: 100%;
}

@media (max-width: 768px) {
  .video-overlay .hero-title {
    font-size: 2rem;
  }
}

@media (min-width: 769px) and (max-width: 1023px) {
  .video-overlay .hero-title {
    font-size: 3rem;
    max-width: 90%;
  }
}

@media (min-width: 1024px) and (max-width: 1439px) {
  .video-overlay .hero-title {
    font-size: 3.5rem;
    max-width: 1000px;
    line-height: 1.25;
  }
}

@media (min-width: 1440px) {
  .video-hero-section {
    height: 120vh;
  }

  .video-overlay .hero-title {
    font-size: 4.5rem;
    max-width: 1400px;
    padding: 0 40px;
    line-height: 1.3;
  }
}

@media (min-width: 1800px) {
  .section-title {
    font-size: 3rem;
  }

  .feature-card h3 {
    font-size: 1.8rem;
  }

  .feature-card p {
    font-size: 1.4rem;
  }

  .advantage-list li {
    font-size: 1.5rem;
    padding: 1.8rem 2.5rem;
  }

  .pain-content h3 {
    font-size: 1.8rem;
  }

  .pain-content p {
    font-size: 1.4rem;
  }

  .intro-title {
    font-size: 1.8rem;
  }

  .intro-content p {
    font-size: 1.4rem;
  }

  .video-overlay .hero-title {
    font-size: 5.5rem;
    max-width: 1600px;
  }
}

@media (min-width: 2560px) {
  .video-overlay .hero-title {
    font-size: 7rem;
    max-width: 2000px;
    line-height: 1.4;
  }
}

.moving-bus {
  position: fixed;
  bottom: -8px;
  left: 0;
  z-index: 100;
  pointer-events: none;
  transition: transform 0.1s ease-out;
}

.moving-bus img {
  width: 35px;
  height: auto;
  object-fit: contain;
}

@media (min-width: 768px) {
  .moving-bus img {
    width: 40px;
  }
}

@media (min-width: 1440px) {
  .moving-bus {
    bottom: -10px;
  }

  .moving-bus img {
    width: 45px;
  }
}

.intro-container {
  margin: 2rem auto;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.intro-content {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.system-image {
  flex: 0 0 auto;
  display: flex;
  justify-content: center;
  align-items: center;
}

.system-image img {
  width: 180px;
  height: auto;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.system-image img:hover {
  transform: rotate(10deg);
}

@media (max-width: 768px) {
  .intro-container {
    flex-direction: column;
  }

  .intro-content {
    grid-template-columns: 1fr;
    width: 100%;
  }

  .system-image img {
    width: 150px;
    margin-top: 1.5rem;
  }
}

@media (min-width: 1440px) {
  .intro-container {
    gap: 3rem;
  }

  .intro-content {
    gap: 2rem;
  }

  .system-image img {
    width: 220px;
  }
}

.intro-title {
  font-size: inherit;
  font-weight: 600;
  color: #2c3e50;
  margin-top: 0;
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  height: 1.5em;
  line-height: 1.5em;
  display: flex;
  align-items: center;
}

.intro-content p {
  margin: 0;
  color: #5a6a7a;
  line-height: 1.6;
}

@media (min-width: 1440px) {
  .intro-title {
    font-size: 1.5rem;
    margin-bottom: 0.8rem;
  }

  .intro-content p {
    font-size: 1.2rem;
    line-height: 1.7;
  }
}
</style>

<template>
  <div class="dashboard-container">
    <div class="chart-wrapper">
      <div class="content row-layout">
        <!-- 左侧区域 -->
        <div class="charts-container">
          <!-- 信号灯状态卡片 -->
          <div class="card card-float card-traffic-light">
            <div class="card-header">
              <div class="card-title">
                {{
                  showIntersectionChart && trafficLightData
                    ? `路口 ${parseInt(selectedIntersection) + 1} 信号灯状态`
                    : "路口信号灯状态"
                }}
              </div>
              <div class="card-badge">🚦 信号控制</div>
            </div>
            <div
              v-if="showIntersectionChart && trafficLightData"
              class="traffic-light-container"
            >
              <div v-if="trafficLightData.error" class="error-message">
                {{ trafficLightData.error }}
              </div>
              <div v-else>
                <div
                  v-for="stepIndex in displayedTimeSteps"
                  :key="stepIndex"
                  class="time-step"
                  :class="{
                    'latest-step': stepIndex === displayedTimeSteps.length - 1,
                  }"
                >
                  <div class="time-step-header">
                    <span class="time-badge"
                      >时间步
                      {{
                        trafficLightData.time_steps[stepIndex].time_step
                      }}</span>
                    <span class="phase-badge"
                      >相位
                      {{ trafficLightData.time_steps[stepIndex].phase }} ({{
                        trafficLightData.time_steps[stepIndex].duration
                      }}秒)</span>
                  </div>
                  <div class="connections">
                    <div
                      v-for="(conn, connIndex) in trafficLightData.time_steps[
                        stepIndex
                      ].connections"
                      :key="connIndex"
                      class="connection"
                    >
                      <div class="connection-description">
                        {{ conn.description }}
                      </div>
                      <div class="connection-states">
                        <span
                          v-for="(char, charIndex) in conn.states"
                          :key="charIndex"
                          :class="getStateClass(char)"
                          class="state-box"
                        ></span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="hint-content">
              <div>
                <i class="el-icon-arrow-right"></i>
                请点击地图上的路口名称查看详细数据
              </div>
            </div>
          </div>

          <!-- 调控效果卡片 - 放在中间 -->
          <div class="card card-float card-improvement">
            <div class="card-header">
              <div class="card-title">调控效果</div>
              <div class="card-badge">📈 改善数据</div>
            </div>
            <div
              v-if="showIntersectionChart && improvementData"
              class="improvement-data-container"
            >
              <div class="stats-summary">
                <div class="stats-row">
                  <div
                    class="stat-box"
                    :class="{ 'data-updated': isDataUpdated }"
                  >
                    <div
                      class="stat-value"
                      :class="
                        getImprovementClass(
                          improvementData?.congestion_decrease
                        )
                      "
                    >
                      {{
                        improvementData?.congestion_decrease
                          ? improvementData.congestion_decrease.toFixed(2)
                          : "0.00"
                      }}%
                    </div>
                    <div class="stat-label">拥堵减少</div>
                  </div>
                  <div
                    class="stat-box"
                    :class="{ 'data-updated': isDataUpdated }"
                  >
                    <div
                      class="stat-value"
                      :class="
                        getImprovementClass(improvementData?.delay_decrease)
                      "
                    >
                      {{
                        improvementData?.delay_decrease
                          ? improvementData.delay_decrease.toFixed(2)
                          : "0.00"
                      }}%
                    </div>
                    <div class="stat-label">延迟减少</div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="hint-content">
              <div>
                <i class="el-icon-arrow-right"></i>
                请点击地图上的路口名称查看调控效果数据
              </div>
            </div>
          </div>

          <!-- 路口指标图表 - 放在最下方 -->
          <div class="card card-float card-intersection">
            <div class="card-header">
              <div class="card-title">
                {{
                  showIntersectionChart
                    ? `路口 ${parseInt(selectedIntersection) + 1} 指标`
                    : "路口指标"
                }}
              </div>
              <div class="card-badge">🔍 详细数据</div>
            </div>
            <div v-if="showIntersectionChart" class="charts-wrapper">
              <div class="chart-container-group">
                <div class="chart-title">奖励数据</div>
                <div
                  id="rewardContainer"
                  class="chart-container"
                  ref="rewardChartRef"
                ></div>
              </div>
              <div class="chart-container-group">
                <div class="chart-title">队列长度数据</div>
                <div
                  id="queueContainer"
                  class="chart-container"
                  ref="queueChartRef"
                ></div>
              </div>
            </div>
            <div v-else class="hint-content">
              <div>
                <i class="el-icon-arrow-right"></i>
                请点击地图上的路口名称查看详细数据
              </div>
            </div>
          </div>
        </div>

        <!-- 地图卡片 - 放置在右侧 -->
        <div class="card card-float card-main map-corner">
          <div class="card-header">
            <div class="card-title">实时地图</div>
            <div class="card-badge">🚦 实时监控</div>
          </div>
          <div class="map-container">
            <div id="map"></div>
            <div v-if="mapLoadError" class="error-message">
              地图加载失败，请刷新页面重试
            </div>
            <!-- 添加地图图例 -->
            <div class="map-legend">
              <div class="legend-title">拥堵状态图例</div>
              <div class="legend-item">
                <span class="legend-icon legend-green"></span>
                <span class="legend-text">畅通 </span>
              </div>
              <div class="legend-item">
                <span class="legend-icon legend-yellow"></span>
                <span class="legend-text">正常 </span>
              </div>
              <div class="legend-item">
                <span class="legend-icon legend-red"></span>
                <span class="legend-text">拥堵</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, onBeforeUnmount, nextTick, watch } from "vue";
import axios from "axios";
import { ElMessage } from "element-plus";

const mapLoadError = ref(false);
const showIntersectionChart = ref(false);
const selectedIntersection = ref(null);
const intersectionChartRef = ref(null);
const initialDataLoaded = ref(false);
// 存储信号灯数据
const trafficLightData = ref(null);
// 存储已经显示的时间步索引
const displayedTimeSteps = ref([]);
// 存储交通改善数据
const improvementData = ref(null);
// 标记数据是否刚刚更新
const isDataUpdated = ref(false);
// 自动播放定时器
let autoPlayTimer = null;
// 数据更新定时器
let dataUpdateTimer = null;
// 存储完整的路口数据
let fullIntersectionData = null;
// 当前显示的数据索引
let currentDataIndex = 1;

const rewardChartRef = ref(null);
const queueChartRef = ref(null);
let intersectionChart = null;
let rewardChart = null;
let queueChart = null;
let trainingChart = null;
let echarts = null;
// 存储后端发送的改善数据
const allImprovementData = ref([]);
// 当前显示的改善数据索引
let currentImprovementIndex = 0;

// 全局存储标记和当前episode索引
let markers = [];
let currentEpisode = 0;
let totalEpisodes = 0;
// 添加拥堵数据更新定时器引用
let congestionTimer = null;

// 创建统一的日志函数，可以根据环境开关日志输出
const debugMode = false;
function log(...args) {
  if (debugMode) {
    console.log(...args);
  }
}

function error(...args) {
  console.error(...args);
}

function loadECharts() {
  return new Promise((resolve) => {
    if (window.echarts) {
      echarts = window.echarts;
      resolve();
      return;
    }

    const script = document.createElement("script");
    script.src =
      "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js";
    script.onload = () => {
      echarts = window.echarts;
      resolve();
    };
    document.head.appendChild(script);
  });
}

function loadMap() {
  if (document.getElementById("tianditu-api")) {
    initMap();
    return;
  }

  const script = document.createElement("script");
  script.id = "tianditu-api";
  script.src =
    "https://api.tianditu.gov.cn/api?v=4.0&tk=a15978e7aabf4ac8abbe0c153db00b3d";

  script.onload = () => {
    // 减少初始化延迟
    initMap();
  };

  script.onerror = () => {
    mapLoadError.value = true;
  };

  document.head.appendChild(script);
}

function initMap() {
  try {
    if (typeof T === "undefined") {
      mapLoadError.value = true;
      return;
    }

    const mapContainer = document.getElementById("map");
    if (!mapContainer) {
      return;
    }

    const map = new T.Map("map");

    // 设置中心点和缩放级别（杭州市中心）
    map.centerAndZoom(new T.LngLat(120.1095712, 30.288957), 14);

    // 添加控件
    map.addControl(new T.Control.Zoom());
    map.addControl(new T.Control.Scale());

    // 添加点位并保存地图引用以便后续更新
    window.bMap = map;
    addMapPoints(map);

    // 如果已经有定时器，先清除
    if (congestionTimer) {
      clearInterval(congestionTimer);
    }

    // 设置更长的间隔时间，减少不必要的API调用
    congestionTimer = setInterval(fetchCongestionData, 30000);

    // 初始化后立即获取一次数据
    fetchCongestionData();

    log("地图初始化完成");
  } catch (error) {
    error("地图初始化失败:", error);
    mapLoadError.value = true;
  }
}

// 获取默认图表选项
function getDefaultChartOption(containerId) {
  return {
    title: {
      text: "",
      textStyle: {
        fontSize: 14,
        fontWeight: "bold",
      },
    },
    tooltip: {
      trigger: "axis",
    },
    legend: {
      data: ["奖励", "队列长度"],
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: [],
    },
    yAxis: {
      type: "value",
    },
    series: [
      {
        name: "奖励",
        type: "line",
        data: [],
        symbol: "circle",
        symbolSize: 8,
        itemStyle: {
          color: "#2196F3",
        },
        lineStyle: {
          width: 3,
        },
      },
      {
        name: "队列长度",
        type: "line",
        data: [],
        symbol: "rect",
        symbolSize: 8,
        itemStyle: {
          color: "#FF5722",
        },
        lineStyle: {
          width: 3,
          type: "dashed",
        },
      },
    ],
  };
}

// 简化forceRenderChart函数，删除过多的错误处理和冗余逻辑
function forceRenderChart(containerId, option) {
  try {
    // 1. 获取容器并确保有效
    const originalContainer = document.getElementById(containerId);
    if (!originalContainer || !originalContainer.parentNode) return;

    // 2. 移除原始容器并创建新容器
    const parentContainer = originalContainer.parentNode;
    parentContainer.removeChild(originalContainer);

    const newContainer = document.createElement("div");
    newContainer.id = containerId;
    newContainer.className = "chart-container";
    newContainer.style.width = "100%";
    newContainer.style.height = "400px";
    newContainer.style.minHeight = "400px !important";
    newContainer.style.display = "block";
    newContainer.style.visibility = "visible";
    parentContainer.appendChild(newContainer);

    // 3. 确保ECharts已加载
    if (!window.echarts) return;

    // 4. 处理图表选项
    let finalOption = option;
    if (!option || typeof option !== "object") {
      finalOption = getDefaultChartOption(containerId);
    } else if (
      option.intersection_data &&
      containerId === "intersectionContainer"
    ) {
      finalOption = option.intersection_data;
    } else if (
      option.training_metrics &&
      containerId === "trainingMetricsContainer"
    ) {
      finalOption = option.training_metrics;
    }

    // 5. 确保系列数据有效
    if (
      !finalOption.series ||
      !Array.isArray(finalOption.series) ||
      finalOption.series.length === 0
    ) {
      finalOption.series =
        containerId === "trainingMetricsContainer"
          ? [
              {
                name: "Q损失",
                type: "line",
                data: [],
                symbolSize: 8,
                itemStyle: { color: "#FF5722" },
              },
              {
                name: "奖励",
                type: "line",
                data: [],
                symbolSize: 8,
                itemStyle: { color: "#2196F3" },
              },
              {
                name: "延迟",
                type: "line",
                data: [],
                symbolSize: 8,
                itemStyle: { color: "#FF9800" },
              },
              {
                name: "吞吐量",
                type: "line",
                data: [],
                symbolSize: 8,
                itemStyle: { color: "#4CAF50" },
              },
            ]
          : [
              {
                name: "奖励",
                type: "line",
                data: [],
                symbolSize: 8,
                itemStyle: { color: "#2196F3" },
                lineStyle: { width: 3 },
              },
              {
                name: "队列长度",
                type: "line",
                data: [],
                symbolSize: 8,
                itemStyle: { color: "#FF5722" },
                lineStyle: { width: 3, type: "dashed" },
              },
            ];
    }

    // 6. 确保其他基本图表配置
    finalOption.title = finalOption.title || {};
    finalOption.title.text = "";

    finalOption.tooltip = finalOption.tooltip || { trigger: "axis" };
    finalOption.grid = finalOption.grid || {
      left: "3%",
      right: "4%",
      bottom: "3%",
      containLabel: true,
    };

    if (!finalOption.legend) {
      finalOption.legend = {
        data: finalOption.series.map((s) => s.name),
        textStyle: { color: "#333" },
      };
    }

    finalOption.xAxis = finalOption.xAxis || { type: "category", data: [] };
    finalOption.yAxis = finalOption.yAxis || { type: "value" };

    // 7. 创建并初始化图表
    const chart = window.echarts.init(newContainer);
    chart.setOption(finalOption);

    // 8. 保存引用并调整大小
    if (containerId === "trainingMetricsContainer") {
      trainingChart = chart;
    } else if (containerId === "intersectionContainer") {
      intersectionChart = chart;
    }

    setTimeout(() => chart.resize(), 100);
  } catch (error) {
    error("渲染图表出错:", error);
  }
}

// 初始化全局echarts变量，如果loadECharts函数已执行，则直接使用window.echarts
function initEchartsVar() {
  if (!echarts && window.echarts) {
    echarts = window.echarts;
  }
}

// 获取改善数据值的样式类
function getImprovementClass(value) {
  if (!value && value !== 0) return "improvement-neutral";

  if (value > 0) {
    return value > 10 ? "improvement-positive-high" : "improvement-positive";
  } else if (value < 0) {
    return value < -10 ? "improvement-negative-high" : "improvement-negative";
  }
  return "improvement-neutral";
}

// 添加变量跟踪是否是第一次点击
const isFirstMapClick = ref(true);

// 路口点击处理函数
function handlePointClick(index) {
  // 更新选中的路口
  selectedIntersection.value = index;

  // 显示路口图表区域
  showIntersectionChart.value = true;

  // 重置信号灯数据
  trafficLightData.value = null;

  // 只有第一次点击时才更新调控效果数据
  if (isFirstMapClick.value) {
    // 重置改善数据
    improvementData.value = null;
    // 清空所有改善数据
    allImprovementData.value = [];
    // 重置当前改善数据索引
    currentImprovementIndex = 0;

    // 重置数据更新标志
    isDataUpdated.value = false;

    // 清除之前的定时器
    if (dataUpdateTimer) {
      clearInterval(dataUpdateTimer);
      dataUpdateTimer = null;
    }
  }

  // 重置当前数据索引
  currentDataIndex = 1;

  // 延迟渲染，确保DOM已更新
  setTimeout(() => {
    // 发送请求获取数据
    axios
      .post("http://127.0.0.1:5500/map_point_click", { index })
      .then((response) => {
        if (response.data && response.data.code === 200 && response.data.data) {
          const data = response.data.data;

          log("接收到路口数据");

          // 只有第一次点击时处理改善数据
          if (
            isFirstMapClick.value &&
            data.all_improvement_data &&
            data.all_improvement_data.length > 0
          ) {
            // 保存所有历史数据
            allImprovementData.value = data.all_improvement_data;

            // 从第一组数据开始显示
            currentImprovementIndex = 0;
            improvementData.value = allImprovementData.value[0];

            // 触发更新动画
            isDataUpdated.value = true;
            setTimeout(() => {
              isDataUpdated.value = false;
            }, 1000);

            // 设置定时器，每18秒更新一次显示的改善数据
            dataUpdateTimer = setInterval(() => {
              // 更新到下一组数据
              currentImprovementIndex =
                (currentImprovementIndex + 1) % allImprovementData.value.length;
              improvementData.value =
                allImprovementData.value[currentImprovementIndex];

              // 触发数据更新动画
              isDataUpdated.value = true;
              setTimeout(() => {
                isDataUpdated.value = false;
              }, 1000);
            }, 18000);

            // 设置为非第一次点击状态 - 移到这里确保数据处理后再更新状态
            isFirstMapClick.value = false;
          } else if (isFirstMapClick.value && data.improvement_data) {
            // 如果没有历史数据但有单组数据
            improvementData.value = data.improvement_data;

            // 设置为非第一次点击状态
            isFirstMapClick.value = false;
          }

          if (data.intersection_data) {
            if (
              data.intersection_data.series &&
              data.intersection_data.series.length > 0
            ) {
            }

            // 保存完整数据
            fullIntersectionData = JSON.parse(
              JSON.stringify(data.intersection_data)
            );

            // 创建只包含第一个数据点的副本
            const initialData = JSON.parse(
              JSON.stringify(data.intersection_data)
            );

            // 验证数据是否足够
            if (
              initialData.series &&
              initialData.series.length > 0 &&
              initialData.series[0].data &&
              initialData.series[0].data.length > 1
            ) {
              // 只保留第一个数据点以初始化图表
              initialData.series.forEach((series) => {
                if (series.data && series.data.length > 0) {
                  // 保存第一个点的值
                  const firstPoint = series.data[0];
                  // 清空数组并重新添加第一个点
                  series.data = [firstPoint];
                }
              });

              // 同样处理X轴数据
              if (
                initialData.xAxis &&
                initialData.xAxis.data &&
                initialData.xAxis.data.length > 0
              ) {
                const firstX = initialData.xAxis.data[0];
                initialData.xAxis.data = [firstX];
              }
            }

            // 渲染初始图表（只有一个点）
            renderSplitCharts(initialData);

            // 缓存数据供后续使用
            if (!window.allIntersectionData) {
              window.allIntersectionData = {};
            }
            window.allIntersectionData[index] = initialData;

            // 清除之前的定时器
            if (dataUpdateTimer) {
              clearInterval(dataUpdateTimer);
            }

            // 设置图表更新定时器，确保始终创建一个新的定时器
            currentDataIndex = 1;
            dataUpdateTimer = setInterval(() => {
              updateIntersectionChart();
            }, 18000);
          } else {
            forceRenderChart(
              "intersectionContainer",
              getDefaultChartOption("intersectionContainer")
            );
          }

          // 处理信号灯数据 - 新增
          if (data.traffic_light_data) {
            trafficLightData.value = data.traffic_light_data;
          }
        } else {
          forceRenderChart(
            "intersectionContainer",
            getDefaultChartOption("intersectionContainer")
          );
        }
      })
      .catch((error) => {
        forceRenderChart(
          "intersectionContainer",
          getDefaultChartOption("intersectionContainer")
        );
      });
  }, 100);
}

// 更新路口图表，添加新的数据点
function updateIntersectionChart() {
  if (!rewardChart || !queueChart) {
    return;
  }

  if (!fullIntersectionData) {
    return;
  }

  if (!fullIntersectionData.series || fullIntersectionData.series.length < 2) {
    return;
  }

  // 修改：如果已经添加了所有数据点，重置索引从头开始，而不是停止定时器
  if (currentDataIndex >= fullIntersectionData.series[0].data.length) {
    log("路口指标图数据显示完毕，开始循环播放");
    // 重置索引到第一个数据点
    currentDataIndex = 0;

    // 重新渲染初始图表
    const initialData = JSON.parse(JSON.stringify(fullIntersectionData));
    initialData.series.forEach((series) => {
      series.data = series.data.slice(0, 1);
    });
    initialData.xAxis.data = initialData.xAxis.data.slice(0, 1);

    // 重新渲染图表
    renderSplitCharts(initialData);
    return;
  }

  // 获取当前奖励图表的选项
  const rewardOption = rewardChart.getOption();

  // 获取当前队列图表的选项
  const queueOption = queueChart.getOption();

  // 添加新的X轴数据点到两个图表
  if (currentDataIndex < fullIntersectionData.xAxis.data.length) {
    const newXPoint = fullIntersectionData.xAxis.data[currentDataIndex];
    rewardOption.xAxis[0].data.push(newXPoint);
    queueOption.xAxis[0].data.push(newXPoint);
  }

  // 添加奖励数据
  if (
    fullIntersectionData.series[0] &&
    currentDataIndex < fullIntersectionData.series[0].data.length
  ) {
    rewardOption.series[0].data.push(
      fullIntersectionData.series[0].data[currentDataIndex]
    );
  }

  // 添加队列长度数据
  if (
    fullIntersectionData.series[1] &&
    currentDataIndex < fullIntersectionData.series[1].data.length
  ) {
    queueOption.series[0].data.push(
      fullIntersectionData.series[1].data[currentDataIndex]
    );
  }

  // 更新两个图表
  rewardChart.setOption(rewardOption);
  queueChart.setOption(queueOption);

  // 更新索引
  currentDataIndex++;

  // 同时更新调控效果数据
  if (allImprovementData.value && allImprovementData.value.length > 0) {
    // 更新到下一组数据
    currentImprovementIndex =
      (currentImprovementIndex + 1) % allImprovementData.value.length;
    improvementData.value = allImprovementData.value[currentImprovementIndex];

    // 触发数据更新动画
    isDataUpdated.value = true;
    setTimeout(() => {
      isDataUpdated.value = false;
    }, 1000);
  }
}

// 获取信号灯状态的CSS类 - 新增
function getStateClass(state) {
  const classMap = {
    G: "state-green",
    g: "state-green",
    r: "state-red",
    y: "state-yellow",
    s: "state-yellow",
  };
  return classMap[state] || "";
}

// 监听路口图表可见性变化
watch(showIntersectionChart, (newVal) => {
  if (newVal && selectedIntersection.value !== null) {
    // 清除之前的定时器
    if (dataUpdateTimer) {
      clearInterval(dataUpdateTimer);
      dataUpdateTimer = null;
    }

    // 重置当前数据索引
    currentDataIndex = 1;
    currentImprovementIndex = 0; // 重置改善数据索引

    setTimeout(() => {
      // 如果有完整数据且图表正在显示
      if (fullIntersectionData && newVal) {
        // 创建只包含第一个数据点的副本
        const initialData = JSON.parse(JSON.stringify(fullIntersectionData));
        initialData.series.forEach((series) => {
          series.data = series.data.slice(0, 1);
        });
        initialData.xAxis.data = initialData.xAxis.data.slice(0, 1);

        // 渲染初始图表（只有一个点）
        renderSplitCharts(initialData);

        // 设置定时器，每18秒添加一个数据点
        dataUpdateTimer = setInterval(() => {
          updateIntersectionChart();
        }, 18000);
      } else {
        const data =
          window.allIntersectionData &&
          window.allIntersectionData[selectedIntersection.value]
            ? window.allIntersectionData[selectedIntersection.value]
            : getDefaultChartOption("intersectionContainer");

        if (typeof data === "object" && !Array.isArray(data)) {
          renderSplitCharts(data);
        }
      }
    }, 200);
  } else {
    // 当图表隐藏时，清除定时器和数据
    if (dataUpdateTimer) {
      clearInterval(dataUpdateTimer);
      dataUpdateTimer = null;
    }

    // 清除改善数据
    improvementData.value = null;
    allImprovementData.value = [];
    currentImprovementIndex = 0;
  }
});

function handleResize() {
  // 延迟执行，避免频繁触发
  if (window.resizeTimer) {
    clearTimeout(window.resizeTimer);
  }

  window.resizeTimer = setTimeout(() => {
    if (trainingChart) {
      trainingChart.resize();
    }
    if (rewardChart) {
      rewardChart.resize();
    }
    if (queueChart) {
      queueChart.resize();
    }
  }, 300);
}

// 颜色判断逻辑
function getColor(meanQueue) {
  // 绿色-畅通
  if (meanQueue < 5) return "#4CAF50";
  // 橙色-一般
  else if (meanQueue < 10) return "#FF9800";
  // 红色-拥堵
  else return "#F44336";
}

// 动态生成图标
function createIcon(color) {
  return new T.Icon({
    iconUrl:
      "data:image/svg+xml;charset=utf-8," +
      encodeURIComponent(`
      <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40">
        <circle cx="20" cy="20" r="15" fill="none" stroke="${color}" stroke-width="2">
          <animate attributeName="r" from="5" to="15" dur="1.5s" repeatCount="indefinite" />
          <animate attributeName="opacity" from="1" to="0" dur="1.5s" repeatCount="indefinite" />
        </circle>
        <circle cx="20" cy="20" r="5" fill="${color}">
          <animate attributeName="opacity" from="1" to="0.5" dur="1.5s" repeatCount="indefinite" />
        </circle>
      </svg>
    `),
    iconSize: new T.Point(40, 40),
  });
}

// 获取拥堵数据并更新标记
function fetchCongestionData() {
  // 添加时间戳避免缓存问题
  const timestamp = new Date().getTime();
  // 使用完整URL路径，确保指向正确的后端地址
  fetch(
    `http://127.0.0.1:5500/api/congestion?episode=${currentEpisode}&_t=${timestamp}`
  )
    .then((response) => response.json())
    .then((res) => {
      // 更新总episode数
      if (totalEpisodes === 0 && res.total > 0) totalEpisodes = res.total;

      // 更新标记颜色
      if (res.data && res.data.length > 0) {
        res.data.forEach((item) => {
          const marker = markers.find((m) => m.id === item.id);
          if (marker) {
            const color = getColor(item.mean_queue);
            marker.setIcon(createIcon(color));
          }
        });

        // 自动递增，循环播放
        currentEpisode = (res.current + 1) % totalEpisodes;
      }
    })
    .catch((error) => error("获取拥堵数据失败:", error));
}

function addMapPoints(map) {
  // 路口数据
  const points = [
    { lng: 120.0960253, lat: 30.278057, name: "文三-古墩", index: "0" },
    { lng: 120.0949253, lat: 30.2837773, name: "文二-古墩", index: "1" },
    { lng: 120.0938253, lat: 30.2887773, name: "文一-古墩", index: "2" },
    { lng: 120.0933253, lat: 30.2972773, name: "余杭塘-古墩", index: "3" },
    { lng: 120.1061253, lat: 30.27838, name: "文三-丰潭", index: "4" },
    { lng: 120.1043253, lat: 30.2841773, name: "文二-丰潭", index: "5" },
    { lng: 120.1029253, lat: 30.2890773, name: "文一-丰潭", index: "6" },
    { lng: 120.1016253, lat: 30.2958773, name: "余杭塘-丰潭", index: "7" },
    { lng: 120.114998, lat: 30.27863, name: "文三-古翠", index: "8" },
    { lng: 120.114638, lat: 30.2845813, name: "文二-古翠", index: "9" },
    { lng: 120.114338, lat: 30.2898773, name: "文一-古翠", index: "10" },
    { lng: 120.113738, lat: 30.2961773, name: "余杭塘-古翠", index: "11" },
    { lng: 120.1251726, lat: 30.278997, name: "文三-学院", index: "12" },
    { lng: 120.1247526, lat: 30.2848973, name: "文二-学院", index: "13" },
    { lng: 120.1242526, lat: 30.2902073, name: "文一-学院", index: "14" },
    { lng: 120.1238226, lat: 30.2967773, name: "余杭塘-学院", index: "15" },
  ];

  // 清空现有标记
  markers = [];

  // 添加点位
  points.forEach((point, index) => {
    try {
      // 添加标签
      const label = new T.Label({
        position: new T.LngLat(point.lng, point.lat),
        text: point.name,
        offset: new T.Point(0, 25),
      });

      // 添加点击事件
      label.addEventListener("click", () => {
        handlePointClick(point.index);
      });

      map.addOverLay(label);

      // 获取初始颜色 - 使用预加载的拥堵数据
      let initialColor = "#F44336"; // 默认红色
      if (window.initialCongestionData) {
        const pointData = window.initialCongestionData.find(
          (item) => item.id === parseInt(point.index)
        );
        if (pointData) {
          initialColor = getColor(pointData.mean_queue);
        }
      }

      // 创建初始图标
      const icon = createIcon(initialColor);
      const animatedMarker = new T.Marker(new T.LngLat(point.lng, point.lat), {
        icon: icon,
      });

      // 保存点位ID用于后续更新
      animatedMarker.id = parseInt(point.index);

      // 添加点击事件
      animatedMarker.addEventListener("click", () => {
        handlePointClick(point.index);
      });

      map.addOverLay(animatedMarker);
      // 存储标记引用以便后续更新
      markers.push(animatedMarker);
    } catch (error) {
      error(`添加标记点失败: ${point.name}`, error);
    }
  });
}

onMounted(async () => {
  try {
    // 重置状态
    resetState();

    // 创建防抖函数避免短时间内多次请求
    const loadInitialData = () => {
      // 检查是否已加载初始拥堵数据
      if (window.initialCongestionData) {
        return;
      }

      // 立即预加载拥堵数据
      const timestamp = new Date().getTime();
      fetch(`http://127.0.0.1:5500/api/congestion?episode=0&_t=${timestamp}`)
        .then((response) => response.json())
        .then((data) => {
          if (data && data.data && data.data.length > 0) {
            // 保存初始拥堵数据用于地图点初始化
            window.initialCongestionData = data.data;
            log("预加载拥堵数据成功");

            // 如果总集数未设置，更新它
            if (totalEpisodes === 0 && data.total > 0) {
              totalEpisodes = data.total;
            }
          }
        })
        .catch((error) => error("预加载拥堵数据失败:", error));
    };

    // 执行一次初始数据加载
    loadInitialData();

    // 立即加载ECharts
    await loadECharts();

    // 立即加载地图，减少延迟
    loadMapAsync()
      .then(() => {})
      .catch((error) => {
        error("地图加载失败:", error);
      });

    // 监听窗口大小变化
    window.addEventListener("resize", handleResize);
  } catch (error) {
    error("初始化失败:", error);
  }
});

// 重置所有状态
function resetState() {
  // 清除定时器
  if (dataUpdateTimer) {
    clearInterval(dataUpdateTimer);
    dataUpdateTimer = null;
  }

  if (autoPlayTimer) {
    clearInterval(autoPlayTimer);
    autoPlayTimer = null;
  }

  // 重置数据状态
  currentDataIndex = 1;
  fullIntersectionData = null;
  showIntersectionChart.value = false;
  selectedIntersection.value = null;
  trafficLightData.value = null;
  displayedTimeSteps.value = [];
  improvementData.value = null;
  isDataUpdated.value = false;
  isFirstMapClick.value = true;

  // 清除图表实例
  if (intersectionChart) {
    intersectionChart.dispose();
    intersectionChart = null;
  }

  if (rewardChart) {
    rewardChart.dispose();
    rewardChart = null;
  }

  if (queueChart) {
    queueChart.dispose();
    queueChart = null;
  }
}

onBeforeUnmount(() => {
  // 清除自动播放定时器
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer);
    autoPlayTimer = null;
  }

  // 清除数据更新定时器
  if (dataUpdateTimer) {
    clearInterval(dataUpdateTimer);
    dataUpdateTimer = null;
  }

  // 清除拥堵数据定时器
  if (congestionTimer) {
    clearInterval(congestionTimer);
    congestionTimer = null;
  }

  // 删除地图和图表实例
  if (window.bMap) {
    window.bMap = null;
  }

  if (trainingChart) {
    trainingChart.dispose();
    trainingChart = null;
  }

  if (intersectionChart) {
    intersectionChart.dispose();
    intersectionChart = null;
  }

  if (rewardChart) {
    rewardChart.dispose();
    rewardChart = null;
  }

  if (queueChart) {
    queueChart.dispose();
    queueChart = null;
  }

  // 移除事件监听
  window.removeEventListener("resize", handleResize);
});

function loadMapAsync() {
  return new Promise((resolve) => {
    loadMap();
    // 由于initMap是异步的但没有返回Promise，我们这里延迟resolve
    setTimeout(resolve, 1000);
  });
}

// 添加训练指标图表渲染函数
function renderTrainingChart(data) {
  try {
    // 1. 尝试使用全局训练指标数据
    if (data.training_metrics) {
      forceRenderChart("trainingMetricsContainer", data.training_metrics);
      window.cachedTrainingMetrics = data.training_metrics;
      return;
    }

    // 2. 尝试使用第一个路口的训练指标数据
    const intersectionIds = Object.keys(data.intersections || {});
    if (intersectionIds.length > 0) {
      const firstIntersection = data.intersections[intersectionIds[0]];
      if (firstIntersection && firstIntersection.training_metrics) {
        forceRenderChart(
          "trainingMetricsContainer",
          firstIntersection.training_metrics
        );
        window.cachedTrainingMetrics = firstIntersection.training_metrics;
        return;
      }
    }

    // 3. 如果没有数据，不自动请求，只显示默认图表
    log("没有可用的训练指标数据");
    forceRenderChart(
      "trainingMetricsContainer",
      getDefaultChartOption("trainingMetricsContainer")
    );
  } catch (error) {
    error("渲染训练指标图表出错:", error);
    // 显示默认图表
    forceRenderChart(
      "trainingMetricsContainer",
      getDefaultChartOption("trainingMetricsContainer")
    );
  }
}

// 添加新的时间步到显示列表
function addNextTimeStep() {
  if (
    !trafficLightData.value ||
    !trafficLightData.value.time_steps ||
    trafficLightData.value.time_steps.length === 0
  ) {
    return;
  }

  // 修改为循环播放
  if (
    displayedTimeSteps.value.length >= trafficLightData.value.time_steps.length
  ) {
    // 重置为只显示第一个时间步，实现循环播放
    displayedTimeSteps.value = [0];
    log("信号灯状态开始循环播放");
  } else {
    // 添加下一个时间步索引
    displayedTimeSteps.value.push(displayedTimeSteps.value.length);
  }

  // 滚动到底部以查看最新添加的时间步
  nextTick(() => {
    const container = document.querySelector(".traffic-light-container");
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  });
}

// 开始自动播放
function startAutoPlay() {
  // 停止之前可能存在的定时器
  stopAutoPlay();

  // 每5秒添加一个新的时间步
  autoPlayTimer = setInterval(() => {
    addNextTimeStep();
  }, 5000);
}

// 停止自动播放
function stopAutoPlay() {
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer);
    autoPlayTimer = null;
  }
}

// 监听trafficLightData变化，重置显示
watch(trafficLightData, (newVal) => {
  if (newVal && newVal.time_steps && newVal.time_steps.length > 0) {
    // 重置显示列表，只显示第一个时间步
    displayedTimeSteps.value = [0];
    // 开始自动播放
    startAutoPlay();
  } else {
    stopAutoPlay();
    displayedTimeSteps.value = [];
  }
});

// 渲染拆分为两个的图表
function renderSplitCharts(data) {
  try {
    // 确保echarts变量已初始化
    initEchartsVar();

    // 准备奖励图表数据
    const rewardOption = {
      title: {
        text: "",
        textStyle: {
          fontSize: 14,
          fontWeight: "normal",
        },
      },
      tooltip: {
        trigger: "axis",
        formatter: function (params) {
          let result = params[0].axisValue + "<br/>";
          params.forEach((param) => {
            result += param.seriesName + ": " + param.value + "<br/>";
          });
          return result;
        },
      },
      grid: {
        top: 10,
        left: "30",
        right: "15",
        bottom: "50",
        containLabel: true,
      },
      dataZoom: [
        {
          type: "inside",
          start: 0,
          end: 100,
          minValueSpan: 5,
        },
        {
          show: true,
          type: "slider",
          height: 20,
          bottom: 10,
          start: 0,
          end: 100,
          width: "80%",
          left: "10%",
        },
      ],
      xAxis: {
        type: "category",
        boundaryGap: false,
        data: data.xAxis ? [...data.xAxis.data] : [],
        axisLabel: {
          color: "#64748b",
          showMaxLabel: true,
        },
        axisLine: {
          lineStyle: {
            color: "#cbd5e1",
          },
        },
      },
      yAxis: {
        type: "value",
        name: "奖励",
        nameLocation: "end",
        nameTextStyle: {
          padding: [0, 0, 0, 5],
        },
        axisLabel: {
          color: "#64748b",
        },
        axisLine: {
          lineStyle: {
            color: "#cbd5e1",
          },
        },
        splitLine: {
          lineStyle: {
            color: "#e2e8f0",
          },
        },
      },
      series: [
        {
          name: "奖励",
          type: "line",
          data:
            data.series && data.series.length > 0
              ? [...data.series[0].data]
              : [],
          smooth: true,
          symbol: "circle",
          symbolSize: 6,
          sampling: "lttb",
          lineStyle: {
            width: 3,
            color: "#3b82f6", // 蓝色
          },
          itemStyle: {
            color: "#3b82f6",
            borderWidth: 2,
            borderColor: "#ffffff",
          },
          areaStyle: {
            color: {
              type: "linear",
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: "rgba(59, 130, 246, 0.3)" },
                { offset: 1, color: "rgba(59, 130, 246, 0.1)" },
              ],
            },
          },
        },
      ],
    };

    // 准备队列长度图表数据
    const queueOption = {
      title: {
        text: "",
        textStyle: {
          fontSize: 14,
          fontWeight: "normal",
        },
      },
      tooltip: {
        trigger: "axis",
        formatter: function (params) {
          let result = params[0].axisValue + "<br/>";
          params.forEach((param) => {
            result += param.seriesName + ": " + param.value + " 辆车<br/>";
          });
          return result;
        },
      },
      grid: {
        top: 10,
        left: "30",
        right: "15",
        bottom: "50",
        containLabel: true,
      },
      dataZoom: [
        {
          type: "inside",
          start: 0,
          end: 100,
          minValueSpan: 5,
        },
        {
          show: true,
          type: "slider",
          height: 20,
          bottom: 10,
          start: 0,
          end: 100,
          width: "80%",
          left: "10%",
        },
      ],
      xAxis: {
        type: "category",
        boundaryGap: false,
        data: data.xAxis ? [...data.xAxis.data] : [],
        axisLabel: {
          color: "#64748b",
          showMaxLabel: true,
        },
        axisLine: {
          lineStyle: {
            color: "#cbd5e1",
          },
        },
      },
      yAxis: {
        type: "value",
        name: "队列长度",
        nameLocation: "end",
        nameTextStyle: {
          padding: [0, 0, 0, 5],
        },
        minInterval: 1,
        axisLabel: {
          color: "#64748b",
        },
        axisLine: {
          lineStyle: {
            color: "#cbd5e1",
          },
        },
        splitLine: {
          lineStyle: {
            color: "#e2e8f0",
          },
        },
      },
      series: [
        {
          name: "队列长度",
          type: "line",
          data:
            data.series && data.series.length > 1
              ? [...data.series[1].data]
              : [],
          smooth: true,
          symbol: "circle",
          symbolSize: 6,
          sampling: "lttb",
          lineStyle: {
            width: 3,
            color: "#f97316",
          },
          itemStyle: {
            color: "#f97316",
            borderWidth: 2,
            borderColor: "#ffffff",
          },
          areaStyle: {
            color: {
              type: "linear",
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: "rgba(249, 115, 22, 0.3)" },
                { offset: 1, color: "rgba(249, 115, 22, 0.1)" },
              ],
            },
          },
        },
      ],
    };

    // 渲染奖励图表
    if (rewardChart) {
      rewardChart.dispose();
    }
    rewardChart = echarts.init(document.getElementById("rewardContainer"));
    rewardChart.setOption(rewardOption);

    // 渲染队列长度图表
    if (queueChart) {
      queueChart.dispose();
    }
    queueChart = echarts.init(document.getElementById("queueContainer"));
    queueChart.setOption(queueOption);
  } catch (error) {
    console.error("渲染拆分图表出错:", error);
  }
}
</script>

<style scoped>
.dashboard-container {
  width: 100%;
  min-height: 100vh;
  padding: 20px;
  background-color: #f5f7fa;
}

.chart-wrapper {
  width: 100%;
  height: calc(100vh - 40px);
}

.content {
  width: 100%;
  height: 100%;
  display: flex;
  margin: 0 auto;
}

.row-layout {
  flex-direction: row;
  gap: 24px;
  width: 100%;
}

/* 左侧图表容器 */
.charts-container {
  width: 50%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 卡片样式 */
.card {
  background-color: #fff;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  border: 1px solid #e2e8f0;
  padding: 1.5rem;
  transition: all 0.3s ease-in-out;
}

.card-float:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(37, 99, 235, 0.1);
  border-color: #3b82f6;
}

/* 调整左侧卡片高度比例 */
.card-improvement {
  flex: 1;
  min-height: 150px;
  position: relative;
}

.card-intersection {
  flex: 3;
  min-height: 400px;
  position: relative;
  padding-bottom: 0.5rem;
}

.card-traffic-light {
  flex: 2;
  min-height: 300px;
  position: relative;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0.8rem;
  margin-bottom: 1.2rem;
  border-bottom: 1px solid #dbeafe;
  width: 100%;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1d4ed8;
}

.card-badge {
  background-color: #dbeafe;
  color: #2563eb;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

/* 右侧地图卡片 */
.map-corner {
  width: 50%;
  height: 100%;
}

/* 图表容器样式 */
.chart-container {
  flex: 1;
  width: 100%;
  height: calc(100% - 70px);
  min-height: 320px;
  display: block;
  position: relative;
  visibility: visible;
  z-index: 5;
}

/* 地图容器样式 */
.map-container {
  flex: 1;
  position: relative;
  width: 100%;
  height: calc(100% - 70px);
  border-radius: 10px;
  overflow: hidden;
  background-color: #f8fafc;
  z-index: 1;
}

#map {
  width: 100%;
  height: 100%;
  z-index: 1;
}

.error-message {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 20px;
  background-color: rgba(245, 108, 108, 0.1);
  border: 1px solid #f56c6c;
  border-radius: 8px;
  color: #f56c6c;
  font-size: 16px;
  z-index: 20;
}

/* 提示卡片样式 */
.hint-content {
  text-align: center;
  color: #909399;
  font-size: 16px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
  padding: 20px;
}

.hint-content i {
  margin-right: 5px;
  font-size: 18px;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .content {
    flex-direction: column;
  }

  .charts-container,
  .map-corner {
    width: 100%;
    margin: 0;
    padding: 0;
  }

  .charts-container {
    display: flex;
    flex-direction: row;
    margin-bottom: 15px;
    height: auto;
    gap: 15px;
  }

  .charts-container .card {
    height: 500px;
  }

  .map-corner {
    height: 500px;
  }
}

@media (max-width: 768px) {
  .charts-container {
    flex-direction: column;
  }
}

/* 信号灯相关样式 - 新增 */
.traffic-light-container {
  padding: 8px;
  overflow-y: auto;
  max-height: 520px;
  scroll-behavior: smooth;
  overscroll-behavior: contain;
  border-radius: 10px;
  background-color: #f8fafc;
  height: calc(100% - 50px);
}

.time-step {
  margin-bottom: 8px;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.time-step-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-weight: bold;
}

.time-badge {
  background-color: #1989fa;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
}

.phase-badge {
  background-color: #67c23a;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
}

.connections {
  margin-top: 6px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

@media (min-width: 992px) {
  .connections {
    grid-template-columns: 1fr 1fr 1fr;
  }
}

.connection {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px;
  background-color: #f9f9f9;
  border-radius: 6px;
  margin-bottom: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: background-color 0.2s;
}

.connection:hover {
  background-color: #f0f0f0;
}

.connection-description {
  font-size: 0.85em;
  margin-right: 2px;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.connection-states {
  display: flex;
  flex-shrink: 0;
}

.state-box {
  display: inline-block;
  width: 16px;
  height: 16px;
  margin-right: 2px;
  border-radius: 3px;
  transition: transform 0.2s;
}

.state-box:hover {
  transform: scale(1.2);
}

.state-green {
  background-color: #67c23a;
}

.state-red {
  background-color: #f56c6c;
}

.state-yellow {
  background-color: #e6a23c;
}

.latest-step {
  animation: highlight 2s ease-in-out;
}

@keyframes highlight {
  0% {
    background-color: rgba(103, 194, 58, 0.1);
  }
  100% {
    background-color: transparent;
  }
}

/* 调控效果数据样式 */
.improvement-data-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 15px;
  height: calc(100% - 60px);
}

/* 统计数据摘要样式 */
.stats-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  padding: 0.2rem 0;
}

.stats-row {
  display: flex;
  gap: 12px;
}

.stat-box {
  flex: 1;
  background-color: #f1f5f9;
  border-radius: 10px;
  padding: 12px;
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid #e2e8f0;
}

.stat-box:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border-color: #3b82f6;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 4px;
  transition: all 0.5s ease;
}

.stat-label {
  font-size: 0.85rem;
  color: #64748b;
}

/* 数据更新动画 */
@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.data-updated {
  animation: pulse 0.5s ease;
}

/* 保留拥堵和延迟减少的颜色样式 */
.improvement-positive {
  color: #67c23a;
}

.improvement-positive-high {
  color: #67c23a;
  font-weight: 800;
}

.improvement-negative {
  color: #f56c6c;
}

.improvement-negative-high {
  color: #f56c6c;
  font-weight: 800;
}

.improvement-neutral {
  color: #909399;
}

/* 地图图例样式 */
.map-legend {
  position: absolute;
  top: 20px;
  right: 20px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 6px;
  padding: 10px 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 500;
  font-size: 13px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.legend-title {
  font-weight: bold;
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
}

.legend-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  margin-right: 10px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.legend-green {
  border: 2px solid #4caf50;
}

.legend-green::after {
  content: "";
  width: 8px;
  height: 8px;
  background-color: #4caf50;
  border-radius: 50%;
}

.legend-yellow {
  border: 2px solid #ff9800;
}

.legend-yellow::after {
  content: "";
  width: 8px;
  height: 8px;
  background-color: #ff9800;
  border-radius: 50%;
}

.legend-red {
  border: 2px solid #f44336;
}

.legend-red::after {
  content: "";
  width: 8px;
  height: 8px;
  background-color: #f44336;
  border-radius: 50%;
}

.legend-text {
  color: #333;
  font-size: 13px;
}

.charts-wrapper {
  display: flex;
  flex-direction: row;
  gap: 15px;
  height: calc(100% - 70px);
  padding-bottom: 10px;
  flex-wrap: wrap;
}

.chart-container-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 240px;
  min-width: 300px;
  width: calc(50% - 15px);
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: #1d4ed8;
  margin-bottom: 5px;
  padding-left: 5px;
  border-left: 3px solid #3b82f6;
}

.charts-wrapper .chart-container {
  flex: 1;
  width: 100%;
  position: relative;
  min-height: 220px;
}

/* 大屏幕字体放大 */
@media (min-width: 1800px) {
  .card-title {
    font-size: 1.4rem;
  }

  .card-badge {
    font-size: 0.95rem;
    padding: 0.3rem 0.85rem;
  }

  .stat-value {
    font-size: 1.8rem;
  }

  .stat-label {
    font-size: 1.1rem;
  }

  .chart-title {
    font-size: 18px;
  }

  .hint-content {
    font-size: 18px;
  }

  .time-badge,
  .phase-badge {
    font-size: 14px;
    padding: 3px 10px;
  }

  .connection-description {
    font-size: 1rem;
  }

  .state-box {
    width: 20px;
    height: 20px;
  }

  .map-legend {
    font-size: 15px;
    padding: 12px 18px;
  }

  .legend-title {
    font-size: 16px;
  }

  .legend-text {
    font-size: 15px;
  }

  .legend-icon {
    width: 24px;
    height: 24px;
  }

  .legend-green::after,
  .legend-yellow::after,
  .legend-red::after {
    width: 10px;
    height: 10px;
  }
}

/* 超大屏幕字体放大 */
@media (min-width: 2400px) {
  .card-title {
    font-size: 1.7rem;
  }

  .card-badge {
    font-size: 1.1rem;
    padding: 0.4rem 1rem;
  }

  .stat-value {
    font-size: 2.2rem;
  }

  .stat-label {
    font-size: 1.3rem;
  }

  .chart-title {
    font-size: 22px;
  }

  .hint-content {
    font-size: 20px;
  }

  .time-badge,
  .phase-badge {
    font-size: 16px;
    padding: 4px 12px;
  }

  .connection-description {
    font-size: 1.15rem;
  }

  .state-box {
    width: 24px;
    height: 24px;
  }

  .map-legend {
    font-size: 18px;
    padding: 15px 22px;
  }

  .legend-title {
    font-size: 20px;
  }

  .legend-text {
    font-size: 18px;
  }

  .legend-icon {
    width: 28px;
    height: 28px;
  }

  .legend-green::after,
  .legend-yellow::after,
  .legend-red::after {
    width: 12px;
    height: 12px;
  }
}
</style>

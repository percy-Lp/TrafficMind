<template>
  <div class="card card-float card-stats">
    <div class="card-header">
      <div class="card-title">数据统计</div>
      <div class="card-badge">📊 实时数据</div>
    </div>

    <!-- 添加统计数据摘要区域 -->
    <div class="stats-container">
      <!-- 统计数据摘要区域 -->
      <div class="stats-summary">
        <div class="stats-row">
          <div class="stat-box">
            <div class="stat-value">
              {{ stats.total_vehicles || 0 }}
            </div>
            <div class="stat-label">总车辆数</div>
          </div>
          <div class="stat-box">
            <div class="stat-value">{{ stats.lane_types || 0 }}</div>
            <div class="stat-label">检测到车道</div>
          </div>
        </div>
        <div class="stats-row">
          <div class="stat-box efficiency">
            <div class="stat-value">
              {{ efficiencyData.trafficEfficiencyImprovement.toFixed(1) }}%
            </div>
            <div class="stat-label">通行效率提升</div>
          </div>
          <div class="stat-box waiting-time">
            <div class="stat-value">
              {{ efficiencyData.waitingTimeReduction.toFixed(1) }}%
            </div>
            <div class="stat-label">等待时间减少</div>
          </div>
        </div>
      </div>

      <!-- 折线图展示区域 -->
      <div class="stats-chart-container">
        <div class="chart-title">车辆数量趋势</div>
        <div ref="chartRef" class="stats-chart"></div>
      </div>

      <!-- 交通流量-容量比分布图 -->
      <div class="stats-chart-container">
        <div class="chart-title">交通流量-容量比分布</div>
        <div ref="flowCapacityChartRef" class="stats-chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";
import * as echarts from "echarts";

const props = defineProps({
  stats: {
    type: Object,
    default: () => ({
      total_vehicles: 0,
      lane_types: 0,
      lane_stats: {
        left_turn: 0,
        others: 0,
      },
    }),
  },
  isDetecting: {
    type: Boolean,
    default: false,
  },
  efficiencyData: {
    type: Object,
    default: () => ({
      trafficEfficiencyImprovement: 0,
      waitingTimeReduction: 0,
    }),
  },
});

// 图表实例引用
const chartRef = ref<HTMLElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

// 交通流量-容量比图表引用
const flowCapacityChartRef = ref<HTMLElement | null>(null);
let flowCapacityChartInstance: echarts.ECharts | null = null;

// 图表数据
const chartData = ref<{
  // 时间点（秒）
  times: number[];
  // 左转车道车辆数
  leftTurnValues: number[];
  // 其他车道车辆数
  otherValues: number[];
}>({
  times: [],
  leftTurnValues: [],
  otherValues: [],
});

// 新增：交通流量-容量比图表数据
const flowCapacityData = ref<{
  times: number[];
  ratioValues: number[];
}>({
  times: [],
  ratioValues: [],
});

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return;

  // 创建图表实例
  chartInstance = echarts.init(chartRef.value);

  // 设置图表选项
  const option = {
    grid: {
      top: 10,
      right: 5,
      bottom: 50,
      left: 30,
      containLabel: true,
    },
    tooltip: {
      trigger: "axis",
      formatter: function (params) {
        let result = params[0].axisValue + "秒<br/>";
        params.forEach((param) => {
          result += param.seriesName + ": " + param.value + "辆车<br/>";
        });
        return result;
      },
    },
    legend: {
      data: ["左转车道", "其他车道"],
      bottom: 0,
      textStyle: {
        color: "#64748b",
      },
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
        bottom: 30,
        start: 0,
        end: 100,
        width: "80%",
        left: "10%",
      },
    ],
    xAxis: {
      type: "category",
      name: "时间(秒)",
      nameLocation: "end",
      data: chartData.value.times,
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
      name: "车辆数",
      nameLocation: "end",
      nameTextStyle: {
        padding: [0, 0, 0, 5],
      },
      minInterval: 1,
      axisLabel: {
        color: "#64748b",
        show: props.isDetecting,
      },
      axisLine: {
        lineStyle: {
          color: "#cbd5e1",
        },
        show: props.isDetecting,
      },
      splitLine: {
        lineStyle: {
          color: "#e2e8f0",
        },
        show: props.isDetecting,
      },
    },
    series: [
      {
        name: "左转车道",
        data: chartData.value.leftTurnValues,
        type: "line",
        smooth: true,
        symbol: "circle",
        symbolSize: 6,
        sampling: "lttb",
        lineStyle: {
          width: 3,
          color: "#3b82f6",
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
      {
        name: "其他车道",
        data: chartData.value.otherValues,
        type: "line",
        smooth: true,
        symbol: "circle",
        symbolSize: 6,
        sampling: "lttb",
        lineStyle: {
          width: 3,
          color: "#10b981",
        },
        itemStyle: {
          color: "#10b981",
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
              { offset: 0, color: "rgba(16, 185, 129, 0.3)" },
              { offset: 1, color: "rgba(16, 185, 129, 0.1)" },
            ],
          },
        },
      },
    ],
  };

  // 应用选项
  chartInstance.setOption(option);

  // 手动触发一次resize以适应容器
  setTimeout(() => {
    chartInstance?.resize();
  }, 200);
};

// 初始化交通流量-容量比图表
const initFlowCapacityChart = () => {
  if (!flowCapacityChartRef.value) return;

  // 创建图表实例
  flowCapacityChartInstance = echarts.init(flowCapacityChartRef.value);

  // 设置图表选项
  const option = {
    grid: {
      top: 10,
      right: 5,
      bottom: 50,
      left: 30,
      containLabel: true,
    },
    tooltip: {
      trigger: "axis",
      formatter: function (params) {
        const value = params[0].value;
        let status = "";
        let color = "";

        if (value <= 0.3) {
          status = "空闲";
          color = "#10b981"; // 绿色
        } else if (value <= 0.7) {
          status = "正常";
          color = "#f59e0b"; // 黄色
        } else {
          status = "拥堵";
          color = "#ef4444"; // 红色
        }

        let result = params[0].axisValue + "秒<br/>";
        result += `<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:${color};"></span>`;
        result +=
          params[0].seriesName +
          ": " +
          params[0].value.toFixed(2) +
          ` <span style="color:${color};font-weight:bold;">(${status})</span><br/>`;
        return result;
      },
    },
    legend: {
      show: false,
      data: ["流量-容量比"],
      bottom: 0,
      textStyle: {
        color: "#64748b",
      },
      formatter: function () {
        return "";
      },
      selectedMode: false,
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
        bottom: 30,
        start: 0,
        end: 100,
        width: "80%",
        left: "10%",
      },
    ],
    xAxis: {
      type: "category",
      name: "时间(秒)",
      nameLocation: "end",
      data: flowCapacityData.value.times,
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
      name: "流量-容量比",
      nameLocation: "end",
      nameTextStyle: {
        padding: [0, 0, 0, 5],
      },
      min: 0,
      max: 1,
      axisLabel: {
        color: "#64748b",
        formatter: "{value}",
        show: props.isDetecting,
      },
      axisLine: {
        lineStyle: {
          color: "#cbd5e1",
        },
        show: props.isDetecting,
      },
      splitLine: {
        lineStyle: {
          color: "#e2e8f0",
        },
        show: props.isDetecting,
      },
    },
    visualMap: {
      show: true,
      type: "piecewise",
      showLabel: true,
      itemWidth: 15,
      itemHeight: 15,
      bottom: 0,
      orient: "horizontal",
      left: "center",
      pieces: [
        {
          gt: 0.7,
          lte: 1.0,
          color: "#ef4444",
          label: "拥堵",
        },
        {
          gt: 0.3,
          lte: 0.7,
          color: "#f59e0b",
          label: "正常",
        },
        {
          gt: 0,
          lte: 0.3,
          color: "#10b981",
          label: "空闲",
        },
      ],
      textStyle: {
        color: "#64748b",
      },
      outOfRange: {
        color: "#999",
      },
    },
    series: [
      {
        name: "流量-容量比",
        data: flowCapacityData.value.ratioValues,
        type: "line",
        smooth: true,
        symbol: "circle",
        symbolSize: 6,
        sampling: "lttb",
        lineStyle: {
          width: 3,
        },
        itemStyle: {
          borderWidth: 2,
          borderColor: "#ffffff",
        },
        areaStyle: {
          opacity: 0.3,
        },
      },
    ],
  };

  // 应用选项
  flowCapacityChartInstance.setOption(option);

  // 手动触发一次resize以适应容器
  setTimeout(() => {
    flowCapacityChartInstance?.resize();
  }, 200);
};

// 添加新数据点
const addDataPoint = () => {
  // 如果未在检测状态，则不更新图表
  if (!props.isDetecting) {
    console.log("不在检测状态，跳过数据更新");
    return;
  }

  // 获取当前时间点（从开始记录的秒数）
  const currentTime = chartData.value.times.length;

  // 获取左转车道和其他车道的车辆数
  const leftTurn = props.stats.lane_stats?.left_turn || 0;
  const others = props.stats.lane_stats?.others || 0;

  console.log(
    `添加数据点: 时间=${currentTime}, 左转车道=${leftTurn}, 其他车道=${others}`
  );

  // 添加数据点
  chartData.value.times.push(currentTime);
  chartData.value.leftTurnValues.push(leftTurn);
  chartData.value.otherValues.push(others);

  // 更新图表
  if (chartInstance) {
    // 获取当前的dataZoom状态
    const dataZoomOption = chartInstance.getOption().dataZoom;
    const isAutoScrolling =
      dataZoomOption &&
      Array.isArray(dataZoomOption) &&
      dataZoomOption[0].end === 100;

    // 更新图表数据
    chartInstance.setOption({
      xAxis: {
        data: chartData.value.times,
      },
      series: [
        {
          data: chartData.value.leftTurnValues,
        },
        {
          data: chartData.value.otherValues,
        },
      ],
    });

    // 如果用户没有手动调整缩放，则自动滚动以显示最新的数据点
    if (isAutoScrolling && chartData.value.times.length > 10) {
      chartInstance.setOption({
        dataZoom: [
          {
            start: Math.max(0, 100 - 1000 / chartData.value.times.length),
            end: 100,
          },
          {
            start: Math.max(0, 100 - 1000 / chartData.value.times.length),
            end: 100,
          },
        ],
      });
    }
  }

  // 计算并更新交通流量-容量比图表
  const totalVehicles = leftTurn + others;
  const maxCapacity = 16;
  const flowCapacityRatio = totalVehicles / maxCapacity;

  // 添加流量-容量比数据点
  flowCapacityData.value.times.push(currentTime);
  flowCapacityData.value.ratioValues.push(flowCapacityRatio);

  // 更新流量-容量比图表
  if (flowCapacityChartInstance) {
    // 获取当前的dataZoom状态
    const dataZoomOption = flowCapacityChartInstance.getOption().dataZoom;
    const isAutoScrolling =
      dataZoomOption &&
      Array.isArray(dataZoomOption) &&
      dataZoomOption[0].end === 100;

    // 更新图表数据
    flowCapacityChartInstance.setOption({
      xAxis: {
        data: flowCapacityData.value.times,
      },
      series: [
        {
          data: flowCapacityData.value.ratioValues,
        },
      ],
    });

    // 如果用户没有手动调整缩放，则自动滚动以显示最新的数据点
    if (isAutoScrolling && flowCapacityData.value.times.length > 10) {
      flowCapacityChartInstance.setOption({
        dataZoom: [
          {
            start: Math.max(
              0,
              100 - 1000 / flowCapacityData.value.times.length
            ),
            end: 100,
          },
          {
            start: Math.max(
              0,
              100 - 1000 / flowCapacityData.value.times.length
            ),
            end: 100,
          },
        ],
      });
    }
  }
};

// 定时器记录
let timer: number | null = null;
let isDetectingPrev = false;

// 监听检测状态变化
watch(
  () => props.isDetecting,
  (newValue, oldValue) => {
    // 记录状态变化
    console.log(`检测状态变化: ${oldValue} -> ${newValue}`);

    // 更新图表的y轴显示状态
    if (chartInstance) {
      chartInstance.setOption({
        yAxis: {
          axisLabel: { show: newValue },
          axisLine: { show: newValue },
          splitLine: { show: newValue },
        },
      });
    }

    if (flowCapacityChartInstance) {
      flowCapacityChartInstance.setOption({
        yAxis: {
          axisLabel: { show: newValue },
          axisLine: { show: newValue },
          splitLine: { show: newValue },
        },
      });
    }

    // 如果状态从true变为false，则表示停止检测
    if (oldValue === true && newValue === false) {
      console.log("停止检测，停止定时器并添加结束标记");

      // 确保定时器被清除
      if (timer !== null) {
        clearInterval(timer);
        timer = null;
      }

      // 添加视频结束标记到车辆数量趋势图
      if (chartInstance && chartData.value.times.length > 0) {
        const lastTimeIndex =
          chartData.value.times[chartData.value.times.length - 1];

        chartInstance.setOption({
          series: [
            {
              markLine: {
                silent: true,
                symbol: ["none", "none"],
                label: {
                  formatter: "视频结束",
                  position: "insideEndTop",
                  fontSize: 14,
                  fontWeight: "bold",
                  color: "#ff4d4f",
                },
                lineStyle: {
                  color: "#ff4d4f",
                  width: 2,
                  type: "dashed",
                },
                data: [{ xAxis: lastTimeIndex }],
              },
            },
          ],
        });
      }

      // 添加视频结束标记到流量-容量比图表
      if (
        flowCapacityChartInstance &&
        flowCapacityData.value.times.length > 0
      ) {
        const lastTimeIndex =
          flowCapacityData.value.times[flowCapacityData.value.times.length - 1];

        flowCapacityChartInstance.setOption({
          series: [
            {
              markLine: {
                silent: true,
                symbol: ["none", "none"],
                label: {
                  formatter: "视频结束",
                  position: "insideEndTop",
                  fontSize: 14,
                  fontWeight: "bold",
                  color: "#ff4d4f",
                },
                lineStyle: {
                  color: "#ff4d4f",
                  width: 2,
                  type: "dashed",
                },
                data: [{ xAxis: lastTimeIndex }],
              },
            },
          ],
        });
      }
    }
    // 如果状态从false变为true，则表示开始或重新开始检测
    else if (oldValue === false && newValue === true) {
      console.log("开始/重新开始检测，清除结束标记并启动定时器");

      // 清除之前的视频结束标记 (不清空数据)
      if (chartInstance) {
        chartInstance.setOption({
          series: [
            {
              markLine: {
                data: [],
              },
            },
          ],
        });
      }

      // 清除流量-容量比图表的结束标记
      if (flowCapacityChartInstance) {
        flowCapacityChartInstance.setOption({
          series: [
            {
              markLine: {
                data: [],
              },
            },
          ],
        });
      }

      // 确保之前的定时器被清除
      if (timer !== null) {
        clearInterval(timer);
        timer = null;
      }

      // 启动新的定时器
      timer = window.setInterval(() => {
        console.log("定时器触发，当前检测状态:", props.isDetecting);
        if (props.isDetecting) {
          addDataPoint();
        } else {
          console.log("检测已停止，清除定时器");
          if (timer !== null) {
            clearInterval(timer);
            timer = null;
          }
        }
      }, 1000);
    }

    // 更新上一次状态
    isDetectingPrev = newValue;
  },
  { immediate: true }
);

watch(
  () => props.stats,
  (newStats, oldStats) => {
    // 当数据变化时，如果在检测状态下且图表已初始化，则更新图表
    if (props.isDetecting && chartInstance && newStats !== oldStats) {
      // 不在此处添加数据点，而是让定时器控制更新频率
    }
  },
  { deep: true }
);

// 组件挂载时
onMounted(() => {
  console.log("组件挂载，初始化图表");
  initChart();
  initFlowCapacityChart();

  // 添加窗口大小变化监听器
  window.addEventListener("resize", handleResize);

  if (props.isDetecting) {
    // 如果初始状态就是正在检测，则启动定时器
    startDataUpdateTimer();
  }
});

// 组件卸载时
onUnmounted(() => {
  // 组件卸载时释放资源
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }

  if (flowCapacityChartInstance) {
    flowCapacityChartInstance.dispose();
    flowCapacityChartInstance = null;
  }

  // 清除定时器
  if (timer !== null) {
    clearInterval(timer);
    timer = null;
  }

  // 移除窗口大小变化监听器
  window.removeEventListener("resize", handleResize);
});

// 处理窗口大小变化
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize();
  }
  if (flowCapacityChartInstance) {
    flowCapacityChartInstance.resize();
  }
};
</script>

<style scoped>
.card {
  padding: 1.2rem;
  border-radius: 14px;
  background-color: #ffffff;
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease-in-out;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
}

.card-float:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(37, 99, 235, 0.1);
  border-color: #3b82f6;
}

.card-stats {
  width: calc(25% - 24px);
  height: calc(100% - 40px);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease-in-out;
  margin: 20px 0 20px 20px;
}

/* 卡片头部样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0.8rem;
  margin-bottom: 1.2rem;
  border-bottom: 1px solid #dbeafe;
  flex-shrink: 0;
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

/* 统计数据容器样式 */
.stats-container {
  display: flex;
  flex-direction: column;
  margin: 0;
  justify-content: flex-start;
  gap: 8px;
  height: calc(100% - 50px);
  overflow-y: auto;
}

/* 统计数据摘要区域样式 */
.stats-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 0.8rem;
  padding: 0.2rem 0;
  flex-shrink: 0;
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
}

.stat-label {
  font-size: 0.85rem;
  color: #64748b;
}

.stat-box.left-turn .stat-value {
  color: #3b82f6;
}

.stat-box.others .stat-value {
  color: #10b981;
}

.stat-box.efficiency .stat-value {
  color: #3b82f6;
}

.stat-box.waiting-time .stat-value {
  color: #10b981;
}

/* 折线图容器样式 */
.stats-chart-container {
  background-color: #f1f5f9;
  border-radius: 10px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  width: 100%;
  margin-bottom: 12px;
  flex: 1;
  min-height: 250px;
}

.chart-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 8px;
  text-align: center;
  flex-shrink: 0;
}

.stats-chart {
  width: 100%;
  height: calc(100% - 30px);
  min-height: 220px;
}

/* 媒体查询 */
@media (max-width: 1200px) {
  .card-stats {
    width: 100%;
    height: auto;
  }

  .stats-chart-container {
    width: 100%;
    min-height: 300px;
  }

  .stats-summary {
    flex-direction: column;
  }

  .stats-row {
    flex-direction: row;
  }
}

@media (max-width: 768px) {
  .stats-row {
    flex-direction: row;
  }

  .stat-box {
    padding: 8px;
  }

  .stat-value {
    font-size: 1.3rem;
  }

  .stat-label {
    font-size: 0.8rem;
  }

  .stats-chart-container {
    min-height: 250px;
  }
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

  .overlay-text {
    font-size: 18px;
  }

  .status-text {
    font-size: 16px;
  }
}

/* 超大屏幕放大 */
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

  .overlay-text {
    font-size: 20px;
  }

  .status-text {
    font-size: 18px;
  }
}
</style>

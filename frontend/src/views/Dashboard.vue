<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon dianping">
              <el-icon :size="32"><ChatDotRound /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total || 0 }}</div>
              <div class="stat-label">总评论数</div>
              <div class="stat-trend positive">
                <el-icon><Top /></el-icon>
                <span>较上周 +12%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon meituan">
              <el-icon :size="32"><Star /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.avg_rating || 0 }}</div>
              <div class="stat-label">平均评分</div>
              <div class="stat-trend positive">
                <el-icon><Top /></el-icon>
                <span>较上周 +0.2</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon eleme">
              <el-icon :size="32"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.unreplied_count || 0 }}</div>
              <div class="stat-label">待回复</div>
              <div class="stat-trend negative" v-if="stats.unreplied_count > 5">
                <el-icon><Bottom /></el-icon>
                <span>需及时处理</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon warning">
              <el-icon :size="32"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.negative_count || 0 }}</div>
              <div class="stat-label">差评数</div>
              <div class="stat-trend" :class="stats.negative_count > 0 ? 'negative' : 'positive'">
                <el-icon v-if="stats.negative_count > 0"><Bottom /></el-icon>
                <el-icon v-else><Top /></el-icon>
                <span v-if="stats.negative_count > 0">需关注</span>
                <span v-else>无差评</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="16" style="margin-top: 20px">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon class="header-icon"><TrendCharts /></el-icon>
                <span class="header-title">评分趋势</span>
              </div>
              <el-radio-group v-model="trendDays" size="small" @change="loadTrendData">
                <el-radio-button label="7">7 天</el-radio-button>
                <el-radio-button label="30">30 天</el-radio-button>
                <el-radio-button label="90">90 天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChart" style="height: 320px"></div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-icon class="header-icon"><PieChart /></el-icon>
                <span class="header-title">情感分布</span>
              </div>
            </div>
          </template>
          <div ref="pieChart" style="height: 320px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 待回复评论 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="header-icon"><ChatDotRound /></el-icon>
            <span class="header-title">待回复评论</span>
          </div>
          <el-button type="primary" size="small" @click="$router.push('/reviews')">
            查看全部
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>

      <el-table :data="unrepliedReviews" style="width: 100%" :row-style="{ height: '60px' }">
        <el-table-column prop="rating" label="评分" width="80">
          <template #default="{ row }">
            <div class="rating-display">
              <el-tag :type="row.rating >= 4 ? 'success' : row.rating >= 3 ? 'warning' : 'danger'" size="small" round>
                {{ row.rating }}星
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="platform" label="平台" width="100">
          <template #default="{ row }">
            <el-tag size="small" v-if="row.platform === 'dianping'">大众点评</el-tag>
            <el-tag size="small" type="warning" v-else-if="row.platform === 'meituan'">美团</el-tag>
            <el-tag size="small" type="danger" v-else-if="row.platform === 'eleme'">饿了么</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user_name" label="用户" width="120" />
        <el-table-column prop="content" label="评论内容" show-overflow-tooltip />
        <el-table-column prop="review_time" label="时间" width="160" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" round @click="handleReply(row)">
              回复
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import request from '@/utils/request'

const stats = ref({
  total: 1280,
  avg_rating: 4.6,
  unreplied_count: 3,
  negative_count: 2
})

const unrepliedReviews = ref([
  {
    id: 1,
    rating: 5,
    platform: 'dianping',
    user_name: '张***3',
    content: '菜品很好吃，服务也很到位，环境不错，下次还会再来！',
    review_time: '2026-03-18 10:30'
  },
  {
    id: 2,
    rating: 4,
    platform: 'meituan',
    user_name: '李***8',
    content: '味道不错，就是上菜有点慢，其他都挺好的',
    review_time: '2026-03-18 09:15'
  },
  {
    id: 3,
    rating: 3,
    platform: 'eleme',
    user_name: '王***5',
    content: '一般般吧，没有想象中好吃，价格有点贵',
    review_time: '2026-03-17 20:45'
  }
])

const trendDays = ref('30')
const trendChart = ref(null)
const pieChart = ref(null)

// 加载趋势数据
const loadTrendData = async () => {
  try {
    // 模拟数据（实际应从 API 获取）
    const mockData = []
    const days = parseInt(trendDays.value)
    const baseDate = new Date()
    
    for (let i = days; i >= 0; i--) {
      const date = new Date(baseDate)
      date.setDate(date.getDate() - i)
      mockData.push({
        date: `${date.getMonth() + 1}/${date.getDate()}`,
        avg_rating: 4.5 + Math.random() * 0.3
      })
    }
    
    renderTrendChart(mockData)
  } catch (error) {
    console.error('加载趋势数据失败:', error)
  }
}

// 渲染趋势图
const renderTrendChart = (data) => {
  if (!trendChart.value) return
  
  const chart = echarts.init(trendChart.value)
  const dates = data.map(item => item.date)
  const ratings = data.map(item => item.avg_rating.toFixed(1))
  
  chart.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e8e8e8',
      textStyle: { color: '#333' },
      formatter: '{b}<br/>评分：{c}星'
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#e8e8e8' } },
      axisLabel: { color: '#666' }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 5,
      splitLine: { lineStyle: { color: '#f0f0f0', type: 'dashed' } },
      axisLabel: { color: '#666' }
    },
    series: [{
      name: '平均评分',
      type: 'line',
      smooth: true,
      data: ratings,
      symbol: 'circle',
      symbolSize: 8,
      itemStyle: {
        color: '#FF6600',
        borderWidth: 2,
        borderColor: '#fff'
      },
      lineStyle: {
        color: '#FF6600',
        width: 3
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(255, 102, 0, 0.3)' },
          { offset: 1, color: 'rgba(255, 102, 0, 0.01)' }
        ])
      }
    }]
  })
}

// 渲染饼图
const renderPieChart = (statsData) => {
  if (!pieChart.value) return
  
  const chart = echarts.init(pieChart.value)
  
  chart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e8e8e8',
      textStyle: { color: '#333' }
    },
    legend: {
      bottom: '5%',
      left: 'center',
      textStyle: { color: '#666' }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: true,
        formatter: '{b}\n{d}%',
        color: '#333'
      },
      data: [
        { value: 856, name: '好评', itemStyle: { color: '#66C23A' } },
        { value: 320, name: '中评', itemStyle: { color: '#E6A23C' } },
        { value: 104, name: '差评', itemStyle: { color: '#F56C6C' } }
      ]
    }]
  })
}

// 回复评论
const handleReply = (row) => {
  console.log('回复评论:', row)
}

onMounted(() => {
  loadTrendData()
  renderPieChart({})
  
  window.addEventListener('resize', () => {
    trendChart.value && echarts.getInstanceByDom(trendChart.value)?.resize()
    pieChart.value && echarts.getInstanceByDom(pieChart.value)?.resize()
  })
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 12px;
  border: none;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.stat-icon.dianping {
  background: linear-gradient(135deg, #FF9068 0%, #FF6600 100%);
}

.stat-icon.meituan {
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
}

.stat-icon.eleme {
  background: linear-gradient(135deg, #66C23A 0%, #4CAF50 100%);
}

.stat-icon.warning {
  background: linear-gradient(135deg, #F56C6C 0%, #E74C3C 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #333;
  line-height: 1;
  margin-bottom: 6px;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-bottom: 6px;
}

.stat-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-trend.positive {
  color: #66C23A;
}

.stat-trend.negative {
  color: #F56C6C;
}

.chart-card {
  border-radius: 12px;
  border: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  font-size: 18px;
  color: #FF6600;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.rating-display {
  display: flex;
  justify-content: center;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  background: #fafafa;
  color: #666;
  font-weight: 500;
}

:deep(.el-tag) {
  font-weight: 500;
}
</style>

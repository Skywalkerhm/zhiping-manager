<template>
  <div class="analytics">
    <el-row :gutter="20">
      <!-- 评分趋势 -->
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>评分趋势</span>
              <el-radio-group v-model="trendDays" size="small" @change="loadTrendData">
                <el-radio-button label="7">7 天</el-radio-button>
                <el-radio-button label="30">30 天</el-radio-button>
                <el-radio-button label="90">90 天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChart" style="height: 350px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 关键词云 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>好评关键词</span>
            </div>
          </template>
          <div ref="wordCloud" style="height: 300px"></div>
        </el-card>
      </el-col>

      <!-- 主题分布 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>评论主题分布</span>
            </div>
          </template>
          <div ref="topicChart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 竞品分析 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>竞品分析</span>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="我的评分">
              <el-tag type="success" size="large">{{ competitor.my_rating || '-' }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="区域平均">
              {{ competitor.avg_rating || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="区域排名">
              第{{ competitor.rank || '-' }}名
            </el-descriptions-item>
            <el-descriptions-item label="竞争对手">
              {{ competitor.total_competitors || '-' }}家
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- 未回复评论 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>待回复评论</span>
              <el-button type="primary" size="small" @click="$router.push('/reviews')">
                去回复
              </el-button>
            </div>
          </template>
          <el-table :data="unreplied" style="width: 100%" :max-height="250">
            <el-table-column prop="rating" label="评分" width="70">
              <template #default="{ row }">
                <el-tag size="small" :type="row.rating >= 4 ? 'success' : 'danger'">
                  {{ row.rating }}星
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="content" label="内容" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import request from '@/utils/request'

const trendDays = ref('30')
const competitor = ref({})
const unreplied = ref([])

const trendChart = ref(null)
const wordCloud = ref(null)
const topicChart = ref(null)

// 加载趋势数据
const loadTrendData = async () => {
  try {
    const res = await request.get(`/analytics/rating-trend?merchant_id=1&days=${trendDays.value}`)
    if (res.code === 200) {
      renderTrendChart(res.data)
    }
  } catch (error) {
    console.error('加载趋势数据失败:', error)
  }
}

// 加载关键词
const loadKeywords = async () => {
  try {
    const res = await request.get('/analytics/keywords?merchant_id=1&limit=20')
    if (res.code === 200) {
      renderWordCloud(res.data)
    }
  } catch (error) {
    console.error('加载关键词失败:', error)
  }
}

// 加载主题分布
const loadTopics = async () => {
  try {
    const res = await request.get('/analytics/topics?merchant_id=1&days=30')
    if (res.code === 200) {
      renderTopicChart(res.data)
    }
  } catch (error) {
    console.error('加载主题数据失败:', error)
  }
}

// 加载竞品分析
const loadCompetitor = async () => {
  try {
    const res = await request.get('/analytics/competitor?merchant_id=1')
    if (res.code === 200) {
      competitor.value = res.data
    }
  } catch (error) {
    console.error('加载竞品数据失败:', error)
  }
}

// 加载未回复评论
const loadUnreplied = async () => {
  try {
    const res = await request.get('/analytics/unreplied?merchant_id=1&limit=5')
    if (res.code === 200) {
      unreplied.value = res.data
    }
  } catch (error) {
    console.error('加载未回复评论失败:', error)
  }
}

// 渲染趋势图
const renderTrendChart = (data) => {
  if (!trendChart.value) return
  
  const chart = echarts.init(trendChart.value)
  const dates = data.map(item => item.date)
  const ratings = data.map(item => item.avg_rating)
  
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 5
    },
    series: [{
      name: '平均评分',
      type: 'line',
      smooth: true,
      data: ratings,
      itemStyle: { color: '#409EFF' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(64,158,255,0.5)' },
          { offset: 1, color: 'rgba(64,158,255,0.01)' }
        ])
      }
    }]
  })
}

// 渲染词云（简化版，用柱状图代替）
const renderWordCloud = (data) => {
  if (!wordCloud.value) return
  
  const chart = echarts.init(wordCloud.value)
  const keywords = data.map(item => item.keyword)
  const counts = data.map(item => item.count)
  
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '10%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'value',
      name: '出现次数'
    },
    yAxis: {
      type: 'category',
      data: keywords,
      inverse: true
    },
    series: [{
      type: 'bar',
      data: counts,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#83bff6' },
          { offset: 1, color: '#188df0' }
        ])
      },
      showBackground: true,
      backgroundStyle: { color: 'rgba(180, 180, 180, 0.1)' }
    }]
  })
}

// 渲染主题图
const renderTopicChart = (data) => {
  if (!topicChart.value) return
  
  const chart = echarts.init(topicChart.value)
  const topics = Object.keys(data).map(key => ({
    value: data[key],
    name: key
  }))
  
  chart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: true,
        formatter: '{b}: {c}'
      },
      data: topics
    }]
  })
}

onMounted(() => {
  loadTrendData()
  loadKeywords()
  loadTopics()
  loadCompetitor()
  loadUnreplied()
  
  window.addEventListener('resize', () => {
    trendChart.value && echarts.getInstanceByDom(trendChart.value)?.resize()
    wordCloud.value && echarts.getInstanceByDom(wordCloud.value)?.resize()
    topicChart.value && echarts.getInstanceByDom(topicChart.value)?.resize()
  })
})
</script>

<style scoped>
.analytics {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

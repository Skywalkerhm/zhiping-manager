<template>
  <div class="reviews">
    <!-- 筛选区 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="平台">
          <el-select v-model="filterForm.platform" placeholder="全部平台" clearable>
            <el-option label="大众点评" value="dianping" />
            <el-option label="美团" value="meituan" />
            <el-option label="饿了么" value="eleme" />
          </el-select>
        </el-form-item>

        <el-form-item label="情感">
          <el-select v-model="filterForm.sentiment" placeholder="全部情感" clearable>
            <el-option label="好评" value="positive" />
            <el-option label="中评" value="neutral" />
            <el-option label="差评" value="negative" />
          </el-select>
        </el-form-item>

        <el-form-item label="评分">
          <el-select v-model="filterForm.rating" placeholder="全部评分" clearable>
            <el-option label="5 星" :value="5" />
            <el-option label="4 星" :value="4" />
            <el-option label="3 星" :value="3" />
            <el-option label="2 星" :value="2" />
            <el-option label="1 星" :value="1" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="filterForm.is_replied" placeholder="全部状态" clearable>
            <el-option label="已回复" :value="true" />
            <el-option label="未回复" :value="false" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 评论列表 -->
    <el-card style="margin-top: 20px">
      <el-table
        v-loading="loading"
        :data="reviews"
        style="width: 100%"
        row-key="id"
      >
        <el-table-column prop="rating" label="评分" width="80">
          <template #default="{ row }">
            <el-tag :type="row.rating >= 4 ? 'success' : row.rating >= 3 ? 'warning' : 'danger'">
              {{ row.rating }}星
            </el-tag>
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

        <el-table-column prop="content" label="评论内容" show-overflow-tooltip min-width="300" />

        <el-table-column prop="sentiment" label="情感" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="row.sentiment === 'positive' ? 'success' : row.sentiment === 'neutral' ? 'warning' : 'danger'">
              {{ row.sentiment === 'positive' ? '好评' : row.sentiment === 'neutral' ? '中评' : '差评' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="is_replied" label="状态" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="row.is_replied ? 'success' : 'info'">
              {{ row.is_replied ? '已回复' : '未回复' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="review_time" label="评论时间" width="160" />

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.is_replied"
              type="primary"
              size="small"
              @click="handleGenerateReply(row)"
            >
              AI 回复
            </el-button>
            <el-button
              v-else
              type="info"
              size="small"
              disabled
            >
              已回复
            </el-button>
            <el-button type="success" size="small" @click="handleView(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div style="margin-top: 20px; text-align: right">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadReviews"
          @current-change="loadReviews"
        />
      </div>
    </el-card>

    <!-- AI 回复对话框 -->
    <el-dialog
      v-model="replyDialogVisible"
      title="AI 生成回复"
      width="600px"
    >
      <el-form :model="replyForm" label-width="80px">
        <el-form-item label="评论内容">
          <el-input
            v-model="replyForm.content"
            type="textarea"
            :rows="3"
            disabled
          />
        </el-form-item>

        <el-form-item label="AI 回复">
          <el-input
            v-model="replyForm.reply"
            type="textarea"
            :rows="4"
            placeholder="AI 正在生成回复..."
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="replyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSendReply">
          发送回复
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const reviews = ref([])
const replyDialogVisible = ref(false)

const filterForm = reactive({
  platform: '',
  sentiment: '',
  rating: null,
  is_replied: null
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const replyForm = reactive({
  reviewId: null,
  content: '',
  reply: ''
})

// 加载评论列表
const loadReviews = async () => {
  loading.value = true
  try {
    const params = {
      merchant_id: 1,
      page: pagination.page,
      size: pagination.size,
      ...filterForm
    }
    
    const res = await request.get('/reviews', { params })
    if (res.code === 200) {
      reviews.value = res.items || []
      pagination.total = res.total || 0
    }
  } catch (error) {
    console.error('加载评论失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadReviews()
}

// 重置
const handleReset = () => {
  filterForm.platform = ''
  filterForm.sentiment = ''
  filterForm.rating = null
  filterForm.is_replied = null
  handleSearch()
}

// 生成 AI 回复
const handleGenerateReply = async (row) => {
  replyForm.reviewId = row.id
  replyForm.content = row.content
  replyForm.reply = ''
  replyDialogVisible = true
  
  try {
    const res = await request.post('/replies/generate', {
      review_id: row.id,
      review_content: row.content,
      review_rating: row.rating,
      sentiment: row.sentiment
    })
    
    if (res.code === 200) {
      replyForm.reply = res.content
    }
  } catch (error) {
    console.error('生成回复失败:', error)
  }
}

// 发送回复
const handleSendReply = async () => {
  try {
    await request.post(`/replies/${replyForm.reviewId}/send`)
    ElMessage.success('回复发送成功')
    replyDialogVisible = false
    loadReviews()
  } catch (error) {
    console.error('发送回复失败:', error)
  }
}

// 查看详情
const handleView = (row) => {
  console.log('查看详情:', row)
}

onMounted(() => {
  loadReviews()
})
</script>

<style scoped>
.reviews {
  padding: 0;
}

.filter-card {
  margin-bottom: 20px;
}
</style>

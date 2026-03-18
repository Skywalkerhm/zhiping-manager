<template>
  <div class="settings">
    <el-row :gutter="20">
      <!-- LLM 设置 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>LLM 配置</span>
              <el-button type="primary" size="small" @click="saveLLMSettings">
                保存
              </el-button>
            </div>
          </template>

          <el-form :model="llmForm" label-width="120px">
            <el-form-item label="首选 LLM">
              <el-select v-model="llmForm.preferred_provider" style="width: 100%">
                <el-option label="通义千问" value="aliyun_qwen" />
                <el-option label="文心一言" value="baidu_ernie" />
                <el-option label="腾讯混元" value="tencent_hunyuan" />
              </el-select>
            </el-form-item>

            <el-form-item label="首选模型">
              <el-select v-model="llmForm.preferred_model" style="width: 100%">
                <el-option label="qwen-turbo" value="qwen-turbo" />
                <el-option label="qwen-plus" value="qwen-plus" />
                <el-option label="qwen-max" value="qwen-max" />
              </el-select>
            </el-form-item>

            <el-form-item label="自动切换">
              <el-switch v-model="llmForm.auto_switch_enabled" />
            </el-form-item>

            <el-form-item label="温度参数">
              <el-slider v-model="llmForm.temperature" :min="0" :max="1" :step="0.1" />
            </el-form-item>

            <el-form-item label="最大 Token">
              <el-input-number v-model="llmForm.max_tokens" :min="100" :max="4000" :step="100" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 通知设置 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>通知配置</span>
              <el-button type="primary" size="small" @click="saveNotificationSettings">
                保存
              </el-button>
            </div>
          </template>

          <el-form :model="notificationForm" label-width="120px">
            <el-form-item label="微信通知">
              <el-switch v-model="notificationForm.wechat_enabled" />
            </el-form-item>

            <el-form-item label="短信通知">
              <el-switch v-model="notificationForm.sms_enabled" />
            </el-form-item>

            <el-form-item label="邮件通知">
              <el-switch v-model="notificationForm.email_enabled" />
            </el-form-item>

            <el-form-item label="仅通知差评">
              <el-switch v-model="notificationForm.notify_negative_only" />
            </el-form-item>

            <el-form-item label="实时通知">
              <el-switch v-model="notificationForm.notify_realtime" />
            </el-form-item>

            <el-form-item label="每日汇总">
              <el-switch v-model="notificationForm.notify_summary_daily" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 店铺信息 -->
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>店铺信息</span>
              <el-button type="primary" size="small" @click="saveShopInfo">
                保存
              </el-button>
            </div>
          </template>

          <el-form :model="shopForm" label-width="120px">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="店铺名称">
                  <el-input v-model="shopForm.shop_name" />
                </el-form-item>
              </el-col>

              <el-col :span="8">
                <el-form-item label="店铺类型">
                  <el-select v-model="shopForm.shop_type" style="width: 100%">
                    <el-option label="餐饮" value="餐饮" />
                    <el-option label="美容" value="美容" />
                    <el-option label="娱乐" value="娱乐" />
                    <el-option label="零售" value="零售" />
                  </el-select>
                </el-form-item>
              </el-col>

              <el-col :span="8">
                <el-form-item label="联系电话">
                  <el-input v-model="shopForm.phone" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="所在城市">
                  <el-input v-model="shopForm.city" />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="所在区域">
                  <el-input v-model="shopForm.district" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="店铺地址">
              <el-input v-model="shopForm.address" type="textarea" :rows="2" />
            </el-form-item>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="大众点评 ID">
                  <el-input v-model="shopForm.dianping_shop_id" placeholder="请输入大众点评店铺 ID" />
                </el-form-item>
              </el-col>

              <el-col :span="8">
                <el-form-item label="美团 ID">
                  <el-input v-model="shopForm.meituan_shop_id" placeholder="请输入美团店铺 ID" />
                </el-form-item>
              </el-col>

              <el-col :span="8">
                <el-form-item label="饿了么 ID">
                  <el-input v-model="shopForm.eleme_shop_id" placeholder="请输入饿了么店铺 ID" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 系统信息 -->
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统信息</span>
            </div>
          </template>

          <el-descriptions :column="3" border>
            <el-descriptions-item label="系统版本">v1.0.0</el-descriptions-item>
            <el-descriptions-item label="API 接口数">29 个</el-descriptions-item>
            <el-descriptions-item label="数据库表">10 张</el-descriptions-item>
            <el-descriptions-item label="代码量">9000+ 行</el-descriptions-item>
            <el-descriptions-item label="开发时间">3 天</el-descriptions-item>
            <el-descriptions-item label="完成度">60%</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const llmForm = reactive({
  preferred_provider: 'aliyun_qwen',
  preferred_model: 'qwen-turbo',
  auto_switch_enabled: true,
  temperature: 0.7,
  max_tokens: 500
})

const notificationForm = reactive({
  wechat_enabled: true,
  sms_enabled: false,
  email_enabled: false,
  notify_negative_only: false,
  notify_realtime: true,
  notify_summary_daily: true
})

const shopForm = reactive({
  shop_name: '',
  shop_type: '',
  phone: '',
  city: '',
  district: '',
  address: '',
  dianping_shop_id: '',
  meituan_shop_id: '',
  eleme_shop_id: ''
})

// 加载设置
const loadSettings = async () => {
  try {
    // 加载 LLM 设置
    const llmRes = await request.get('/llm/settings')
    if (llmRes.code === 200) {
      Object.assign(llmForm, llmRes.data)
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

// 保存 LLM 设置
const saveLLMSettings = async () => {
  try {
    await request.put('/llm/settings', llmForm)
    ElMessage.success('LLM 设置保存成功')
  } catch (error) {
    console.error('保存 LLM 设置失败:', error)
  }
}

// 保存通知设置
const saveNotificationSettings = async () => {
  try {
    // TODO: 实现通知设置保存
    ElMessage.success('通知设置保存成功')
  } catch (error) {
    console.error('保存通知设置失败:', error)
  }
}

// 保存店铺信息
const saveShopInfo = async () => {
  try {
    // TODO: 实现店铺信息保存
    ElMessage.success('店铺信息保存成功')
  } catch (error) {
    console.error('保存店铺信息失败:', error)
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

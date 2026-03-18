<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside width="240px" class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <div class="logo-icon">
            <el-icon :size="28"><Monitor /></el-icon>
          </div>
          <span class="logo-text">智评管家</span>
        </div>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        router
      >
        <el-menu-item index="/dashboard" class="menu-item">
          <el-icon class="menu-icon"><DataAnalysis /></el-icon>
          <span class="menu-text">仪表盘</span>
        </el-menu-item>
        
        <el-menu-item index="/reviews" class="menu-item">
          <el-icon class="menu-icon"><ChatDotRound /></el-icon>
          <span class="menu-text">评论管理</span>
          <el-badge :value="stats.unreplied || 0" :hidden="!stats.unreplied" class="menu-badge" />
        </el-menu-item>
        
        <el-menu-item index="/analytics" class="menu-item">
          <el-icon class="menu-icon"><TrendCharts /></el-icon>
          <span class="menu-text">数据分析</span>
        </el-menu-item>
        
        <el-menu-item index="/settings" class="menu-item">
          <el-icon class="menu-icon"><Setting /></el-icon>
          <span class="menu-text">系统设置</span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <div class="user-info-mini">
          <el-avatar :size="32" icon="User" />
          <div class="user-detail">
            <div class="username">{{ userStore.userInfo?.username || '管理员' }}</div>
            <div class="user-role">商家版</div>
          </div>
        </div>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentTitle">{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-badge :value="stats.unreplied || 0" :hidden="!stats.unreplied" class="notification-badge">
            <el-button circle icon="Bell" />
          </el-badge>
          
          <el-dropdown @command="handleCommand" class="user-dropdown">
            <span class="user-info">
              <el-avatar :size="36" icon="User" />
              <span class="username">{{ userStore.userInfo?.username || '管理员' }}</span>
              <el-icon class="arrow"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  系统设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 模拟统计数据（实际应从 API 获取）
const stats = ref({
  unreplied: 3
})

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta.title || '仪表盘')

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } else if (command === 'profile') {
    ElMessage.info('个人中心开发中')
  } else if (command === 'settings') {
    router.push('/settings')
  }
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
  background: #f5f7fa;
}

/* 侧边栏样式 */
.sidebar {
  background: #fff;
  border-right: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(135deg, #FF9068 0%, #FF6600 100%);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  letter-spacing: 1px;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  padding: 12px 8px;
}

.menu-item {
  height: 48px;
  margin-bottom: 4px;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
}

.menu-item:hover {
  background: #fff7f2;
}

.menu-item.is-active {
  background: linear-gradient(135deg, #FFF0E6 0%, #FFE6D9 100%);
  color: #FF6600;
}

.menu-icon {
  font-size: 18px;
  margin-right: 12px;
  color: #666;
}

.menu-item.is-active .menu-icon {
  color: #FF6600;
}

.menu-text {
  font-size: 14px;
  font-weight: 500;
}

.menu-badge {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
}

:deep(.el-badge__content) {
  background: #FF6600;
  border: 2px solid #fff;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.user-info-mini {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-detail {
  flex: 1;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.user-role {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

/* 顶部导航 */
.header {
  height: 64px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.header-left {
  flex: 1;
}

:deep(.el-breadcrumb) {
  font-size: 14px;
}

:deep(.el-breadcrumb__item) {
  color: #666;
}

:deep(.el-breadcrumb__item.is-link) {
  color: #999;
}

:deep(.el-breadcrumb__item:last-child) {
  color: #333;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.notification-badge {
  cursor: pointer;
}

:deep(.el-badge__content) {
  background: #FF6600;
  border: 2px solid #fff;
}

.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.user-info:hover {
  background: #f5f7fa;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.arrow {
  font-size: 12px;
  color: #999;
}

/* 内容区 */
.main-content {
  padding: 20px;
  overflow-y: auto;
}

:deep(.el-menu-item) {
  border-radius: 8px !important;
}
</style>

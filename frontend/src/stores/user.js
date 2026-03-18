import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)

  // 登录
  async function login(username, password) {
    const response = await axios.post('/api/v1/auth/login', {
      username,
      password
    })
    
    if (response.data.access_token) {
      token.value = response.data.access_token
      localStorage.setItem('token', response.data.access_token)
      
      // 获取用户信息
      await getUserInfo()
      
      return response.data
    }
  }

  // 获取用户信息
  async function getUserInfo() {
    try {
      const response = await axios.get('/api/v1/auth/me')
      userInfo.value = response.data
      return response.data
    } catch (error) {
      logout()
      throw error
    }
  }

  // 登出
  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  return {
    token,
    userInfo,
    login,
    getUserInfo,
    logout
  }
})

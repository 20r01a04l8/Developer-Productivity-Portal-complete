import axios from 'axios'

const taskClient = axios.create({
  baseURL: '/api/tasks',
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
})

taskClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

taskClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred'

    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }

    return Promise.reject(new Error(message))
  }
)

export default taskClient

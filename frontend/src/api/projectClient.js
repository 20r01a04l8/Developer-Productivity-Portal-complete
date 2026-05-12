/**
 * Axios client for Project Service.
 *
 * Why a dedicated instance per service (not one global axios):
 *   - Each service has its own base URL
 *   - Interceptors are scoped — project service errors don't affect task service calls
 *   - Easy to add service-specific headers (e.g. X-Service-Version)
 *
 * Why interceptors instead of try/catch in every component:
 *   - Token injection happens once here, not in 20 different API calls
 *   - 401 handling (redirect to login) is centralised
 */
import axios from 'axios'

const projectClient = axios.create({
  baseURL: '/api/projects',
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
})

// Attach JWT to every outgoing request
projectClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Normalise error responses — components receive a plain Error with a message
projectClient.interceptors.response.use(
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

export default projectClient

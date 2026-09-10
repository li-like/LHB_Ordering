const TOKEN_KEY = 'ordering_v2_token'

function baseUrl() {
  const value = import.meta.env && import.meta.env.VITE_API_BASE_URL
  return String(value || 'http://127.0.0.1:8000/api/v2').replace(/\/+$/, '')
}

function queryString(query = {}) {
  const parts = []
  Object.keys(query).forEach((key) => {
    const value = query[key]
    if (value === undefined || value === null || value === '') return
    ;(Array.isArray(value) ? value : [value]).forEach((item) => parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(item)}`))
  })
  return parts.length ? `?${parts.join('&')}` : ''
}

export class ApiError extends Error {
  constructor(message, status = 0, data = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

function errorMessage(data, fallback) {
  if (!data || typeof data !== 'object') return fallback
  if (data.message || data.detail || data.error) return data.message || data.detail || data.error
  const first = Object.values(data)[0]
  if (Array.isArray(first) && first.length) return String(first[0])
  if (typeof first === 'string') return first
  return fallback
}

export const tokenStore = {
  get: () => uni.getStorageSync(TOKEN_KEY) || '',
  set(token) { token ? uni.setStorageSync(TOKEN_KEY, token) : uni.removeStorageSync(TOKEN_KEY) }
}

export function request(path, options = {}) {
  const token = tokenStore.get()
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${baseUrl()}/${String(path).replace(/^\/+/, '')}${queryString(options.query)}`,
      method: options.method || 'GET', data: options.data, timeout: options.timeout || 15000,
      header: { Accept: 'application/json', 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(options.headers || {}) },
      success(response) {
        if (response.statusCode >= 200 && response.statusCode < 300) return resolve(response.data)
        if (response.statusCode === 401) {
          tokenStore.set('')
          uni.$emit('auth:expired')
        }
        const data = response.data
        reject(new ApiError(errorMessage(data, `请求失败 (${response.statusCode})`), response.statusCode, data))
      },
      fail(error) { reject(new ApiError(error.errMsg || '网络连接失败，请稍后重试')) }
    })
  })
}

export function uploadImage(path, filePath, formData = {}, name = 'file') {
  const token = tokenStore.get()
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: `${baseUrl()}/${String(path).replace(/^\/+/, '')}`, filePath, name, formData,
      header: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      success(response) {
        let data = response.data
        try { data = typeof data === 'string' ? JSON.parse(data) : data } catch (_) {}
        if (response.statusCode >= 200 && response.statusCode < 300) return resolve(data)
        reject(new ApiError(errorMessage(data, '图片上传失败'), response.statusCode, data))
      },
      fail(error) { reject(new ApiError(error.errMsg || '图片上传失败')) }
    })
  })
}

/**
 * API Client
 * Axios-based HTTP client for Club ID Invest API
 */

import axios from 'axios'

const API_URL = process.env.API_URL || 'http://localhost:8000/api'

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_URL}/auth/refresh`, null, {
            headers: {
              Authorization: `Bearer ${refreshToken}`,
            },
          })

          const { access_token, refresh_token } = response.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)

          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        } catch (refreshError) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      }
    }

    return Promise.reject(error)
  }
)

// API endpoints
export const authAPI = {
  login: (email: string, password: string) =>
    apiClient.post('/auth/login', { email, password }),
  register: (data: RegisterData) =>
    apiClient.post('/auth/register', data),
  logout: () =>
    apiClient.post('/auth/logout'),
  me: () =>
    apiClient.get('/auth/me'),
  refreshToken: () =>
    apiClient.post('/auth/refresh'),
}

export const dashboardAPI = {
  getDashboard: () =>
    apiClient.get('/dashboard/'),
  getAlerts: (severity?: string) =>
    apiClient.get('/dashboard/alerts', { params: { severity } }),
  getProjectProgress: () =>
    apiClient.get('/dashboard/projects'),
}

export const projectsAPI = {
  list: (params?: ProjectFilters) =>
    apiClient.get('/projects/', { params }),
  get: (id: number) =>
    apiClient.get(`/projects/${id}`),
  getInvestors: (id: number) =>
    apiClient.get(`/projects/${id}/investors`),
}

export const investmentsAPI = {
  validate: (data: ValidateInvestmentData) =>
    apiClient.post('/investments/validate', data),
  create: (data: CreateInvestmentData) =>
    apiClient.post('/investments/', data),
  list: (params?: InvestmentFilters) =>
    apiClient.get('/investments/', { params }),
  get: (id: number) =>
    apiClient.get(`/investments/${id}`),
  confirm: (id: number) =>
    apiClient.post(`/investments/${id}/confirm`),
}

export const contractsAPI = {
  create: (data: CreateContractData) =>
    apiClient.post('/contracts/', data),
  generatePdf: (id: number) =>
    apiClient.post(`/contracts/${id}/generate-pdf`),
  sendForSignature: (id: number) =>
    apiClient.post(`/contracts/${id}/send-signature`),
  sign: (id: number, data: SignContractData) =>
    apiClient.post(`/contracts/${id}/sign`, data),
  list: (params?: ContractFilters) =>
    apiClient.get('/contracts/', { params }),
  get: (id: number) =>
    apiClient.get(`/contracts/${id}`),
}

// Types
export interface RegisterData {
  email: string
  password: string
  first_name: string
  last_name: string
  phone?: string
}

export interface ProjectFilters {
  status?: string
  category?: string
  min_raised_percent?: number
  limit?: number
  offset?: number
}

export interface InvestmentFilters {
  status?: string
  project_id?: number
  limit?: number
  offset?: number
}

export interface ValidateInvestmentData {
  project_id: number
  investment_amount: number
  user_id: number
}

export interface CreateInvestmentData {
  project_id: number
  investment_amount: number
  legal_entity_id?: number
  notes?: string
}

export interface CreateContractData {
  project_id: number
  investment_id?: number
  legal_entity_id?: number
  contract_type: string
  title?: string
}

export interface SignContractData {
  contract_id: number
  ip_address: string
  user_agent: string
}

export interface ContractFilters {
  status?: string
  limit?: number
}

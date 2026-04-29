/**
 * API Client Configuration
 * Базовая настройка HTTP клиента для работы с бекендом
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

// API Configuration
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
export const API_TIMEOUT = 30000;

// Типы
export interface ApiError {
  message: string;
  detail?: string;
  status?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
}

// Создаём экземпляр axios
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - добавляем токен авторизации
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('accessToken');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor - обработка ошибок и refresh token
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Если 401 и не retry - пробуем обновить токен
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data;
          localStorage.setItem('accessToken', access_token);
          localStorage.setItem('refreshToken', refresh_token);

          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }

          return api(originalRequest);
        } catch (refreshError) {
          // Refresh не удался - разлогиниваем
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          localStorage.removeItem('isLoggedIn');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

export default api;

// Хелпер для обработки ошибок
export function handleApiError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail?: string; message?: string }>;
    return {
      message: axiosError.response?.data?.detail || axiosError.response?.data?.message || 'Ошибка сервера',
      status: axiosError.response?.status,
    };
  }
  return { message: 'Неизвестная ошибка' };
}


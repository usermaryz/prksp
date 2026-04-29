/**
 * Auth API Service
 * Сервис аутентификации
 */

import api, { handleApiError } from './api';

// Типы
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  phone?: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login_at?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name: string;
  phone?: string;
}

// API методы
export const authApi = {
  /**
   * Вход в систему
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      // OAuth2 форма требует form-urlencoded
      const formData = new URLSearchParams();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);

      const response = await api.post<LoginResponse>('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      // Сохраняем токены
      localStorage.setItem('accessToken', response.data.access_token);
      localStorage.setItem('refreshToken', response.data.refresh_token);
      localStorage.setItem('isLoggedIn', 'true');
      localStorage.setItem('user', JSON.stringify({
        fullName: response.data.user.full_name,
        role: response.data.user.role,
        email: response.data.user.email,
      }));

      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Регистрация
   */
  async register(data: RegisterRequest): Promise<User> {
    try {
      const response = await api.post<User>('/auth/register', data);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Выход из системы
   */
  async logout(): Promise<void> {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        await api.post('/auth/logout', { refresh_token: refreshToken });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('isLoggedIn');
      localStorage.removeItem('user');
    }
  },

  /**
   * Получить текущего пользователя
   */
  async getCurrentUser(): Promise<User> {
    try {
      const response = await api.get<User>('/auth/me');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Обновить токен
   */
  async refreshToken(refreshToken: string): Promise<{ access_token: string; refresh_token: string }> {
    try {
      const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

export default authApi;

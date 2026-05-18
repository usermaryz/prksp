/**
 * Picking API Service
 * Сервис сборки заказов
 */

import api, { handleApiError } from './api';

// Типы
export type PickingTaskStatus = 'pending' | 'assigned' | 'in_progress' | 'completed' | 'cancelled';

export interface PickingItem {
  id: number;
  picking_task_id: number;
  order_item_id: number;
  product_id: number;
  product_name: string;
  product_barcode: string;
  location_id: number;
  location_code: string;
  quantity_to_pick: number;
  quantity_picked: number;
  status: 'pending' | 'picked' | 'short';
  picked_at?: string;
}

export interface PickingTask {
  id: number;
  order_id: number;
  order_number: string;
  status: PickingTaskStatus;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  assigned_to?: number;
  assigned_to_name?: string;
  items: PickingItem[];
  items_count?: number;
  total_items?: number;
  picked_items?: number;
  progress: number;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

export interface PickingStats {
  pending: number;
  in_progress: number;
  completed_today: number;
  average_time_minutes: number;
}

// API методы
export const pickingApi = {
  /**
   * Получить задания на сборку
   */
  async getTasks(filters: { status?: PickingTaskStatus; assigned_to?: number } = {}): Promise<PickingTask[]> {
    try {
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.assigned_to) params.append('assigned_to', filters.assigned_to.toString());

      const response = await api.get<PickingTask[]>(`/picking/tasks?${params}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить задание по ID
   */
  async getTask(id: number): Promise<PickingTask> {
    try {
      const response = await api.get<PickingTask>(`/picking/tasks/${id}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Создать задание на сборку
   */
  async createTask(orderId: number): Promise<PickingTask> {
    try {
      const response = await api.post<PickingTask>('/picking/tasks', { order_id: orderId });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Взять задание в работу
   */
  async assignTask(taskId: number): Promise<PickingTask> {
    try {
      const response = await api.post<PickingTask>(`/picking/tasks/${taskId}/assign`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Начать сборку
   */
  async startTask(taskId: number): Promise<PickingTask> {
    try {
      const response = await api.post<PickingTask>(`/picking/tasks/${taskId}/start`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Отметить товар как собранный
   */
  async pickItem(taskId: number, itemId: number, quantity: number): Promise<PickingItem> {
    try {
      const response = await api.post<PickingItem>(`/picking/tasks/${taskId}/items/${itemId}/pick`, {
        quantity_picked: quantity,
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Завершить сборку
   */
  async completeTask(taskId: number): Promise<PickingTask> {
    try {
      const response = await api.post<PickingTask>(`/picking/tasks/${taskId}/complete`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Отменить задание
   */
  async cancelTask(taskId: number, reason?: string): Promise<PickingTask> {
    try {
      const response = await api.post<PickingTask>(`/picking/tasks/${taskId}/cancel`, { reason });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить статистику
   */
  async getStats(): Promise<PickingStats> {
    try {
      const response = await api.get<PickingStats>('/picking/stats');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

export default pickingApi;


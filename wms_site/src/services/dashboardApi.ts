/**
 * Dashboard API Service
 * Сервис метрик и дашборда
 */

import api, { handleApiError } from './api';

// Типы
export interface DashboardMetrics {
  products: {
    total: number;
    active: number;
    low_stock: number;
  };
  orders: {
    total: number;
    pending: number;
    picking: number;
    shipped: number;
    delivered_today: number;
  };
  inventory: {
    total_items: number;
    total_value: number;
    zones_capacity: number;
    zones_usage: number;
  };
  picking: {
    pending_tasks: number;
    in_progress: number;
    completed_today: number;
    average_time_minutes: number;
  };
  logistics: {
    pending_shipments: number;
    in_transit: number;
    delivered_today: number;
    failed_deliveries: number;
  };
}

export interface RecentOrder {
  id: number;
  order_number: string;
  customer_name: string;
  status: string;
  total: number;
  created_at: string;
}

export interface RecentActivity {
  id: number;
  type: 'order' | 'picking' | 'shipment' | 'inventory';
  description: string;
  user_name: string;
  created_at: string;
}

export interface PerformanceData {
  date: string;
  orders_created: number;
  orders_shipped: number;
  orders_delivered: number;
}

// API методы
export const dashboardApi = {
  /**
   * Получить метрики дашборда
   */
  async getMetrics(): Promise<DashboardMetrics> {
    try {
      const response = await api.get<DashboardMetrics>('/dashboard/metrics');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить последние заказы
   */
  async getRecentOrders(limit: number = 5): Promise<RecentOrder[]> {
    try {
      const response = await api.get<RecentOrder[]>(`/dashboard/recent-orders?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить последнюю активность
   */
  async getRecentActivity(limit: number = 10): Promise<RecentActivity[]> {
    try {
      const response = await api.get<RecentActivity[]>(`/dashboard/recent-activity?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить данные производительности за период
   */
  async getPerformance(days: number = 7): Promise<PerformanceData[]> {
    try {
      const response = await api.get<PerformanceData[]>(`/dashboard/performance?days=${days}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

export default dashboardApi;

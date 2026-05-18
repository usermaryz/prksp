/**
 * Orders API Service
 * Сервис работы с заказами
 */

import api, { handleApiError, PaginatedResponse } from './api';

// Типы
export type OrderStatus = 'pending' | 'confirmed' | 'picking' | 'packed' | 'shipped' | 'delivered' | 'cancelled';
export type OrderPriority = 'low' | 'normal' | 'high' | 'urgent';
export type DeliveryMethod = 'courier' | 'pickup' | 'post' | 'transport';

export interface OrderItem {
  id: number;
  product_id: number;
  product_barcode: string;
  product_name: string;
  quantity: number;
  picked_quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Customer {
  id: number;
  name: string;
  email?: string;
  phone: string;
  company_name?: string;
  inn?: string;
  is_corporate: boolean;
}

export interface Address {
  id: number;
  city: string;
  street: string;
  building: string;
  apartment?: string;
  postal_code?: string;
  entrance?: string;
  floor?: string;
  intercom?: string;
  notes?: string;
}

export interface Order {
  id: number;
  order_number: string;
  external_id?: string;
  customer_id?: number;
  customer?: Customer;
  shipping_address_id?: number;
  shipping_address?: Address;
  status: OrderStatus;
  priority: OrderPriority;
  delivery_method: DeliveryMethod;
  subtotal: number;
  discount: number;
  shipping_cost: number;
  total: number;
  notes?: string;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
  shipped_at?: string;
  delivered_at?: string;
}

export interface OrderCreate {
  customer_id?: number;
  shipping_address?: {
    city: string;
    street: string;
    building: string;
    apartment?: string;
    postal_code?: string;
  };
  priority?: OrderPriority;
  delivery_method?: DeliveryMethod;
  notes?: string;
  items: Array<{
    product_id: number;
    quantity: number;
  }>;
}

export interface OrderUpdate {
  status?: OrderStatus;
  priority?: OrderPriority;
  delivery_method?: DeliveryMethod;
  notes?: string;
}

export interface OrderFilters {
  page?: number;
  limit?: number;
  status?: OrderStatus;
  priority?: OrderPriority;
}

// API методы
export const orderApi = {
  /**
   * Получить список заказов
   */
  async getOrders(filters: OrderFilters = {}): Promise<PaginatedResponse<Order>> {
    try {
      const params = new URLSearchParams();
      if (filters.page) params.append('page', filters.page.toString());
      if (filters.limit) params.append('limit', filters.limit.toString());
      if (filters.status) params.append('status', filters.status);
      if (filters.priority) params.append('priority', filters.priority);

      const response = await api.get<PaginatedResponse<Order>>(`/orders?${params}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить заказ по ID
   */
  async getOrder(id: number): Promise<Order> {
    try {
      const response = await api.get<Order>(`/orders/${id}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Поиск заказов
   */
  async searchOrders(query: string): Promise<Order[]> {
    try {
      const response = await api.get<Order[]>(`/orders/search?q=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Создать заказ
   */
  async createOrder(data: OrderCreate): Promise<Order> {
    try {
      const response = await api.post<Order>('/orders', data);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Обновить заказ
   */
  async updateOrder(id: number, data: OrderUpdate): Promise<Order> {
    try {
      const response = await api.patch<Order>(`/orders/${id}`, data);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Обновить статус заказа
   */
  async updateOrderStatus(id: number, status: OrderStatus): Promise<Order> {
    try {
      const response = await api.patch<Order>(`/orders/${id}/status`, { status });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Удалить заказ
   */
  async deleteOrder(id: number): Promise<void> {
    try {
      await api.delete(`/orders/${id}`);
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

export default orderApi;

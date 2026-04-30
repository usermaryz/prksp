/**
 * Logistics API Service
 * Сервис доставки и логистики
 */

import api, { handleApiError } from './api';

// Типы
export type ShipmentStatus = 'pending' | 'label_created' | 'picked_up' | 'in_transit' | 'out_for_delivery' | 'delivered' | 'failed' | 'returned';
export type DeliveryMethod = 'courier' | 'pickup_point' | 'post';
export type CarrierCode = 'cdek' | 'boxberry' | 'russian_post' | 'dpd' | 'dellin';

export interface Carrier {
  id: number;
  code: CarrierCode;
  name: string;
  tracking_url_template?: string;
  is_active: boolean;
}

export interface TrackingEvent {
  id: number;
  shipment_id: number;
  status: ShipmentStatus;
  location?: string;
  description: string;
  event_time: string;
  raw_status?: string;
}

export interface Shipment {
  id: number;
  order_id: number;
  order_number: string;
  tracking_number: string;
  carrier_id: number;
  carrier?: Carrier;
  delivery_method: DeliveryMethod;
  status: ShipmentStatus;
  recipient_name: string;
  recipient_phone: string;
  delivery_address: string;
  delivery_city: string;
  delivery_postal_code?: string;
  estimated_delivery?: string;
  actual_delivery?: string;
  weight?: number;
  declared_value?: number;
  shipping_cost?: number;
  tracking_events: TrackingEvent[];
  created_at: string;
  updated_at: string;
}

export interface ShipmentCreate {
  order_id: number;
  carrier_id: number;
  delivery_method: DeliveryMethod;
  recipient_name: string;
  recipient_phone: string;
  delivery_address: string;
  delivery_city: string;
  delivery_postal_code?: string;
  weight?: number;
  declared_value?: number;
}

export interface DeliveryRate {
  carrier_id: number;
  carrier_name: string;
  delivery_method: DeliveryMethod;
  price: number;
  estimated_days: number;
  estimated_delivery: string;
}

export interface ShipmentStats {
  total: number;
  pending: number;
  in_transit: number;
  delivered: number;
  failed: number;
}

// API методы
export const logisticsApi = {
  /**
   * Получить список отправлений
   */
  async getShipments(filters: { status?: ShipmentStatus; carrier_id?: number } = {}): Promise<Shipment[]> {
    try {
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.carrier_id) params.append('carrier_id', filters.carrier_id.toString());

      const response = await api.get<Shipment[]>(`/logistics/shipments?${params}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить отправление по ID
   */
  async getShipment(id: number): Promise<Shipment> {
    try {
      const response = await api.get<Shipment>(`/logistics/shipments/${id}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить отправление по трек-номеру
   */
  async getShipmentByTracking(trackingNumber: string): Promise<Shipment> {
    try {
      const response = await api.get<Shipment>(`/logistics/shipments/tracking/${trackingNumber}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Создать отправление
   */
  async createShipment(data: ShipmentCreate): Promise<Shipment> {
    try {
      const response = await api.post<Shipment>('/logistics/shipments', data);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Отменить отправление
   */
  async cancelShipment(id: number): Promise<Shipment> {
    try {
      const response = await api.post<Shipment>(`/logistics/shipments/${id}/cancel`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить историю отслеживания
   */
  async getTrackingHistory(shipmentId: number): Promise<TrackingEvent[]> {
    try {
      const response = await api.get<TrackingEvent[]>(`/logistics/shipments/${shipmentId}/tracking`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Обновить статус отслеживания (sync с перевозчиком)
   */
  async syncTracking(shipmentId: number): Promise<Shipment> {
    try {
      const response = await api.post<Shipment>(`/logistics/shipments/${shipmentId}/sync-tracking`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить перевозчиков
   */
  async getCarriers(): Promise<Carrier[]> {
    try {
      const response = await api.get<Carrier[]>('/logistics/carriers');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Рассчитать стоимость доставки
   */
  async calculateRates(data: {
    from_city: string;
    to_city: string;
    weight: number;
    declared_value?: number;
  }): Promise<DeliveryRate[]> {
    try {
      const response = await api.post<DeliveryRate[]>('/logistics/calculate-rates', data);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить статистику
   */
  async getStats(): Promise<ShipmentStats> {
    try {
      const response = await api.get<ShipmentStats>('/logistics/stats');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

export default logisticsApi;

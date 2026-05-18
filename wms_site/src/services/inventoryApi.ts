/**
 * Inventory API Service
 * Сервис работы со складскими остатками
 */

import api, { handleApiError, PaginatedResponse } from './api';

// Типы
export interface WarehouseZone {
  id: number;
  code: string;
  name: string;
  description?: string;
  zone_type: 'storage' | 'picking' | 'receiving' | 'shipping' | 'staging';
  capacity: number;
  current_usage: number;
  is_active: boolean;
}

export interface StorageLocation {
  id: number;
  zone_id: number;
  zone?: WarehouseZone;
  code: string;
  aisle: string;
  rack: string;
  shelf: string;
  bin: string;
  location_type: 'bulk' | 'pick' | 'reserve';
  max_weight?: number;
  max_volume?: number;
  is_available: boolean;
}

export interface InventoryItem {
  id: number;
  product_id: number;
  product_name: string;
  product_sku: string;
  location_id: number;
  location_code: string;
  quantity: number;
  reserved_quantity: number;
  available_quantity: number;
  lot_number?: string;
  expiry_date?: string;
  received_at: string;
  last_counted_at?: string;
}

export interface StockMovement {
  id: number;
  product_id: number;
  product_name: string;
  from_location_id?: number;
  from_location_code?: string;
  to_location_id?: number;
  to_location_code?: string;
  quantity: number;
  movement_type: 'receive' | 'ship' | 'transfer' | 'adjustment' | 'return';
  reference_type?: string;
  reference_id?: number;
  reason?: string;
  performed_by: number;
  performed_at: string;
}

export interface PlacementTask {
  id: number;
  product_id: number;
  product_name: string;
  product_sku: string;
  quantity: number;
  suggested_location_id: number;
  suggested_location_code: string;
  actual_location_id?: number;
  status: 'pending' | 'in_progress' | 'completed';
  assigned_to?: number;
  created_at: string;
  completed_at?: string;
}

// API методы
export const inventoryApi = {
  /**
   * Получить склады
   */
  async getWarehouses(): Promise<{ id: number; code: string; name: string; address?: string }[]> {
    try {
      const response = await api.get('/inventory/warehouses');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить зоны склада
   */
  async getZones(): Promise<WarehouseZone[]> {
    try {
      const response = await api.get<WarehouseZone[]>('/inventory/zones');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить ячейки хранения
   */
  async getLocations(zoneId?: number): Promise<StorageLocation[]> {
    try {
      const params = zoneId ? `?zone_id=${zoneId}` : '';
      const response = await api.get<StorageLocation[]>(`/inventory/locations${params}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить остатки
   */
  async getInventory(filters: { product_id?: number; location_id?: number } = {}): Promise<InventoryItem[]> {
    try {
      const params = new URLSearchParams();
      if (filters.product_id) params.append('product_id', filters.product_id.toString());
      if (filters.location_id) params.append('location_id', filters.location_id.toString());

      const response = await api.get<InventoryItem[]>(`/inventory?${params}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить остаток товара
   */
  async getProductStock(productId: number): Promise<{ total: number; available: number; reserved: number }> {
    try {
      const response = await api.get<{ total: number; available: number; reserved: number }>(
        `/inventory/products/${productId}/stock`
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить историю перемещений
   */
  async getMovements(filters: { product_id?: number; from?: string; to?: string } = {}): Promise<StockMovement[]> {
    try {
      const params = new URLSearchParams();
      if (filters.product_id) params.append('product_id', filters.product_id.toString());
      if (filters.from) params.append('from', filters.from);
      if (filters.to) params.append('to', filters.to);

      const response = await api.get<StockMovement[]>(`/inventory/movements?${params}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Создать перемещение
   */
  async createMovement(data: {
    product_id: number;
    from_location_id?: number;
    to_location_id?: number;
    quantity: number;
    movement_type: string;
    reason?: string;
  }): Promise<StockMovement> {
    try {
      const response = await api.post<StockMovement>('/inventory/movements', data);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить задания на размещение
   */
  async getPlacementTasks(): Promise<PlacementTask[]> {
    try {
      const response = await api.get<PlacementTask[]>('/inventory/placement-tasks');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Выполнить размещение
   */
  async completePlacement(taskId: number, locationId: number): Promise<PlacementTask> {
    try {
      const response = await api.post<PlacementTask>(`/inventory/placement-tasks/${taskId}/complete`, {
        actual_location_id: locationId,
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

export default inventoryApi;


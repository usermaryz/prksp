/**
 * API Services Index
 * Экспорт всех API сервисов
 */

export { default as api, API_BASE_URL, handleApiError } from './api';
export type { ApiError, PaginatedResponse } from './api';

export { default as authApi } from './authApi';
export type { User, LoginRequest, LoginResponse, RegisterRequest } from './authApi';

export { default as productApi } from './productApi';
export type { Product, Category, Brand, ProductCreate, ProductUpdate, ProductFilters } from './productApi';

export { default as orderApi } from './orderApi';
export type { Order, OrderItem, Customer, Address, OrderCreate, OrderUpdate, OrderFilters, OrderStatus, OrderPriority, DeliveryMethod } from './orderApi';

export { default as inventoryApi } from './inventoryApi';
export type { WarehouseZone, StorageLocation, InventoryItem, StockMovement, PlacementTask } from './inventoryApi';

export { default as pickingApi } from './pickingApi';
export type { PickingTask, PickingItem, PickingTaskStatus, PickingStats } from './pickingApi';

export { default as logisticsApi } from './logisticsApi';
export type { Shipment, ShipmentCreate, Carrier, TrackingEvent, DeliveryRate, ShipmentStatus, ShipmentStats } from './logisticsApi';

export { default as dashboardApi } from './dashboardApi';
export type { DashboardMetrics, RecentOrder, RecentActivity, PerformanceData } from './dashboardApi';


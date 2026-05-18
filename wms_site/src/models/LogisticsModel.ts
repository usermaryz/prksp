// =============================================================================
// LOGISTICS & DELIVERY MODELS
// Модели для логистики и интеграции с сервисом доставки
// =============================================================================

// -----------------------------------------------------------------------------
// Enums
// -----------------------------------------------------------------------------

/** Статус отправления */
export type ShipmentStatus =
    | 'created'          // Создано
    | 'pending_pickup'   // Ожидает забора
    | 'picked_up'        // Забрано
    | 'in_transit'       // В пути
    | 'out_for_delivery' // Передано курьеру
    | 'delivered'        // Доставлено
    | 'failed'           // Ошибка доставки
    | 'returned'         // Возвращено
    | 'cancelled';       // Отменено

/** Способ доставки */
export type DeliveryMethod =
    | 'courier'   // Курьерская доставка
    | 'truck'     // Фура/грузовик
    | 'express'   // Экспресс-доставка
    | 'standard'  // Стандартная доставка
    | 'pickup';   // Самовывоз

/** Тип адреса */
export type AddressType = 'pickup' | 'delivery' | 'warehouse' | 'billing';

/** Статус маршрута */
export type RouteStatus = 'planned' | 'in_progress' | 'completed' | 'cancelled';

/** Статус остановки */
export type StopStatus = 'pending' | 'completed' | 'failed' | 'skipped';

// -----------------------------------------------------------------------------
// Address Models
// -----------------------------------------------------------------------------

/** Адрес */
export interface Address {
    id: number;
    type: AddressType;
    country: string;
    region?: string;
    city: string;
    street: string;
    building: string;
    apartment?: string;
    postalCode: string;
    latitude?: number;
    longitude?: number;
    fullAddress?: string;
    isDefault?: boolean;
}

/** Запрос на создание адреса */
export interface CreateAddressRequest {
    type?: AddressType;
    country?: string;
    region?: string;
    city: string;
    street: string;
    building: string;
    apartment?: string;
    postalCode: string;
    latitude?: number;
    longitude?: number;
    isDefault?: boolean;
}

/** Запрос на обновление адреса */
export interface UpdateAddressRequest extends Partial<CreateAddressRequest> {}

// -----------------------------------------------------------------------------
// Contact Info
// -----------------------------------------------------------------------------

/** Контактная информация */
export interface ContactInfo {
    name: string;
    phone: string;
    email?: string;
    company?: string;
}

// -----------------------------------------------------------------------------
// Package & Dimensions
// -----------------------------------------------------------------------------

/** Размеры */
export interface Dimensions {
    length: number;  // см
    width: number;   // см
    height: number;  // см
}

/** Упаковка/грузовое место */
export interface Package {
    id: number;
    barcode: string;
    weight: number;       // кг
    dimensions?: Dimensions;
    contents?: string;
    declaredValue?: number;
}

/** Запрос на создание упаковки */
export interface CreatePackageRequest {
    weight: number;
    dimensions?: Dimensions;
    contents?: string;
    declaredValue?: number;
}

// -----------------------------------------------------------------------------
// Shipment Models
// -----------------------------------------------------------------------------

/** Отправление */
export interface Shipment {
    id: number;
    shipmentNumber: string;
    orderId: number;
    orderNumber: string;
    status: ShipmentStatus;
    deliveryMethod: DeliveryMethod;
    providerId?: number;
    providerName?: string;
    externalTrackingId?: string;
    pickupAddress?: Address;
    deliveryAddress: Address;
    senderInfo?: ContactInfo;
    receiverInfo: ContactInfo;
    packages?: Package[];
    weight?: number;
    dimensions?: Dimensions;
    estimatedDeliveryDate?: string;
    actualDeliveryDate?: string;
    cost?: number;
    currency?: string;
    notes?: string;
    trackingHistory?: TrackingEvent[];
    createdAt: string;
    updatedAt: string;
}

/** Запрос на создание отправления */
export interface CreateShipmentRequest {
    orderId: number;
    deliveryMethod: DeliveryMethod;
    providerId?: number;
    pickupAddress?: CreateAddressRequest;
    deliveryAddress: CreateAddressRequest;
    senderInfo?: ContactInfo;
    receiverInfo: ContactInfo;
    packages?: CreatePackageRequest[];
    scheduledPickupDate?: string;
    notes?: string;
}

/** Запрос на обновление отправления */
export interface UpdateShipmentRequest {
    deliveryMethod?: DeliveryMethod;
    deliveryAddress?: UpdateAddressRequest;
    receiverInfo?: ContactInfo;
    scheduledPickupDate?: string;
    notes?: string;
}

// -----------------------------------------------------------------------------
// Tracking Models
// -----------------------------------------------------------------------------

/** Событие отслеживания */
export interface TrackingEvent {
    id: number;
    shipmentId: number;
    status: ShipmentStatus;
    location?: string;
    description: string;
    timestamp: string;
    source: 'internal' | 'external';
}

/** Запрос на создание события отслеживания */
export interface CreateTrackingEventRequest {
    status: ShipmentStatus;
    location?: string;
    description: string;
}

// -----------------------------------------------------------------------------
// Delivery Method Info
// -----------------------------------------------------------------------------

/** Информация о способе доставки */
export interface DeliveryMethodInfo {
    id: string;
    name: string;
    description: string;
    method: DeliveryMethod;
    estimatedDays: {
        min: number;
        max: number;
    };
    maxWeight?: number;
    maxDimensions?: Dimensions;
    priceRange?: {
        min: number;
        max: number;
        currency: string;
    };
    available: boolean;
}

// -----------------------------------------------------------------------------
// Delivery Cost Calculation
// -----------------------------------------------------------------------------

/** Запрос на расчет стоимости доставки */
export interface CalculateDeliveryCostRequest {
    pickupAddress: CreateAddressRequest;
    deliveryAddress: CreateAddressRequest;
    deliveryMethod: DeliveryMethod;
    packages?: CreatePackageRequest[];
    totalWeight?: number;
    declaredValue?: number;
}

/** Ответ с расчетом стоимости */
export interface DeliveryCostResponse {
    deliveryMethod: DeliveryMethod;
    cost: number;
    currency: string;
    estimatedDays: number;
    estimatedDeliveryDate: string;
    breakdown?: Array<{
        name: string;
        cost: number;
    }>;
}

// -----------------------------------------------------------------------------
// Delivery Routes
// -----------------------------------------------------------------------------

/** Остановка маршрута */
export interface RouteStop {
    id: number;
    order: number;
    shipmentId: number;
    address: Address;
    type: 'pickup' | 'delivery';
    estimatedArrival?: string;
    actualArrival?: string;
    status: StopStatus;
    notes?: string;
}

/** Маршрут доставки */
export interface DeliveryRoute {
    id: number;
    routeNumber: string;
    date: string;
    driverId: number;
    driverName: string;
    vehicleId?: number;
    vehicleNumber?: string;
    status: RouteStatus;
    stops: RouteStop[];
    totalDistance?: number;
    estimatedDuration?: number;
    startTime?: string;
    endTime?: string;
}

/** Запрос на создание маршрута */
export interface CreateDeliveryRouteRequest {
    date: string;
    driverId: number;
    vehicleId?: number;
    shipmentIds: number[];
    notes?: string;
}

/** Запрос на обновление маршрута */
export interface UpdateDeliveryRouteRequest {
    driverId?: number;
    vehicleId?: number;
    status?: RouteStatus;
    stops?: Array<{
        shipmentId: number;
        order: number;
    }>;
}

// -----------------------------------------------------------------------------
// External Delivery Provider Integration
// -----------------------------------------------------------------------------

/** Провайдер доставки (внешний сервис) */
export interface DeliveryProvider {
    id: number;
    name: string;
    code: string;
    logo?: string;
    supportedMethods: DeliveryMethod[];
    active: boolean;
    rating?: number;
}

/** Запрос на создание доставки через внешний сервис */
export interface CreateDeliveryRequest {
    orderId: number;
    shipmentId?: number;
    providerId: number;
    deliveryMethod: DeliveryMethod;
    pickupAddress: CreateAddressRequest;
    deliveryAddress: CreateAddressRequest;
    senderInfo?: ContactInfo;
    receiverInfo: ContactInfo;
    packages?: CreatePackageRequest[];
    declaredValue?: number;
    cashOnDelivery?: number;
    insuranceRequired?: boolean;
    scheduledPickupDate?: string;
    notes?: string;
}

/** Ответ от внешнего сервиса доставки */
export interface DeliveryResponse {
    id: number;
    externalId: string;
    trackingNumber: string;
    trackingUrl?: string;
    status: ShipmentStatus;
    providerName: string;
    estimatedDeliveryDate?: string;
    cost?: number;
    createdAt: string;
}

/** Ответ с отслеживанием от внешнего сервиса */
export interface DeliveryTrackingResponse {
    deliveryId: string;
    trackingNumber: string;
    status: ShipmentStatus;
    statusDescription: string;
    currentLocation?: string;
    estimatedDeliveryDate?: string;
    lastUpdated: string;
    events: TrackingEvent[];
}

/** Payload вебхука от внешнего сервиса */
export interface DeliveryWebhookPayload {
    providerId: string;
    event: 'status_changed' | 'delivered' | 'failed' | 'returned';
    deliveryId: string;
    trackingNumber: string;
    status: string;
    statusDescription?: string;
    location?: string;
    timestamp: string;
    signature: string;
}

/** Запрос на получение тарифов */
export interface GetDeliveryRatesRequest {
    pickupAddress: CreateAddressRequest;
    deliveryAddress: CreateAddressRequest;
    packages?: CreatePackageRequest[];
    totalWeight?: number;
    declaredValue?: number;
    preferredDeliveryDate?: string;
}

/** Тариф от провайдера */
export interface DeliveryRate {
    providerId: number;
    providerName: string;
    providerLogo?: string;
    deliveryMethod: DeliveryMethod;
    methodName: string;
    cost: number;
    currency: string;
    estimatedDays: {
        min: number;
        max: number;
    };
    estimatedDeliveryDate: {
        from: string;
        to: string;
    };
    available: boolean;
    unavailableReason?: string;
}

// -----------------------------------------------------------------------------
// List Responses
// -----------------------------------------------------------------------------

/** Мета-информация для пагинации */
export interface PaginationMeta {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
}

/** Ответ со списком отправлений */
export interface ShipmentsListResponse {
    data: Shipment[];
    meta: PaginationMeta;
}

// -----------------------------------------------------------------------------
// Utility Types
// -----------------------------------------------------------------------------

/** Маппинг статусов на русский */
export const SHIPMENT_STATUS_LABELS: Record<ShipmentStatus, string> = {
    created: 'Создано',
    pending_pickup: 'Ожидает забора',
    picked_up: 'Забрано',
    in_transit: 'В пути',
    out_for_delivery: 'Передано курьеру',
    delivered: 'Доставлено',
    failed: 'Ошибка доставки',
    returned: 'Возвращено',
    cancelled: 'Отменено',
};

/** Маппинг способов доставки на русский */
export const DELIVERY_METHOD_LABELS: Record<DeliveryMethod, string> = {
    courier: 'Курьерская доставка',
    truck: 'Фура/грузовик',
    express: 'Экспресс-доставка',
    standard: 'Стандартная доставка',
    pickup: 'Самовывоз',
};

/** Цвета статусов для UI */
export const SHIPMENT_STATUS_COLORS: Record<ShipmentStatus, string> = {
    created: 'bg-gray-500',
    pending_pickup: 'bg-yellow-500',
    picked_up: 'bg-blue-500',
    in_transit: 'bg-slate-1000',
    out_for_delivery: 'bg-purple-500',
    delivered: 'bg-green-500',
    failed: 'bg-red-500',
    returned: 'bg-orange-500',
    cancelled: 'bg-gray-400',
};


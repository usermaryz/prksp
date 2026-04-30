import axios from 'axios';
import { Product } from '../models/ProductModel';
import { API_BASE_URL, API_TIMEOUT } from '../config/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: API_TIMEOUT,
    headers: {
        'Content-Type': 'application/json',
    },
});

export interface Order {
    id: number;
    orderNumber: string;
    status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
    createdAt: string;
    products: OrderProduct[];
    assignedTo?: string;
    priority: 'low' | 'medium' | 'high';
}

export interface OrderProduct {
    id: number;
    product: Product;
    quantity: number;
    picked: boolean;
    location: string;
}

// Моковые данные для заказов
const mockOrders: Order[] = [
    {
        id: 1,
        orderNumber: 'ORD-2024-001',
        status: 'pending',
        createdAt: '2024-03-20 10:00',
        priority: 'high',
        products: [
            {
                id: 1,
                product: {
                    id: 1,
                    barcode: 'PRD12345',
                    name: 'Беспроводные наушники',
                    brand: 'SoundCore',
                    country: 'China',
                    category: 'Electronics',
                    image: 'https://example.com/headphones.jpg',
                    status: 'pending',
                },
                quantity: 2,
                picked: false,
                location: 'A-01-01',
            },
            {
                id: 2,
                product: {
                    id: 2,
                    barcode: 'PRD23456',
                    name: 'Белковый порошок',
                    brand: 'OptimumNutrition',
                    country: 'USA',
                    category: 'Health & Fitness',
                    image: 'https://example.com/protein.jpg',
                    status: 'pending',
                },
                quantity: 1,
                picked: false,
                location: 'B-02-03',
            },
        ],
    },
    {
        id: 2,
        orderNumber: 'ORD-2024-002',
        status: 'in_progress',
        createdAt: '2024-03-20 09:30',
        priority: 'medium',
        assignedTo: 'Иван Петров',
        products: [
            {
                id: 3,
                product: {
                    id: 3,
                    barcode: 'PRD34567',
                    name: 'Механическая клавиатура',
                    brand: 'Logitech',
                    country: 'Taiwan',
                    category: 'Computer Accessories',
                    image: 'https://example.com/keyboard.jpg',
                    status: 'pending',
                },
                quantity: 1,
                picked: true,
                location: 'C-03-02',
            },
        ],
    },
];

export const orderPickingApi = {
    // Получить список заказов
    async getOrders(): Promise<Order[]> {
        try {
            const response = await api.get('/picking/orders');
            return response.data;
        } catch (error) {
            console.error('Error fetching orders:', error);
            return mockOrders;
        }
    },

    // Получить заказ по ID
    async getOrder(orderId: number): Promise<Order> {
        try {
            const response = await api.get(`/picking/orders/${orderId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching order:', error);
            const order = mockOrders.find(o => o.id === orderId);
            if (!order) throw new Error('Order not found');
            return order;
        }
    },

    // Обновить статус заказа
    async updateOrderStatus(orderId: number, status: Order['status']): Promise<Order> {
        try {
            const response = await api.patch(`/picking/orders/${orderId}/status`, { status });
            return response.data;
        } catch (error) {
            console.error('Error updating order status:', error);
            const order = mockOrders.find(o => o.id === orderId);
            if (!order) throw new Error('Order not found');
            return { ...order, status };
        }
    },

    // Отметить товар как собранный
    async markProductAsPicked(orderId: number, productId: number): Promise<Order> {
        try {
            const response = await api.patch(`/picking/orders/${orderId}/products/${productId}/picked`);
            return response.data;
        } catch (error) {
            console.error('Error marking product as picked:', error);
            const order = mockOrders.find(o => o.id === orderId);
            if (!order) throw new Error('Order not found');
            const product = order.products.find(p => p.id === productId);
            if (!product) throw new Error('Product not found');
            product.picked = true;
            return order;
        }
    },

    // Назначить заказ сборщику
    async assignOrder(orderId: number, assignee: string): Promise<Order> {
        try {
            const response = await api.patch(`/picking/orders/${orderId}/assign`, { assignee });
            return response.data;
        } catch (error) {
            console.error('Error assigning order:', error);
            const order = mockOrders.find(o => o.id === orderId);
            if (!order) throw new Error('Order not found');
            return { ...order, assignedTo: assignee };
        }
    },

    // Поиск заказов
    async searchOrders(query: string): Promise<Order[]> {
        try {
            const response = await api.get(`/picking/orders/search?q=${query}`);
            return response.data;
        } catch (error) {
            console.error('Error searching orders:', error);
            return mockOrders.filter(
                order =>
                    order.orderNumber.toLowerCase().includes(query.toLowerCase()) ||
                    order.products.some(
                        p =>
                            p.product.name.toLowerCase().includes(query.toLowerCase()) ||
                            p.product.barcode.toLowerCase().includes(query.toLowerCase())
                    )
            );
        }
    },
};

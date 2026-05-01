import { makeAutoObservable } from 'mobx';
import { orderPickingApi, Order, OrderProduct } from '../services/orderPickingApi';

export default class OrderPickingViewModel {
    orders: Order[] = [];
    selectedOrder: Order | null = null;
    loading = false;
    error: string | null = null;
    searchQuery = '';

    constructor() {
        makeAutoObservable(this);
    }

    async loadData() {
        this.loading = true;
        this.error = null;
        try {
            this.orders = await orderPickingApi.getOrders();
        } catch (error) {
            this.error = 'Ошибка при загрузке заказов';
            console.error('Error loading orders:', error);
        } finally {
            this.loading = false;
        }
    }

    async selectOrder(orderId: number) {
        try {
            this.selectedOrder = await orderPickingApi.getOrder(orderId);
        } catch (error) {
            console.error('Error selecting order:', error);
            throw error;
        }
    }

    async updateOrderStatus(orderId: number, status: Order['status']) {
        try {
            const updatedOrder = await orderPickingApi.updateOrderStatus(orderId, status);
            const index = this.orders.findIndex(o => o.id === orderId);
            if (index !== -1) {
                this.orders[index] = updatedOrder;
            }
            if (this.selectedOrder?.id === orderId) {
                this.selectedOrder = updatedOrder;
            }
        } catch (error) {
            console.error('Error updating order status:', error);
            throw error;
        }
    }

    async markProductAsPicked(orderId: number, productId: number) {
        try {
            const updatedOrder = await orderPickingApi.markProductAsPicked(orderId, productId);
            const index = this.orders.findIndex(o => o.id === orderId);
            if (index !== -1) {
                this.orders[index] = updatedOrder;
            }
            if (this.selectedOrder?.id === orderId) {
                this.selectedOrder = updatedOrder;
            }
        } catch (error) {
            console.error('Error marking product as picked:', error);
            throw error;
        }
    }

    async assignOrder(orderId: number, assignee: string) {
        try {
            const updatedOrder = await orderPickingApi.assignOrder(orderId, assignee);
            const index = this.orders.findIndex(o => o.id === orderId);
            if (index !== -1) {
                this.orders[index] = updatedOrder;
            }
            if (this.selectedOrder?.id === orderId) {
                this.selectedOrder = updatedOrder;
            }
        } catch (error) {
            console.error('Error assigning order:', error);
            throw error;
        }
    }

    async searchOrders(query: string) {
        this.searchQuery = query;
        if (!query.trim()) {
            await this.loadData();
            return;
        }
        try {
            this.orders = await orderPickingApi.searchOrders(query);
        } catch (error) {
            console.error('Error searching orders:', error);
        }
    }

    get pendingOrders() {
        return this.orders.filter(order => order.status === 'pending');
    }

    get inProgressOrders() {
        return this.orders.filter(order => order.status === 'in_progress');
    }

    get completedOrders() {
        return this.orders.filter(order => order.status === 'completed');
    }

    get cancelledOrders() {
        return this.orders.filter(order => order.status === 'cancelled');
    }

    get selectedOrderProgress() {
        if (!this.selectedOrder) return 0;
        const totalProducts = this.selectedOrder.products.length;
        const pickedProducts = this.selectedOrder.products.filter(p => p.picked).length;
        return (pickedProducts / totalProducts) * 100;
    }
}

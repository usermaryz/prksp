/**
 * Order picking — данные из Picking Service через API Gateway
 */
import { pickingApi, PickingTask } from './pickingApi';
import { Product } from '../models/ProductModel';

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

function mapPriority(p: string): Order['priority'] {
  if (p === 'high' || p === 'urgent') return 'high';
  if (p === 'low') return 'low';
  return 'medium';
}

function mapStatus(s: string): Order['status'] {
  if (s === 'in_progress' || s === 'assigned') return 'in_progress';
  if (s === 'completed') return 'completed';
  if (s === 'cancelled') return 'cancelled';
  return 'pending';
}

function taskToOrder(task: PickingTask): Order {
  const picked = task.status === 'completed';
  return {
    id: task.id,
    orderNumber: task.order_number,
    status: mapStatus(task.status),
    createdAt: task.created_at,
    assignedTo: task.assigned_to_name,
    priority: mapPriority(task.priority),
    products: Array.from({ length: Math.max(1, task.items_count ?? task.total_items ?? 1) }, (_, i) => ({
      id: i + 1,
      product: {
        id: task.order_id,
        barcode: task.order_number,
        name: `Позиция ${i + 1}`,
        brand: '',
        country: '',
        category: '',
        image: '',
        status: picked ? 'accepted' : 'pending',
      },
      quantity: 1,
      picked,
      location: '—',
    })),
  };
}

export const orderPickingApi = {
  async getOrders(): Promise<Order[]> {
    const tasks = await pickingApi.getTasks();
    return tasks.map(taskToOrder);
  },

  async getOrder(taskId: number): Promise<Order> {
    const task = await pickingApi.getTask(taskId);
    return taskToOrder(task);
  },

  async updateOrderStatus(taskId: number, status: Order['status']): Promise<Order> {
    if (status === 'in_progress') {
      const task = await pickingApi.startTask(taskId);
      return taskToOrder(task);
    }
    if (status === 'completed') {
      const task = await pickingApi.completeTask(taskId);
      return taskToOrder(task);
    }
    return this.getOrder(taskId);
  },

  async markProductAsPicked(taskId: number, _productId: number): Promise<Order> {
    return this.getOrder(taskId);
  },

  async assignOrder(taskId: number, assignee: string): Promise<Order> {
    const order = await this.getOrder(taskId);
    return { ...order, assignedTo: assignee };
  },

  async searchOrders(query: string): Promise<Order[]> {
    const orders = await this.getOrders();
    const q = query.toLowerCase();
    return orders.filter(o => o.orderNumber.toLowerCase().includes(q));
  },
};

export default orderPickingApi;

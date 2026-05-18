import { makeAutoObservable, runInAction } from 'mobx';
import { OrderCollection } from '../models/OrderCollectionModel';
import { pickingApi, PickingTask } from '../services/pickingApi';

function mapTaskToCollection(task: PickingTask): OrderCollection {
  const statusMap: Record<string, OrderCollection['status']> = {
    pending: 'Pending Collection',
    assigned: 'Pending Collection',
    in_progress: 'In Progress',
    completed: 'Completed',
    cancelled: 'Completed',
  };
  return {
    id: task.order_number,
    customerName: task.assigned_to_name || 'Клиент',
    customerEmail: '',
    items: [{ name: `Заказ #${task.order_id}`, quantity: task.items_count || 1 }],
    location: `Задача ${task.id}`,
    status: statusMap[task.status] || 'Pending Collection',
  };
}

export class OrderCollectionViewModel {
  search = '';
  statusFilter: string = 'All Statuses';
  showModal = false;
  selectedOrder: OrderCollection | null = null;
  orders: OrderCollection[] = [];
  loading = false;
  error: string | null = null;

  constructor() {
    makeAutoObservable(this);
    void this.loadOrders();
  }

  async loadOrders() {
    this.loading = true;
    this.error = null;
    try {
      const tasks = await pickingApi.getTasks();
      runInAction(() => {
        this.orders = tasks.map(mapTaskToCollection);
      });
    } catch (e) {
      runInAction(() => {
        this.error = 'Ошибка загрузки заданий сборки';
        console.error(e);
      });
    } finally {
      runInAction(() => {
        this.loading = false;
      });
    }
  }

  get filteredOrders() {
    let filtered = this.orders;
    if (this.statusFilter !== 'All Statuses') {
      filtered = filtered.filter(o => o.status === this.statusFilter);
    }
    if (this.search.trim()) {
      const s = this.search.toLowerCase();
      filtered = filtered.filter(
        o =>
          o.id.toLowerCase().includes(s) ||
          o.customerName.toLowerCase().includes(s) ||
          o.location.toLowerCase().includes(s)
      );
    }
    return filtered;
  }

  setSearch(value: string) {
    this.search = value;
  }

  setStatusFilter(value: string) {
    this.statusFilter = value;
  }

  openModal(order: OrderCollection) {
    this.selectedOrder = order;
    this.showModal = true;
  }

  closeModal() {
    this.showModal = false;
    this.selectedOrder = null;
  }
}

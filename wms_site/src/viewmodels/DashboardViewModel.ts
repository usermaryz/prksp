import { makeAutoObservable, runInAction } from 'mobx';
import { DashboardModel, DashboardStat } from '../models/DashboardModel';
import { dashboardApi } from '../services/dashboardApi';

export class DashboardViewModel {
  model: DashboardModel = { stats: [] };
  loading = false;
  error: string | null = null;

  constructor() {
    makeAutoObservable(this);
    void this.loadStats();
  }

  get stats(): DashboardStat[] {
    return this.model.stats;
  }

  async loadStats() {
    this.loading = true;
    this.error = null;
    try {
      const m = await dashboardApi.getMetrics();
      runInAction(() => {
        this.model.stats = [
          {
            icon: 'fa-solid fa-box',
            label: 'Заказы всего',
            value: String(m.orders.total),
            change: `${m.orders.pending} ожидают`,
            changeType: 'neutral',
            color: 'bg-slate-100 text-slate-700',
          },
          {
            icon: 'fa-solid fa-chart-line',
            label: 'В сборке',
            value: String(m.orders.picking),
            change: `${m.picking.in_progress} в работе`,
            changeType: 'up',
            color: 'bg-blue-100 text-blue-600',
          },
          {
            icon: 'fa-solid fa-warehouse',
            label: 'Товары на складе',
            value: String(m.products.total),
            change: `${m.products.low_stock} мало остатков`,
            changeType: m.products.low_stock > 0 ? 'down' : 'up',
            color: 'bg-green-100 text-green-600',
          },
          {
            icon: 'fa-solid fa-truck',
            label: 'Отгружено',
            value: String(m.orders.shipped),
            change: `${m.picking.pending_tasks} задач сборки`,
            changeType: 'neutral',
            color: 'bg-red-100 text-red-600',
          },
        ];
      });
    } catch (e) {
      runInAction(() => {
        this.error = 'Не удалось загрузить метрики';
        console.error(e);
      });
    } finally {
      runInAction(() => {
        this.loading = false;
      });
    }
  }
}

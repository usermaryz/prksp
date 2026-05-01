import { makeAutoObservable } from 'mobx';
import { DashboardModel, DashboardStat } from '../models/DashboardModel';

export class DashboardViewModel {
  model: DashboardModel = {
    stats: [
      {
        icon: 'fa-solid fa-box',
        label: 'Общее количество заказов',
        value: '1,284',
        change: '12.5%',
        changeType: 'up',
        color: 'bg-indigo-100 text-indigo-600',
      },
      {
        icon: 'fa-solid fa-chart-line',
        label: 'Скорость обработки',
        value: '98.3%',
        change: '3.2%',
        changeType: 'up',
        color: 'bg-blue-100 text-blue-600',
      },
      {
        icon: 'fa-solid fa-warehouse',
        label: 'Уровень инвентаризации',
        value: '85.7%',
        change: '0.5%',
        changeType: 'down',
        color: 'bg-green-100 text-green-600',
      },
      {
        icon: 'fa-solid fa-undo',
        label: 'Коэффициент возврата',
        value: '3.8%',
        change: '1.1%',
        changeType: 'down',
        color: 'bg-red-100 text-red-600',
      },
    ],
  };

  constructor() {
    makeAutoObservable(this);
  }

  get stats(): DashboardStat[] {
    return this.model.stats;
  }
}

import { makeAutoObservable } from 'mobx';
import { UserAccountModel } from '../models/UserAccountModel';

export class UserAccountViewModel {
  user: UserAccountModel | null = null;
  isEditing: { [key: string]: boolean } = {
    email: false,
    phone: false,
    location: false,
  };
  tempValues: { [key: string]: string } = {
    email: '',
    phone: '',
    location: '',
  };
  showAllActivities: boolean = false;

  constructor() {
    makeAutoObservable(this);
    this.loadUser();
  }

  loadUser() {
    // Replace with real API call
    this.user = {
      id: '1',
      fullName: 'Марк Кучер',
      role: 'Главный бригадир',
      avatar: '',
      verified: true,
      premium: true,
      email: 'mark.kucher@wms.com',
      phone: '+7 (916) 123-4567',
      location: 'Сколково, Россия',
      timezone: 'UTC',
      stats: {
        totalOrders: 1284,
        pendingShipments: 45,
        completedTasks: 892,
        efficiency: 94.5,
      },
      activities: [
        {
          id: 1,
          action: 'Обработан заказ #WH58921',
          timestamp: '2 часа назад',
          status: 'success',
          icon: 'fa-box',
        },
        {
          id: 2,
          action: 'Обновлен счетчик запасов',
          timestamp: '4 часа назад',
          status: 'info',
          icon: 'fa-clipboard-check',
        },
        {
          id: 3,
          action: 'Сгенерированы метки для отправки',
          timestamp: '6 часов назад',
          status: 'success',
          icon: 'fa-shipping-fast',
        },
        {
          id: 4,
          action: 'Оповещение о запасе: SKU-75892',
          timestamp: '1 день назад',
          status: 'warning',
          icon: 'fa-exclamation-triangle',
        },
        {
          id: 5,
          action: 'Проведена инвентаризация склада',
          timestamp: '2 дня назад',
          status: 'success',
          icon: 'fa-clipboard-list',
        },
        {
          id: 6,
          action: 'Обновлен статус заказа #WH58920',
          timestamp: '2 дня назад',
          status: 'info',
          icon: 'fa-tasks',
        },
        {
          id: 7,
          action: 'Добавлен новый товар в систему',
          timestamp: '3 дня назад',
          status: 'success',
          icon: 'fa-plus-circle',
        },
        {
          id: 8,
          action: 'Проверка качества товаров',
          timestamp: '3 дня назад',
          status: 'info',
          icon: 'fa-check-circle',
        },
        {
          id: 9,
          action: 'Обновление цен на товары',
          timestamp: '4 дня назад',
          status: 'info',
          icon: 'fa-tag',
        },
        {
          id: 10,
          action: 'Отчет по движению товаров',
          timestamp: '4 дня назад',
          status: 'success',
          icon: 'fa-chart-bar',
        },
      ],
    };
  }

  get recentActivities() {
    return this.user?.activities.slice(0, 4) || [];
  }

  get allActivities() {
    return this.user?.activities || [];
  }

  toggleEditing(field: string) {
    if (!this.isEditing[field]) {
      // При начале редактирования копируем текущее значение во временное
      this.tempValues[field] = this.user ? (this.user as any)[field] : '';
    }
    this.isEditing[field] = !this.isEditing[field];
  }

  updateTempValue(field: string, value: string) {
    this.tempValues[field] = value;
  }

  saveField(field: string) {
    if (this.user) {
      (this.user as any)[field] = this.tempValues[field];
      // Here you would typically make an API call to update the user data
      this.toggleEditing(field);
    }
  }

  cancelEditing(field: string) {
    this.toggleEditing(field);
  }

  toggleAllActivities() {
    this.showAllActivities = !this.showAllActivities;
  }

  logout() {
    // Очищаем данные авторизации
    localStorage.removeItem('isLoggedIn');
    // Перезагружаем страницу для сброса состояния приложения
    window.location.href = '/login';
  }
}

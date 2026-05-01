import { makeAutoObservable } from 'mobx';
import { OrderCollection } from '../models/OrderCollectionModel';

export class OrderCollectionViewModel {
  search = '';
  statusFilter: string = 'All Statuses';
  showModal = false;
  selectedOrder: OrderCollection | null = null;

  orders: OrderCollection[] = [
    {
      id: 'ORD-2505-1234',
      customerName: 'Марк Кучер',
      customerEmail: 'mark.kucher@wms.com',
      items: [
        { name: 'Беспроводные наушники', quantity: 1 },
        { name: 'Смартфонный чехол', quantity: 1 },
      ],
      location: 'Зона A - Полка 12',
      status: 'In Progress',
    },
    {
      id: 'ORD-2505-1235',
      customerName: 'Ева Джонсон',
      customerEmail: 'emma.j@example.com',
      items: [
        { name: 'Беговые кроссовки', quantity: 1 },
        { name: 'Фитнес-трекер', quantity: 1 },
        { name: 'Вода', quantity: 1 },
      ],
      location: 'Зона B - Полка 5',
      status: 'In Progress',
    },
    {
      id: 'ORD-2505-1236',
      customerName: 'Михаил Чен',
      customerEmail: 'michael.c@example.com',
      items: [{ name: 'Ноутбучный рюкзак', quantity: 1 }],
      location: 'Зона A - Полка 8',
      status: 'Pending Collection',
    },
    {
      id: 'ORD-2505-1237',
      customerName: 'Сара Уильямс',
      customerEmail: 'sarah.w@example.com',
      items: [
        { name: 'Беспроводная мышь', quantity: 1 },
        { name: 'USB-C кабель', quantity: 1 },
      ],
      location: 'Зона C - Полка 3',
      status: 'Pending Collection',
    },
    {
      id: 'ORD-2505-1238',
      customerName: 'Давид Гарсия',
      customerEmail: 'david.g@example.com',
      items: [
        { name: 'Белковый порошок', quantity: 1 },
        { name: 'Шейкер бутылка', quantity: 1 },
      ],
      location: 'Зона B - Полка 11',
      status: 'Completed',
    },
  ];

  constructor() {
    makeAutoObservable(this);
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
          o.customerEmail.toLowerCase().includes(s) ||
          o.items.some(i => i.name.toLowerCase().includes(s))
      );
    }
    return filtered;
  }

  setSearch(val: string) {
    this.search = val;
  }
  setStatusFilter(val: string) {
    this.statusFilter = val;
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

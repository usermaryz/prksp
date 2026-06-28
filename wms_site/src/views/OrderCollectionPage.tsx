import React, { useEffect, useState } from 'react';
import { observer } from 'mobx-react-lite';
import { OrderCollectionViewModel } from '../viewmodels/OrderCollectionViewModel';
import OrderCollectionTable from '../components/OrderCollectionTable';
import OrderCollectionModal from '../components/OrderCollectionModal';
import AppLayout from '../components/layout/AppLayout';
import PageHeader from '../components/layout/PageHeader';
import { btnPrimary, searchInputClass } from '../components/layout/pageStyles';

const OrderCollectionPage: React.FC = observer(() => {
  const [vm] = useState(() => new OrderCollectionViewModel());

  useEffect(() => {
    void vm.loadOrders();
  }, [vm]);

  return (
    <AppLayout>
      <PageHeader title="Приёмка" subtitle="Управление и обработка сборки заказов на складе" />

      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
        <div className="flex-grow relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <i className="fas fa-barcode text-slate-400" />
          </div>
          <input
            type="text"
            value={vm.search}
            onChange={e => vm.setSearch(e.target.value)}
            className={`${searchInputClass} pl-10`}
            placeholder="Сканируйте или введите штрих-код заказа"
          />
        </div>
        <div className="flex items-center space-x-2">
          <select
            value={vm.statusFilter}
            onChange={e => vm.setStatusFilter(e.target.value)}
            className="px-3 py-2.5 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-slate-900"
          >
            <option value="All Statuses">Все статусы</option>
            <option value="Pending Collection">Ожидает сборки</option>
            <option value="In Progress">В процессе</option>
            <option value="Completed">Завершено</option>
          </select>
          <button
            type="button"
            className={btnPrimary}
            onClick={() => {
              if (vm.selectedOrder) {
                vm.openModal(vm.selectedOrder);
              } else if (vm.filteredOrders.length > 0) {
                vm.openModal(vm.filteredOrders[0]);
              }
            }}
          >
            <i className="fas fa-barcode mr-2" />
            Сканировать заказ
          </button>
        </div>
      </div>

      {vm.error && (
        <div className="mb-4 rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">{vm.error}</div>
      )}

      {vm.loading ? (
        <p className="text-sm text-slate-500">Загрузка...</p>
      ) : (
        <OrderCollectionTable orders={vm.filteredOrders} onAction={order => vm.openModal(order)} />
      )}
      <OrderCollectionModal order={vm.showModal ? vm.selectedOrder : null} onClose={() => vm.closeModal()} />
    </AppLayout>
  );
});

export default OrderCollectionPage;

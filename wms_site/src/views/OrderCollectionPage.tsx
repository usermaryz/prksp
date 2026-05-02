import React from 'react';
import { observer } from 'mobx-react-lite';
import { OrderCollectionViewModel } from '../viewmodels/OrderCollectionViewModel';
import Navigation from '../components/Navigation';
import OrderCollectionTable from '../components/OrderCollectionTable';
import OrderCollectionModal from '../components/OrderCollectionModal';


const vm = new OrderCollectionViewModel();

const statusFilterLabels: Record<string, string> = {
  'All Statuses': 'Все статусы',
  'Pending Collection': 'Ожидает сборки',
  'In Progress': 'В процессе',
  Completed: 'Завершено',
};

const OrderCollectionPage: React.FC = observer(() => (
  <div className="order-collection-page min-h-screen bg-gray-50">
    <Navigation active="Сборка заказов" />
    <div className="py-10">
      <header>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold leading-tight text-gray-900">Сбор заказов</h1>
          <p className="text-sm text-gray-500">Управление и обработка сборки заказов на складе</p>
        </div>
      </header>
      <main>
        <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
          <div className="px-4 py-8 sm:px-0">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
              <div className="flex-grow relative mb-4 md:mb-0">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i className="fas fa-barcode text-gray-400"></i>
                  </div>
                  <input
                    type="text"
                    value={vm.search}
                    onChange={e => vm.setSearch(e.target.value)}
                    className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                    placeholder="Сканируйте или введите штрих-код заказа"
                  />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <div className="relative">
                  <select
                    value={vm.statusFilter}
                    onChange={e => vm.setStatusFilter(e.target.value)}
                    className="appearance-none block pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-lg bg-white transition"
                  >
                    <option value="All Statuses">Все статусы</option>
                    <option value="Pending Collection">Ожидает сборки</option>
                    <option value="In Progress">В процессе</option>
                    <option value="Completed">Завершено</option>
                  </select>
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                    <svg className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="none">
                      <path
                        d="M7 7l3 3 3-3"
                        stroke="currentColor"
                        strokeWidth="1.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </div>
                </div>
                <button
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
                  onClick={() => {
                    if (vm.selectedOrder) {
                      vm.openModal(vm.selectedOrder);
                    } else if (vm.filteredOrders.length > 0) {
                      vm.openModal(vm.filteredOrders[0]);
                    }
                  }}
                >
                  <i className="fas fa-barcode mr-2"></i>
                  Сканировать заказ
                </button>
              </div>
            </div>
            <OrderCollectionTable
              orders={vm.filteredOrders}
              onAction={order => vm.openModal(order)}
            />
            <OrderCollectionModal
              order={vm.showModal ? vm.selectedOrder : null}
              onClose={() => vm.closeModal()}
            />
          </div>
        </div>
      </main>
    </div>
  </div>
));

export default OrderCollectionPage;

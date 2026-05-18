import React, { useEffect, useState } from 'react';
import { observer } from 'mobx-react-lite';
import OrderPickingViewModel from '../viewmodels/OrderPickingViewModel';
import OrderPickingList from '../components/OrderPickingList';
import OrderPickingDetails from '../components/OrderPickingDetails';
import { Order } from '../services/orderPickingApi';
import AppLayout from '../components/layout/AppLayout';
import PageHeader from '../components/layout/PageHeader';
import { pageCard, searchInputClass } from '../components/layout/pageStyles';

const OrderPickingPage: React.FC = observer(() => {
  const [viewModel] = useState(() => new OrderPickingViewModel());
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    viewModel.loadData();
  }, [viewModel]);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    viewModel.searchOrders(query);
  };

  const handleOrderSelect = (order: Order) => {
    viewModel.selectOrder(order.id);
  };

  const handleProductPicked = (productId: number) => {
    if (viewModel.selectedOrder) {
      viewModel.markProductAsPicked(viewModel.selectedOrder.id, productId);
    }
  };

  const handleStatusChange = (status: Order['status']) => {
    if (viewModel.selectedOrder) {
      viewModel.updateOrderStatus(viewModel.selectedOrder.id, status);
    }
  };

  if (viewModel.error) {
    return (
      <AppLayout>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {viewModel.error}
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <PageHeader title="Сборка" subtitle="Управление процессом сбора заказов" />

      <div className="mb-6">
        <input
          type="text"
          value={searchQuery}
          onChange={handleSearch}
          placeholder="Поиск заказов..."
          className={searchInputClass}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <OrderPickingList
            orders={viewModel.orders}
            selectedOrderId={viewModel.selectedOrder?.id}
            onOrderSelect={handleOrderSelect}
          />
        </div>
        <div className="lg:col-span-2">
          {viewModel.selectedOrder ? (
            <OrderPickingDetails
              order={viewModel.selectedOrder}
              onProductPicked={handleProductPicked}
              onStatusChange={handleStatusChange}
            />
          ) : (
            <div className={`${pageCard} p-6 text-center text-slate-500`}>
              Выберите заказ для просмотра деталей
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
});

export default OrderPickingPage;

import React, { useEffect, useState } from 'react';
import { observer } from 'mobx-react-lite';
import OrderPickingViewModel from '../viewmodels/OrderPickingViewModel';
import OrderPickingList from '../components/OrderPickingList';
import OrderPickingDetails from '../components/OrderPickingDetails';
import { Order } from '../services/orderPickingApi';
import Navigation from '../components/Navigation';

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
            <div className="min-h-screen bg-gray-50">
                <Navigation active="Сборка заказов" />
                <div className="p-4">
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                        {viewModel.error}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <Navigation active="Сборка заказов" />
            <div className="p-4">
                <div className="mb-6">
                    <h1 className="text-2xl font-semibold text-gray-900">Сборка заказов</h1>
                    <p className="mt-1 text-sm text-gray-500">
                        Управление процессом сбора заказов
                    </p>
                </div>

                <div className="mb-4">
                    <div style={{ display: 'flex', gap: '10px' }}>
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={handleSearch}
                            placeholder="Поиск заказов..."
                            style={{
                                flex: 1,
                                padding: '8px',
                                border: '1px solid #dee2e6',
                                borderRadius: '4px'
                            }}
                        />
                    </div>
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
                            <div className="bg-white shadow rounded-lg p-6 text-center text-gray-500">
                                Выберите заказ для просмотра деталей
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
});

export default OrderPickingPage;

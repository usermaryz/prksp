import React from 'react';
import { Order } from '../services/orderPickingApi';
import classNames from 'classnames';

interface Props {
    orders: Order[];
    selectedOrderId?: number;
    onOrderSelect: (order: Order) => void;
}

const OrderPickingList: React.FC<Props> = ({ orders, selectedOrderId, onOrderSelect }) => {
    const getStatusColor = (status: Order['status']) => {
        switch (status) {
            case 'pending':
                return 'bg-yellow-100 text-yellow-800';
            case 'in_progress':
                return 'bg-blue-100 text-blue-800';
            case 'completed':
                return 'bg-green-100 text-green-800';
            case 'cancelled':
                return 'bg-red-100 text-red-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    const getPriorityColor = (priority: Order['priority']) => {
        switch (priority) {
            case 'high':
                return 'bg-red-100 text-red-800';
            case 'medium':
                return 'bg-yellow-100 text-yellow-800';
            case 'low':
                return 'bg-green-100 text-green-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    return (
        <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Список заказов</h3>
            </div>
            <div className="divide-y divide-gray-200">
                {orders.map((order) => (
                    <div
                        key={order.id}
                        className={classNames(
                            'px-4 py-4 hover:bg-gray-50 cursor-pointer',
                            selectedOrderId === order.id && 'bg-indigo-50'
                        )}
                        onClick={() => onOrderSelect(order)}
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-medium text-gray-900">{order.orderNumber}</p>
                                <p className="text-sm text-gray-500">{order.createdAt}</p>
                            </div>
                            <div className="flex items-center space-x-2">
                                <span
                                    className={classNames(
                                        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                                        getStatusColor(order.status)
                                    )}
                                >
                                    {order.status === 'pending' && 'Ожидает'}
                                    {order.status === 'in_progress' && 'В работе'}
                                    {order.status === 'completed' && 'Завершен'}
                                    {order.status === 'cancelled' && 'Отменен'}
                                </span>
                                <span
                                    className={classNames(
                                        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                                        getPriorityColor(order.priority)
                                    )}
                                >
                                    {order.priority === 'high' && 'Высокий'}
                                    {order.priority === 'medium' && 'Средний'}
                                    {order.priority === 'low' && 'Низкий'}
                                </span>
                            </div>
                        </div>
                        <div className="mt-2">
                            <p className="text-sm text-gray-500">
                                Товаров: {order.products.length}
                                {order.assignedTo && ` • Сборщик: ${order.assignedTo}`}
                            </p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default OrderPickingList;

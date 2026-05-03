import React from 'react';
import { OrderCollection } from '../models/OrderCollectionModel';

interface Props {
  orders: OrderCollection[];
  onAction: (order: OrderCollection) => void;
}

const statusColor = (status: string) => {
  if (status === 'Pending Collection') return 'bg-yellow-100 text-yellow-800';
  if (status === 'In Progress') return 'bg-blue-100 text-blue-800';
  if (status === 'Completed') return 'bg-green-100 text-green-800';
  return '';
};

const statusLabels: Record<string, string> = {
  'Pending Collection': 'Ожидает сборки',
  'In Progress': 'В процессе',
  Completed: 'Завершено',
};

const OrderCollectionTable: React.FC<Props> = ({ orders, onAction }) => (
  <div className="bg-white shadow rounded-lg">
    <div className="px-4 py-5 border-b">
      <h2 className="text-lg font-medium text-gray-900">Заказы для сборки</h2>
      <p className="text-sm text-gray-500">Найдено заказов: {orders.length}</p>
    </div>
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">
              № Заказа
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-48">
              Клиент
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-64">
              Товары
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">
              Локация
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">
              Статус
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">
              Действия
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {orders.map(order => (
            <tr key={order.id}>
              <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-indigo-700 flex items-center">
                <i className="fas fa-box mr-2 text-indigo-400"></i>
                {order.id}
              </td>
              <td className="px-4 py-4 whitespace-nowrap text-sm">
                <div className="font-medium text-gray-900 truncate">{order.customerName}</div>
                <div className="text-gray-500 truncate">{order.customerEmail}</div>
              </td>
              <td className="px-4 py-4 text-sm">
                <div className="flex flex-col">
                  <span className="inline-flex items-center px-2 py-0.5 rounded bg-indigo-100 text-indigo-700 text-xs font-semibold mb-1">
                    {order.items.length}{' '}
                    {order.items.length === 1
                      ? 'товар'
                      : order.items.length < 5
                        ? 'товара'
                        : 'товаров'}
                  </span>
                  <div className="text-gray-900 truncate">
                    {order.items.map(i => i.name).join(', ')}
                  </div>
                </div>
              </td>
              <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-700">
                <i className="fas fa-map-marker-alt text-red-400 mr-1"></i>
                {order.location}
              </td>
              <td className="px-4 py-4 whitespace-nowrap">
                <span
                  className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    order.status === 'Pending Collection'
                      ? 'bg-yellow-100 text-yellow-800'
                      : order.status === 'In Progress'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-green-100 text-green-800'
                  }`}
                >
                  {statusLabels[order.status] || order.status}
                </span>
              </td>
              <td className="px-4 py-4 whitespace-nowrap text-sm font-medium">
                {order.status === 'Completed' ? (
                  <span className="flex items-center text-gray-400">
                    <i className="fas fa-check-circle mr-1"></i>
                    <span className="hidden sm:inline">Завершено</span>
                  </span>
                ) : (
                  <button
                    className="text-indigo-600 hover:text-indigo-900 flex items-center"
                    onClick={() => onAction(order)}
                  >
                    <i className="fas fa-play mr-1"></i>
                    <span className="hidden sm:inline">
                      {order.status === 'In Progress' ? 'Продолжить' : 'Начать'}
                    </span>
                    <span className="sm:hidden">
                      {order.status === 'In Progress' ? 'Продолжить' : 'Начать'}
                    </span>
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

export default OrderCollectionTable;

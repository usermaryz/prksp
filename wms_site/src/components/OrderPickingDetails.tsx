import React from 'react';
import { Order, OrderProduct } from '../services/orderPickingApi';
import classNames from 'classnames';

interface Props {
  order: Order;
  onProductPicked: (productId: number) => void;
  onStatusChange: (status: Order['status']) => void;
}

const OrderPickingDetails: React.FC<Props> = ({
  order,
  onProductPicked,
  onStatusChange,
}) => {
  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-lg font-medium text-gray-900">Заказ {order.orderNumber}</h2>
            <p className="text-sm text-gray-500">Создан: {order.createdAt}</p>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={order.status}
              onChange={e => onStatusChange(e.target.value as Order['status'])}
              style={{
                padding: '8px',
                border: '1px solid #dee2e6',
                borderRadius: '4px',
                width: '100%'
              }}
            >
              <option value="pending">Ожидает</option>
              <option value="in_progress">В работе</option>
              <option value="completed">Завершен</option>
              <option value="cancelled">Отменен</option>
            </select>
          </div>
        </div>
      </div>

      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Прогресс сбора</span>
          <span>
            {Math.round(
              (order.products.filter(p => p.picked).length / order.products.length) * 100
            )}
            %
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full"
            style={{
              width: `${(order.products.filter(p => p.picked).length / order.products.length) * 100}%`,
            }}
          ></div>
        </div>
      </div>

      <div className="space-y-4">
        {order.products.map(product => (
          <div
            key={product.id}
            className={classNames(
              'p-4 rounded-lg border',
              product.picked ? 'border-green-200 bg-green-50' : 'border-gray-200'
            )}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <img
                  src={product.product.image}
                  alt={product.product.name}
                  className="w-12 h-12 rounded-lg object-cover"
                />
                <div>
                  <h3 className="text-sm font-medium text-gray-900">{product.product.name}</h3>
                  <p className="text-sm text-gray-500">
                    {product.product.brand} • {product.quantity} шт.
                  </p>
                  <p className="text-sm text-gray-500">
                    <i className="fa-solid fa-location-dot text-red-400 mr-1"></i>
                    {product.location}
                  </p>
                </div>
              </div>
              <button
                onClick={() => onProductPicked(product.id)}
                disabled={product.picked}
                className={classNames(
                  'px-4 py-2 rounded-md text-sm font-medium',
                  product.picked
                    ? 'bg-green-100 text-green-800 cursor-not-allowed'
                    : 'bg-indigo-600 text-white hover:bg-indigo-700'
                )}
              >
                {product.picked ? 'Собран' : 'Отметить как собранный'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OrderPickingDetails;

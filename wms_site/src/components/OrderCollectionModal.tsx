import React, { useState } from 'react';
import { observer } from 'mobx-react-lite';
import { OrderCollection } from '../models/OrderCollectionModel';

interface Props {
  order: OrderCollection | null;
  onClose: () => void;
}

const OrderCollectionModal: React.FC<Props> = observer(({ order, onClose }) => {
  const [isCollecting, setIsCollecting] = useState(false);
  const [scannedBarcodes, setScannedBarcodes] = useState<Record<string, string>>({});

  if (!order) return null;

  const handleStartCollection = () => {
    setIsCollecting(true);
  };

  const handleBarcodeScan = (itemName: string, barcode: string) => {
    setScannedBarcodes(prev => ({
      ...prev,
      [itemName]: barcode,
    }));
  };

  const allItemsScanned = order.items.every(item => scannedBarcodes[item.name]);

  return (
    <div className="order-collection-modal fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
      <div className="order-collection-modal__content bg-white rounded-lg shadow-lg w-full max-w-xl p-6 border-2 border-blue-200">
        <h2 className="text-lg font-bold mb-4">Сканирование товара</h2>
        <p className="text-sm text-gray-500 mb-4">
          Отсканируйте штрих-код товара для начала процесса сборки
        </p>
        <div className="bg-gray-50 p-4 rounded-md mb-4">
          <h3 className="text-md font-medium text-gray-900 mb-2">Детали заказа</h3>
          <div className="mb-2">
            <span className="font-semibold">ID заказа:</span> {order.id}
          </div>
          <div className="mb-2">
            <span className="font-semibold">Клиент:</span> {order.customerName} (
            {order.customerEmail})
          </div>
          <div className="mb-2">
            <span className="font-semibold">Локация:</span> {order.location}
          </div>
          <div className="mb-2">
            <span className="font-semibold">Товары:</span>
            <ul className="list-disc ml-6">
              {order.items.map((item, idx) => (
                <li key={idx} className="mb-2">
                  <div className="flex items-center justify-between">
                    <span>
                      {item.name} <span className="text-xs text-gray-500">x{item.quantity}</span>
                    </span>
                    {isCollecting && (
                      <div className="flex items-center space-x-2">
                        <input
                          type="text"
                          value={scannedBarcodes[item.name] || ''}
                          onChange={e => handleBarcodeScan(item.name, e.target.value)}
                          placeholder="Введите штрих-код"
                          className="px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        {scannedBarcodes[item.name] && (
                          <i className="fas fa-check text-green-500"></i>
                        )}
                      </div>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="flex justify-end space-x-3">
          {!isCollecting ? (
            <button
              onClick={handleStartCollection}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
            >
              <i className="fas fa-play mr-2"></i>
              Начать собирать товар
            </button>
          ) : (
            <button
              onClick={onClose}
              disabled={!allItemsScanned}
              className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                allItemsScanned
                  ? 'bg-green-600 hover:bg-green-700'
                  : 'bg-gray-400 cursor-not-allowed'
              }`}
            >
              <i className="fas fa-check mr-2"></i>
              Завершить сборку
            </button>
          )}
          <button
            onClick={onClose}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <i className="fas fa-times mr-2"></i>
            Закрыть
          </button>
        </div>
      </div>
    </div>
  );
});

export default OrderCollectionModal;

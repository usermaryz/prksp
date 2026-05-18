import React from 'react';
import { Product } from '../models/ProductModel';

interface Props {
  product: Product | null;
  packageType: string;
  containerBarcode: string;
  onPackageTypeChange: (type: string) => void;
  onContainerBarcodeChange: (barcode: string) => void;
  onSubmit: () => void;
  onClose: () => void;
  isValid: boolean;
}

const OrderAcceptModal: React.FC<Props> = ({
  product,
  packageType,
  containerBarcode,
  onPackageTypeChange,
  onContainerBarcodeChange,
  onSubmit,
  onClose,
  isValid,
}) => {
  if (!product) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-lg p-6">
        <h2 className="text-lg font-bold mb-4">Прием товара</h2>
        <div className="mb-4">
          <div className="text-sm text-gray-500">Наименование</div>
          <div className="font-medium text-gray-900">{product.name}</div>
          <div className="text-sm text-gray-500 mt-2">Штрих-код</div>
          <div className="font-medium text-gray-900">{product.barcode}</div>
          <div className="text-sm text-gray-500 mt-2">Бренд</div>
          <div className="font-medium text-gray-900">{product.brand}</div>
          <div className="text-sm text-gray-500 mt-2">Категория</div>
          <div className="font-medium text-gray-900">{product.category}</div>
        </div>
        <form
          onSubmit={e => {
            e.preventDefault();
            onSubmit();
          }}
          className="space-y-4"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Тип упаковки</label>
            <div className="relative">
              <select
                value={packageType}
                onChange={e => onPackageTypeChange(e.target.value)}
                style={{
                  padding: '8px',
                  border: '1px solid #dee2e6',
                  borderRadius: '4px',
                  width: '100%'
                }}
              >
                <option value="">Выберите тип</option>
                <option value="Box">Коробка</option>
                <option value="Pallet">Паллета</option>
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                <svg className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="none">
                  <path
                    d="M7 7l3-3 3 3m0 6l-3 3-3-3"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Штрих-код контейнера</label>
            <input
              type="text"
              value={containerBarcode}
              onChange={e => onContainerBarcodeChange(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
              placeholder="Введите штрих-код контейнера"
            />
          </div>
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={!isValid}
              className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${isValid ? 'bg-slate-900 hover:bg-slate-800' : 'bg-gray-400 cursor-not-allowed'}`}
            >
              Принять
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
export default OrderAcceptModal;


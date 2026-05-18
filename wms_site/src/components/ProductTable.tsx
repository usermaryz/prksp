import React from 'react';
import { Product } from '../models/ProductModel';
import classNames from 'classnames';

interface Props {
  products: Product[];
  onAccept: (product: Product) => void;
}

const categoryLabels: Record<string, string> = {
  Electronics: 'Электроника',
  'Health & Fitness': 'Здоровье и фитнес',
  'Computer Accessories': 'Компьютерные аксессуары',
  'Kitchen Appliances': 'Кухонная техника',
  Footwear: 'Обувь',
  Wearables: 'Носимая электроника',
  'Fitness Equipment': 'Фитнес-оборудование',
  'Storage Devices': 'Устройства хранения',
};

const categoryColors: Record<string, string> = {
  Electronics: 'bg-blue-100 text-blue-800',
  'Health & Fitness': 'bg-green-100 text-green-800',
  'Computer Accessories': 'bg-slate-100 text-slate-800',
  'Kitchen Appliances': 'bg-yellow-100 text-yellow-800',
  Footwear: 'bg-pink-100 text-pink-800',
  Wearables: 'bg-purple-100 text-purple-800',
  'Fitness Equipment': 'bg-orange-100 text-orange-800',
  'Storage Devices': 'bg-gray-100 text-gray-800',
};

const countryLabels: Record<string, string> = {
  China: 'Китай',
  USA: 'США',
  Taiwan: 'Тайвань',
  Australia: 'Австралия',
  Canada: 'Канада',
  'South Korea': 'Южная Корея',
  // Добавьте другие страны по необходимости
};

const ProductTable: React.FC<Props> = ({ products, onAccept }) => {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Штрих-код
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Наименование
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Бренд
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Категория
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Страна
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Статус
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Действия
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {products.map(product => (
            <tr key={product.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {product.barcode}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{product.name}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{product.brand}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span
                  className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${categoryColors[product.category] || 'bg-gray-100 text-gray-800'}`}
                >
                  {categoryLabels[product.category] || product.category}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {countryLabels[product.country] || product.country}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span
                  className={classNames(
                    'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                    {
                      'bg-yellow-100 text-yellow-800': product.status === 'pending',
                      'bg-blue-100 text-blue-800': product.status === 'processing',
                      'bg-green-100 text-green-800': product.status === 'completed',
                    }
                  )}
                >
                  {product.status === 'pending' && 'Ожидает'}
                  {product.status === 'processing' && 'В обработке'}
                  {product.status === 'completed' && 'Завершен'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                {product.status !== 'completed' ? (
                  <button
                    onClick={() => onAccept(product)}
                    className="text-white bg-slate-900 hover:bg-slate-800 px-4 py-2 rounded-md text-sm font-medium"
                  >
                    Принять
                  </button>
                ) : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
export default ProductTable;


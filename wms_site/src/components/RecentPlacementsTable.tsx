import React from 'react';
import { Placement } from '../models/PlacementModel';

interface Props {
  placements: Placement[];
  onAccept?: (placement: Placement) => void;
}

const statusStyles: Record<string, string> = {
  'В обработке': 'bg-yellow-100 text-yellow-800',
  'Завершен': 'bg-green-100 text-green-800',
  'Ожидает размещения': 'bg-blue-100 text-blue-800'
};

const RecentPlacementsTable: React.FC<Props> = ({ placements, onAccept }) => (
  <div className="overflow-x-auto">
    <table className="placement-table bg-white shadow rounded-lg">
      <thead className="bg-gray-50">
        <tr>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Товар
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Штрих-код
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Локация
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Кол-во
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Время
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Статус
          </th>
          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Действия
          </th>
        </tr>
      </thead>
      <tbody className="bg-white divide-y divide-gray-200">
        {placements.map(placement => (
          <tr key={placement.id}>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              {placement.productName}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {placement.barcode}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 flex items-center gap-2">
              <i className="fa-solid fa-location-dot text-red-400 text-base"></i>
              {placement.location}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {placement.quantity}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {placement.timestamp}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm">
              <span
                className={`inline-block px-3 py-1 rounded-full font-semibold text-xs ${statusStyles[placement.status] || 'bg-gray-100 text-gray-800'}`}
              >
                {placement.status}
              </span>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {placement.status === 'Ожидает размещения' && (
                <button
                  onClick={() => onAccept?.(placement)}
                  className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-slate-900 hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-900"
                >

                  Принять
                </button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export default RecentPlacementsTable;

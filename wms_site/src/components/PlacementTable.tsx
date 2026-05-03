import React from 'react';
import { Placement } from '../models/PlacementModel';

interface Props {
  placements: Placement[];
  search: string;
  setSearch: (val: string) => void;
}

const PlacementTable: React.FC<Props> = ({ placements, search, setSearch }) => (
  <div className="placement-table bg-white shadow rounded-lg">
    <div className="placement-table__header px-4 py-5 border-b flex justify-between items-center">
      <div>
        <h2 className="text-lg font-medium text-gray-900">Recently Placed Products</h2>
        <p className="text-sm text-gray-500">Last 10 product placements</p>
      </div>
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <i className="fas fa-search text-gray-400"></i>
        </div>
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md bg-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          placeholder="Search placements"
        />
      </div>
    </div>
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {[
              'Product',
              'Barcode',
              'Location',
              'Timestamp',
              'Quantity',
              'Placed By',
              'Status',
              'Actions',
            ].map(h => (
              <th
                key={h}
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {h}
              </th>
            ))}
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
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {placement.location}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {placement.timestamp}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {placement.quantity}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {placement.placedBy}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                  {placement.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button className="text-indigo-600 hover:text-indigo-900 mr-3">
                  <i className="fas fa-eye"></i>
                </button>
                <button className="text-indigo-600 hover:text-indigo-900">
                  <i className="fas fa-print"></i>
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200">
      <div>
        <p className="text-sm text-gray-700">
          Showing <span className="font-medium">1</span> to{' '}
          <span className="font-medium">{placements.length}</span> of{' '}
          <span className="font-medium">{placements.length}</span> results
        </p>
      </div>
      <div>
        <nav
          className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px"
          aria-label="Pagination"
        >
          <a
            href="#"
            className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
          >
            <span className="sr-only">Previous</span>
            <i className="fas fa-chevron-left"></i>
          </a>
          <a
            href="#"
            aria-current="page"
            className="z-10 bg-indigo-50 border-indigo-500 text-indigo-600 relative inline-flex items-center px-4 py-2 border text-sm font-medium"
          >
            1
          </a>
          <a
            href="#"
            className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
          >
            <span className="sr-only">Next</span>
            <i className="fas fa-chevron-right"></i>
          </a>
        </nav>
      </div>
    </div>
  </div>
);

export default PlacementTable;

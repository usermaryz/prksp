import React from 'react';
import { observer } from 'mobx-react-lite';
import { ProductPlacementViewModel } from '../viewmodels/ProductPlacementViewModel';
import Navigation from '../components/Navigation';
import Card from '../components/common/Card';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import Table from '../components/common/Table';
import PlacementModal from '../components/ProductModal';
import { Placement } from '../models/PlacementModel';

const vm = new ProductPlacementViewModel();

const ProductPlacementPage: React.FC = observer(() => {
  const columns = [
    { header: 'Товар', accessor: 'productName' as keyof Placement },
    { header: 'Штрих-код', accessor: 'barcode' as keyof Placement },
    { header: 'Расположение', accessor: 'location' as keyof Placement },
    { header: 'Время', accessor: 'timestamp' as keyof Placement },
    { header: 'Кол-во', accessor: 'quantity' as keyof Placement },
    {
      header: 'Статус',
      accessor: (item: Placement) => (
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium ${item.status === 'Завершен'
            ? 'bg-green-100 text-green-800'
            : item.status === 'В обработке'
              ? 'bg-yellow-100 text-yellow-800'
              : 'bg-gray-100 text-gray-800'
            }`}
        >
          {item.status}
        </span>
      ),
    },
    {
      header: 'Действия',
      accessor: (item: Placement) => (
        item.status !== 'Завершен' ? (
          <button
            onClick={(e: React.MouseEvent) => {
              e.stopPropagation();
              vm.openModal();
              vm.setBarcodeInput(item.barcode);
              vm.scanProduct();
            }}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200 text-sm font-medium shadow-sm hover:shadow-md"
          >
            Разместить
          </button>
        ) : null
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation active="Размещение товара" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Размещение товара</h1>
          <p className="mt-1 text-sm text-gray-500">
            Управление размещением товаров на складе
          </p>
        </div>

        <div className="mb-6">
          <Input
            type="text"
            value={vm.search}
            onChange={vm.setSearch}
            placeholder="Поиск по товару или штрих-коду..."
            className="max-w-xl"
          />
        </div>

        <Card
          title="Недавние размещения"
          subtitle="Последние 10 размещений товаров"
        >
          <Table
            columns={columns}
            data={vm.filteredPlacements}
            onRowClick={(placement) => vm.acceptPlacement(placement)}
          />
        </Card>


      </div>

      {vm.showModal && (
        <PlacementModal
          vm={vm}
          onClose={() => vm.closeModal()}
          onConfirm={() => vm.confirmPlacement('Текущий пользователь')}
        />
      )}
    </div>
  );
});

export default ProductPlacementPage;

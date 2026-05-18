import React from 'react';
import { observer } from 'mobx-react-lite';
import { ProductPlacementViewModel } from '../viewmodels/ProductPlacementViewModel';
import AppLayout from '../components/layout/AppLayout';
import PageHeader from '../components/layout/PageHeader';
import { btnPrimary } from '../components/layout/pageStyles';
import Card from '../components/common/Card';
import Input from '../components/common/Input';
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
          className={`px-2 py-1 rounded-full text-xs font-medium ${
            item.status === 'Завершен'
              ? 'bg-green-100 text-green-800'
              : item.status === 'В обработке'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-slate-100 text-slate-800'
          }`}
        >
          {item.status}
        </span>
      ),
    },
    {
      header: 'Действия',
      accessor: (item: Placement) =>
        item.status !== 'Завершен' ? (
          <button
            type="button"
            onClick={(e: React.MouseEvent) => {
              e.stopPropagation();
              vm.openModal();
              vm.setBarcodeInput(item.barcode);
              vm.scanProduct();
            }}
            className={btnPrimary}
          >
            Разместить
          </button>
        ) : null,
    },
  ];

  return (
    <AppLayout>
      <PageHeader title="Склад" subtitle="Управление размещением товаров на складе" />

      <div className="mb-6">
        <Input
          type="text"
          value={vm.search}
          onChange={vm.setSearch}
          placeholder="Поиск по товару или штрих-коду..."
          className="max-w-xl"
        />
      </div>

      <Card title="Недавние размещения" subtitle="Последние 10 размещений товаров">
        <Table
          columns={columns}
          data={vm.filteredPlacements}
          onRowClick={placement => vm.acceptPlacement(placement)}
        />
      </Card>

      {vm.showModal && (
        <PlacementModal
          vm={vm}
          onClose={() => vm.closeModal()}
          onConfirm={() => vm.confirmPlacement('Текущий пользователь')}
        />
      )}
    </AppLayout>
  );
});

export default ProductPlacementPage;

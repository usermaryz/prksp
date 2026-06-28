import React, { useEffect, useState } from 'react';
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

const ProductPlacementPage: React.FC = observer(() => {
  const [vm] = useState(() => new ProductPlacementViewModel());

  useEffect(() => {
    void vm.loadFromApi();
  }, [vm]);

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

      <div className="mb-6 flex flex-col sm:flex-row gap-4 sm:items-center sm:justify-between">
        <Input
          type="text"
          value={vm.search}
          onChange={vm.setSearch}
          placeholder="Поиск по товару или штрих-коду..."
          className="max-w-xl"
        />
        <button type="button" onClick={() => vm.openModal()} className={btnPrimary}>
          Новое размещение
        </button>
      </div>

      {vm.error && (
        <div className="mb-4 rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">{vm.error}</div>
      )}

      <Card title="Недавние размещения" subtitle="Последние 10 размещений товаров">
        {vm.loading ? (
          <p className="px-6 py-8 text-sm text-slate-500">Загрузка данных склада...</p>
        ) : vm.filteredPlacements.length === 0 ? (
          <p className="px-6 py-8 text-sm text-slate-500">Нет размещений. Нажмите «Новое размещение».</p>
        ) : (
          <Table
            columns={columns}
            data={vm.filteredPlacements}
            onRowClick={placement => vm.acceptPlacement(placement)}
          />
        )}
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

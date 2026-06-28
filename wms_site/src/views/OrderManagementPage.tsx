import React, { useEffect, useState } from 'react';
import { observer } from 'mobx-react-lite';
import { OrderManagementViewModel } from '../viewmodels/OrderManagementViewModel';
import ProductTable from '../components/ProductTable';
import OrderAcceptModal from '../components/OrderAcceptModal';
import AppLayout from '../components/layout/AppLayout';
import PageHeader from '../components/layout/PageHeader';
import { pageCard, pageCardHeader, searchInputClass } from '../components/layout/pageStyles';

const OrderManagementPage: React.FC = observer(() => {
  const [vm] = useState(() => new OrderManagementViewModel());

  useEffect(() => {
    void vm.loadProducts();
  }, [vm]);

  return (
    <AppLayout>
      <PageHeader title="Заказы" subtitle="Просмотр и управление заказами" />

      <div className="mb-6">
        <input
          type="text"
          placeholder="Поиск заказов..."
          value={vm.searchQuery}
          onChange={e => vm.setSearchQuery(e.target.value)}
          className={searchInputClass}
        />
      </div>

      {vm.error && (
        <div className="mb-4 rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">{vm.error}</div>
      )}

      <div className={pageCard}>
        <div className={pageCardHeader}>
          <h2 className="text-lg font-semibold text-slate-900">Активные заказы</h2>
          <p className="text-sm text-slate-500 mt-1">Список заказов, требующих обработки</p>
        </div>
        {vm.loading ? (
          <p className="px-6 py-8 text-sm text-slate-500">Загрузка...</p>
        ) : (
          <ProductTable products={vm.filteredProducts} onAccept={order => vm.handleAccept(order)} />
        )}
      </div>

      {vm.showModal && (
        <OrderAcceptModal
          product={vm.selectedProduct}
          packageType={vm.packageType}
          containerBarcode={vm.containerBarcode}
          onPackageTypeChange={type => vm.setPackageType(type)}
          onContainerBarcodeChange={barcode => vm.setContainerBarcode(barcode)}
          onSubmit={() => vm.handleModalSubmit()}
          onClose={() => vm.setShowModal(false)}
          isValid={vm.isFormValid}
        />
      )}
    </AppLayout>
  );
});

export default OrderManagementPage;

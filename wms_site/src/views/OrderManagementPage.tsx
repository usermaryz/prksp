import React from 'react';
import { observer } from 'mobx-react-lite';
import { OrderManagementViewModel } from '../viewmodels/OrderManagementViewModel';
import Navigation from '../components/Navigation';
import ProductTable from '../components/ProductTable';
import OrderAcceptModal from '../components/OrderAcceptModal';

const vm = new OrderManagementViewModel();

const OrderManagementPage: React.FC = observer(() => (
  <div style={{ backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
    <Navigation active="Управление заказами" />
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '20px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '5px' }}>Управление заказами</h1>
        <p style={{ color: '#666', fontSize: '14px' }}>Просмотр и управление заказами</p>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Поиск заказов..."
          value={vm.searchQuery}
          onChange={e => vm.setSearchQuery(e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            border: '1px solid #dee2e6',
            borderRadius: '4px'
          }}
        />
      </div>

      <div style={{ backgroundColor: 'white', borderRadius: '4px', border: '1px solid #dee2e6' }}>
        <div style={{ padding: '15px', borderBottom: '1px solid #dee2e6' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '5px' }}>Активные заказы</h2>
          <p style={{ color: '#666', fontSize: '14px' }}>Список заказов, требующих обработки</p>
        </div>
        <ProductTable
          products={vm.filteredProducts}
          onAccept={order => vm.handleAccept(order)}
        />
      </div>
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
  </div>
));

export default OrderManagementPage;

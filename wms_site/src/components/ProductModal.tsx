import React from 'react';
import { observer } from 'mobx-react-lite';
import { ProductPlacementViewModel } from '../viewmodels/ProductPlacementViewModel';
import Modal from './common/Modal';
import Input from './common/Input';
import Button from './common/Button';
import Select from './common/Select';

interface ProductModalProps {
  vm: ProductPlacementViewModel;
  onClose: () => void;
  onConfirm: () => void;
}

const ProductModal: React.FC<ProductModalProps> = observer(({ vm, onClose, onConfirm }) => {
  return (
    <Modal
      isOpen={vm.showModal}
      onClose={onClose}
      title="Размещение товара"
      footer={
        <div className="flex gap-3">
          <Button variant="secondary" onClick={onClose}>
            Отмена
          </Button>
          <Button
            variant="primary"
            onClick={onConfirm}
            disabled={!vm.isFormValid}
            className={!vm.isFormValid ? '' : 'bg-slate-900 hover:bg-slate-800'}
          >
            Подтвердить
          </Button>
        </div>
      }
    >
      <div className="space-y-4">
        <Input
          type="text"
          value={vm.barcodeInput}
          onChange={vm.setBarcodeInput}
          placeholder="Введите штрих-код"
          label="Штрих-код"
          required
        />

        {vm.scannedProduct && (
          <div className="bg-gray-50 p-4 rounded-md">
            <h4 className="font-medium text-gray-900">{vm.scannedProduct.name}</h4>
            <p className="text-sm text-gray-500">Бренд: {vm.scannedProduct.brand}</p>
            <p className="text-sm text-gray-500">Категория: {vm.scannedProduct.category}</p>
          </div>
        )}

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Select
            value={vm.selectedZone}
            onChange={(value) => {
              console.log('Zone select onChange:', value);
              vm.setSelectedZone(value);
            }}
            options={vm.zones.map(zone => ({ value: zone.id, label: zone.name }))}
            label="Зона"
            placeholder="Выберите зону"
            required
          />

          <Select
            value={vm.selectedAisle}
            onChange={(value) => {
              console.log('Aisle select onChange:', value);
              vm.setSelectedAisle(value);
            }}
            options={vm.filteredAisles.map(aisle => ({ value: aisle.id, label: aisle.name }))}
            label="Проход"
            placeholder="Выберите проход"
            disabled={!vm.selectedZone}
            required
          />

          <Select
            value={vm.selectedShelf}
            onChange={(value) => {
              console.log('Shelf select onChange:', value);
              vm.setSelectedShelf(value);
            }}
            options={vm.filteredShelves.map(shelf => ({ value: shelf.id, label: shelf.name }))}
            label="Полка"
            placeholder="Выберите полку"
            disabled={!vm.selectedAisle}
            required
          />

          <Input
            type="number"
            value={vm.quantity}
            onChange={vm.setQuantity}
            label="Количество"
            required
          />
        </div>

        <Select
          value={vm.storageType}
          onChange={vm.setStorageType}
          options={[
            { value: 'Box', label: 'Коробка' },
            { value: 'Pallet', label: 'Палета' },
            { value: 'Shelf', label: 'Полка' },
          ]}
          label="Тип хранения"
        />

        <Input
          type="text"
          value={vm.notes}
          onChange={vm.setNotes}
          placeholder="Дополнительные заметки"
          label="Заметки"
        />
      </div>
    </Modal>
  );
});

export default ProductModal;

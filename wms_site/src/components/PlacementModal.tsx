import React from 'react';
import { observer } from 'mobx-react-lite';
import { ProductPlacementViewModel } from '../viewmodels/ProductPlacementViewModel';

interface Props {
  vm: ProductPlacementViewModel;
  onConfirm: () => void;
  onClose: () => void;
}

const PlacementModal: React.FC<Props> = observer(({ vm, onConfirm, onClose }) => {
  if (!vm.showModal) return null;

  return (
    <div className="placement-modal fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
      <div className="placement-modal__content bg-white rounded-lg shadow-lg w-full max-w-2xl p-6">
        {!vm.scannedProduct ? (
          <>
            <h2 className="text-lg font-bold mb-4">Сканирование товара</h2>
            <p className="text-sm text-gray-500 mb-4">
              Отсканируйте штрих-код товара для начала процесса размещения
            </p>
            <div className="mb-4">
              <input
                type="text"
                value={vm.barcodeInput}
                onChange={e => vm.setBarcodeInput(e.target.value)}
                placeholder="Введите или отсканируйте штрих-код"
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                onKeyPress={e => {
                  if (e.key === 'Enter') {
                    vm.scanProduct();
                  }
                }}
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
                onClick={() => vm.scanProduct()}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-slate-900 hover:bg-slate-800"
              >
                Сканировать
              </button>
            </div>
          </>
        ) : (
          <>
            <h2 className="text-lg font-bold mb-4">Размещение товара</h2>
            <div className="bg-gray-50 p-4 rounded-md mb-4">
              <h3 className="text-md font-medium text-gray-900 mb-2">Детали отсканированного товара</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Наименование</p>
                  <p className="text-sm font-medium text-gray-900">{vm.scannedProduct.name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Штрих-код</p>
                  <p className="text-sm font-medium text-gray-900">{vm.scannedProduct.barcode}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Бренд</p>
                  <p className="text-sm font-medium text-gray-900">{vm.scannedProduct.brand}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Категория</p>
                  <p className="text-sm font-medium text-gray-900">{vm.scannedProduct.category}</p>
                </div>
              </div>
            </div>
            <form
              onSubmit={e => {
                e.preventDefault();
                onConfirm();
              }}
              className="space-y-6"
            >
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label htmlFor="zone" className="block text-sm font-medium text-gray-700">
                    Зона
                  </label>
                  <div className="mt-1 relative">
                    <select
                      id="zone"
                      value={vm.selectedZone}
                      onChange={e => vm.setSelectedZone(e.target.value)}
                      style={{
                        padding: '8px',
                        border: '1px solid #dee2e6',
                        borderRadius: '4px',
                        width: '100%'
                      }}
                    >
                      <option value="" className="py-2">
                        Выберите зону
                      </option>
                      {vm.zones.map(zone => (
                        <option key={zone.id} value={zone.id} className="py-2">
                          {zone.name} - {zone.capacity}% занято
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div>
                  <label htmlFor="aisle" className="block text-sm font-medium text-gray-700">
                    Шкаф
                  </label>
                  <div className="mt-1 relative">
                    <select
                      id="aisle"
                      value={vm.selectedAisle}
                      onChange={e => vm.setSelectedAisle(e.target.value)}
                      disabled={!vm.selectedZone}
                      style={{
                        padding: '8px',
                        border: '1px solid #dee2e6',
                        borderRadius: '4px',
                        width: '100%',
                        backgroundColor: !vm.selectedZone ? '#f8f9fa' : 'white'
                      }}
                    >
                      <option value="" className="py-2">
                        Выберите шкаф
                      </option>
                      {vm.filteredAisles.map(aisle => (
                        <option key={aisle.id} value={aisle.id} className="py-2">
                          {aisle.name} - {aisle.capacity}% занято
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div>
                  <label htmlFor="shelf" className="block text-sm font-medium text-gray-700">
                    Полка
                  </label>
                  <div className="mt-1 relative">
                    <select
                      id="shelf"
                      value={vm.selectedShelf}
                      onChange={e => vm.setSelectedShelf(e.target.value)}
                      disabled={!vm.selectedAisle}
                      style={{
                        padding: '8px',
                        border: '1px solid #dee2e6',
                        borderRadius: '4px',
                        width: '100%',
                        backgroundColor: !vm.selectedAisle ? '#f8f9fa' : 'white'
                      }}
                    >
                      <option value="" className="py-2">
                        Выберите полку
                      </option>
                      {vm.filteredShelves.map(shelf => (
                        <option key={shelf.id} value={shelf.id} className="py-2">
                          {shelf.name} - {shelf.capacity}% занято
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="quantity" className="block text-sm font-medium text-gray-700">
                    Количество
                  </label>
                  <div className="mt-1">
                    <input
                      type="number"
                      min="1"
                      id="quantity"
                      value={vm.quantity}
                      onChange={e => vm.setQuantity(e.target.value)}
                      className="shadow-sm focus:ring-slate-900 focus:border-slate-900 block w-full sm:text-sm border-gray-300 rounded-md"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Тип хранения</label>
                  <div className="mt-2 space-x-4 flex items-center">
                    <div className="flex items-center">
                      <input
                        id="box"
                        name="storageType"
                        type="radio"
                        checked={vm.storageType === 'Box'}
                        onChange={() => vm.setStorageType('Box')}
                        className="focus:ring-slate-900 h-4 w-4 text-slate-700 border-gray-300"
                      />
                      <label htmlFor="box" className="ml-2 block text-sm font-medium text-gray-700">
                        Коробка
                      </label>
                    </div>
                    <div className="flex items-center">
                      <input
                        id="pallet"
                        name="storageType"
                        type="radio"
                        checked={vm.storageType === 'Pallet'}
                        onChange={() => vm.setStorageType('Pallet')}
                        className="focus:ring-slate-900 h-4 w-4 text-slate-700 border-gray-300"
                      />
                      <label htmlFor="pallet" className="ml-2 block text-sm font-medium text-gray-700">
                        Палета
                      </label>
                    </div>
                  </div>
                </div>
              </div>
              <div>
                <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
                  Примечание (необязательно)
                </label>
                <div className="mt-1">
                  <textarea
                    id="notes"
                    rows={3}
                    value={vm.notes}
                    onChange={e => vm.setNotes(e.target.value)}
                    className="shadow-sm focus:ring-slate-900 focus:border-slate-900 block w-full sm:text-sm border-gray-300 rounded-md"
                    placeholder="Добавьте инструкции или примечания к размещению"
                  ></textarea>
                </div>
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-900 cursor-pointer"
                >
                  <i className="fas fa-times mr-2"></i>
                  Очистить форму
                </button>
                <button
                  type="submit"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-slate-900 hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-900 cursor-pointer"
                >
                  <i className="fas fa-check mr-2"></i>
                  Подтвердить размещение
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
});

export default PlacementModal;

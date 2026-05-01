import { makeAutoObservable } from 'mobx';
import { Product } from '../models/ProductModel';
import { Placement } from '../models/PlacementModel';
import { Zone } from '../models/ZoneModel';
import { Aisle } from '../models/AisleModel';
import { Shelf } from '../models/ShelfModel';

export class ProductPlacementViewModel {
  barcodeInput = '';
  selectedZone = '';
  selectedAisle = '';
  selectedShelf = '';
  quantity = '1';
  notes = '';
  storageType = 'Box';
  scannedProduct: Product | null = null;
  showModal = false;
  errorMessage = '';
  showError = false;
  showSuccess = false;
  recentPlacements: Placement[] = [];
  search = '';

  zones: Zone[] = [
    { id: 'A', name: 'Зона A', capacity: 85 },
    { id: 'B', name: 'Зона B', capacity: 65 },
    { id: 'C', name: 'Зона C', capacity: 45 },
    { id: 'D', name: 'Зона D', capacity: 25 },
  ];
  aisles: Aisle[] = [
    { id: 'A1', zoneId: 'A', name: 'Проход 1', capacity: 90 },
    { id: 'A2', zoneId: 'A', name: 'Проход 2', capacity: 80 },
    { id: 'A3', zoneId: 'A', name: 'Проход 3', capacity: 75 },
    { id: 'B1', zoneId: 'B', name: 'Проход 1', capacity: 70 },
    { id: 'B2', zoneId: 'B', name: 'Проход 2', capacity: 60 },
    { id: 'C1', zoneId: 'C', name: 'Проход 1', capacity: 50 },
    { id: 'C2', zoneId: 'C', name: 'Проход 2', capacity: 40 },
    { id: 'D1', zoneId: 'D', name: 'Проход 1', capacity: 30 },
    { id: 'D2', zoneId: 'D', name: 'Проход 2', capacity: 20 },
  ];
  shelves: Shelf[] = [
    { id: 'A1-1', aisleId: 'A1', name: 'Полка 1', capacity: 95 },
    { id: 'A1-2', aisleId: 'A1', name: 'Полка 2', capacity: 85 },
    { id: 'A2-1', aisleId: 'A2', name: 'Полка 1', capacity: 75 },
    { id: 'A2-2', aisleId: 'A2', name: 'Полка 2', capacity: 65 },
    { id: 'B1-1', aisleId: 'B1', name: 'Полка 1', capacity: 55 },
    { id: 'B1-2', aisleId: 'B1', name: 'Полка 2', capacity: 45 },
    { id: 'B2-1', aisleId: 'B2', name: 'Полка 1', capacity: 35 },
    { id: 'B2-2', aisleId: 'B2', name: 'Полка 2', capacity: 25 },
  ];

  // Тестовые данные для продуктов
  products: Product[] = [
    {
      id: 1,
      name: 'Беспроводные наушники',
      barcode: 'PRD12345',
      brand: 'Sony',
      country: 'Япония',
      category: 'Электроника',
      image: 'https://example.com/headphones.jpg',
      weight: '250g',
      dimensions: '10x5x3cm'
    },
    {
      id: 2,
      name: 'Белковый порошок',
      barcode: 'PRD23456',
      brand: 'Optimum Nutrition',
      country: 'США',
      category: 'Спортивное питание',
      image: 'https://example.com/protein.jpg',
      weight: '2kg',
      dimensions: '20x15x10cm'
    },
    {
      id: 3,
      name: 'Механическая клавиатура',
      barcode: 'PRD34567',
      brand: 'Logitech',
      country: 'Швейцария',
      category: 'Периферия',
      image: 'https://example.com/keyboard.jpg',
      weight: '1.2kg',
      dimensions: '45x15x3cm'
    }
  ];

  constructor() {
    makeAutoObservable(this);
    this.recentPlacements = [
      {
        id: 1,
        productName: 'Беспроводные наушники',
        barcode: 'PRD12345',
        location: 'Зона A, Шкаф 2, Полка 1',
        timestamp: '2025-05-05 09:15:23',
        quantity: 5,
        status: 'Завершен',
      },
      {
        id: 2,
        productName: 'Белковый порошок',
        barcode: 'PRD23456',
        location: 'Зона B, Шкаф 1, Полка 2',
        timestamp: '2025-05-05 08:42:11',
        quantity: 10,
        status: 'В обработке',
      },
      {
        id: 3,
        productName: 'Механическая клавиатура',
        barcode: 'PRD34567',
        location: 'Зона A, Шкаф 3, Полка 1',
        timestamp: '2025-05-04 16:37:45',
        quantity: 3,
        status: 'Ожидает размещения',
      },
      {
        id: 4,
        productName: 'Кофеварка',
        barcode: 'PRD45678',
        location: 'Зона C, Шкаф 1, Полка 1',
        timestamp: '2025-05-04 14:22:09',
        quantity: 2,
        status: 'В обработке',
      },
      {
        id: 5,
        productName: 'Беговые кроссовки',
        barcode: 'PRD56789',
        location: 'Зона B, Шкаф 2, Полка 1',
        timestamp: '2025-05-04 11:05:37',
        quantity: 8,
        status: 'Ожидает размещения',
      },
    ];
  }

  get filteredPlacements() {
    if (!this.search) return this.recentPlacements;
    return this.recentPlacements.filter(
      p =>
        p.productName.toLowerCase().includes(this.search.toLowerCase()) ||
        p.barcode.toLowerCase().includes(this.search.toLowerCase())
    );
  }

  get filteredAisles() {
    if (!this.selectedZone) return [];
    return this.aisles.filter(a => a.zoneId === this.selectedZone);
  }

  get filteredShelves() {
    if (!this.selectedAisle) return [];
    return this.shelves.filter(s => s.aisleId === this.selectedAisle);
  }

  get isFormValid() {
    return (
      this.scannedProduct &&
      this.selectedZone &&
      this.selectedAisle &&
      this.selectedShelf &&
      this.quantity &&
      parseInt(this.quantity) > 0
    );
  }

  setBarcodeInput(value: string) {
    this.barcodeInput = value;
  }

  setSelectedZone(value: string) {
    console.log('Setting zone:', value);
    this.selectedZone = value;
    this.selectedAisle = '';
    this.selectedShelf = '';
    console.log('Current state:', {
      selectedZone: this.selectedZone,
      filteredAisles: this.filteredAisles
    });
  }

  setSelectedAisle(value: string) {
    console.log('Setting aisle:', value);
    this.selectedAisle = value;
    this.selectedShelf = '';
    console.log('Current state:', {
      selectedAisle: this.selectedAisle,
      filteredShelves: this.filteredShelves
    });
  }

  setSelectedShelf(value: string) {
    console.log('Setting shelf:', value);
    this.selectedShelf = value;
    console.log('Current state:', {
      selectedShelf: this.selectedShelf
    });
  }

  setQuantity(value: string) {
    this.quantity = value;
  }

  setNotes(value: string) {
    this.notes = value;
  }

  setStorageType(value: string) {
    this.storageType = value;
  }

  setSearch(value: string) {
    this.search = value;
  }

  openModal() {
    this.showModal = true;
    this.scannedProduct = null;
    this.barcodeInput = '';
  }

  closeModal() {
    this.showModal = false;
    this.scannedProduct = null;
    this.barcodeInput = '';
    this.selectedZone = '';
    this.selectedAisle = '';
    this.selectedShelf = '';
    this.quantity = '1';
    this.notes = '';
    this.storageType = 'Box';
  }

  scanProduct() {
    if (!this.barcodeInput.trim()) {
      this.showError = true;
      this.errorMessage = 'Введите валидный штрих-код';
      setTimeout(() => (this.showError = false), 3000);
      return;
    }
    const product = this.products.find(p => p.barcode === this.barcodeInput);
    if (product) {
      this.scannedProduct = product;
      this.showSuccess = true;
      setTimeout(() => (this.showSuccess = false), 2000);
    } else {
      this.showError = true;
      this.errorMessage = 'Продукт не найден. Пожалуйста, попробуйте снова.';
      setTimeout(() => (this.showError = false), 3000);
    }
  }

  confirmPlacement(user: string) {
    if (
      !this.scannedProduct ||
      !this.selectedZone ||
      !this.selectedAisle ||
      !this.selectedShelf ||
      !this.quantity
    ) {
      this.showError = true;
      this.errorMessage = 'Пожалуйста, заполните все обязательные поля';
      setTimeout(() => (this.showError = false), 3000);
      return;
    }
    const statuses: ('Завершен' | 'В обработке' | 'Ожидает размещения')[] = ['Завершен', 'В обработке', 'Ожидает размещения'];
    const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
    const newPlacement: Placement = {
      id: Date.now(),
      productName: this.scannedProduct.name,
      barcode: this.scannedProduct.barcode,
      location: `Zone ${this.selectedZone}, Aisle ${this.selectedAisle.split('-')[1]}, Shelf ${this.selectedShelf.split('-')[1]}`,
      timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
      quantity: parseInt(this.quantity),
      status: randomStatus,
    };
    this.recentPlacements = [newPlacement, ...this.recentPlacements].slice(0, 10);
    this.closeModal();
    this.showSuccess = true;
    setTimeout(() => (this.showSuccess = false), 2000);
  }

  acceptPlacement(placement: Placement) {
    // Находим продукт по штрих-коду
    const product = this.products.find(p => p.barcode === placement.barcode);
    if (product) {
      this.scannedProduct = product;
      this.barcodeInput = product.barcode;
      this.showModal = true;
    }
  }
}

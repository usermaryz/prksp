import { makeAutoObservable, runInAction } from 'mobx';
import { Product } from '../models/ProductModel';
import { Placement } from '../models/PlacementModel';
import { Zone } from '../models/ZoneModel';
import { Aisle } from '../models/AisleModel';
import { Shelf } from '../models/ShelfModel';
import { placementApi } from '../services/placementApi';

const defaultAisles: Aisle[] = [
  { id: 'A1', zoneId: 'A', name: 'Проход 1', capacity: 90 },
  { id: 'A2', zoneId: 'A', name: 'Проход 2', capacity: 80 },
  { id: 'B1', zoneId: 'B', name: 'Проход 1', capacity: 70 },
  { id: 'B2', zoneId: 'B', name: 'Проход 2', capacity: 60 },
  { id: 'C1', zoneId: 'C', name: 'Проход 1', capacity: 50 },
];

const defaultShelves: Shelf[] = [
  { id: 'A1-1', aisleId: 'A1', name: 'Полка 1', capacity: 95 },
  { id: 'A1-2', aisleId: 'A1', name: 'Полка 2', capacity: 85 },
  { id: 'A2-1', aisleId: 'A2', name: 'Полка 1', capacity: 75 },
  { id: 'B1-1', aisleId: 'B1', name: 'Полка 1', capacity: 55 },
  { id: 'B2-1', aisleId: 'B2', name: 'Полка 1', capacity: 35 },
  { id: 'C1-1', aisleId: 'C1', name: 'Полка 1', capacity: 45 },
];

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
  loading = false;
  error: string | null = null;

  products: Product[] = [];
  zones: Zone[] = [];
  aisles: Aisle[] = defaultAisles;
  shelves: Shelf[] = defaultShelves;

  constructor() {
    makeAutoObservable(this);
    void this.loadFromApi();
  }

  async loadFromApi() {
    this.loading = true;
    this.error = null;
    try {
      const [products, apiZones] = await Promise.all([
        placementApi.getProducts(),
        placementApi.getZones(),
      ]);
      runInAction(() => {
        this.products = products;
        this.zones = apiZones.map(z => ({
          id: String(z.id),
          name: z.name,
          capacity: z.capacity ? Math.round((z.currentLoad / z.capacity) * 100) : 50,
        }));
        if (this.zones.length === 0) {
          this.zones = [
            { id: 'A', name: 'Зона A', capacity: 85 },
            { id: 'B', name: 'Зона B', capacity: 65 },
            { id: 'C', name: 'Зона C', capacity: 45 },
          ];
        }
        this.recentPlacements = products
          .filter(p => p.location)
          .slice(0, 12)
          .map(p => ({
            id: p.id,
            productName: p.name,
            barcode: p.barcode,
            location: p.location!,
            timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
            quantity: 1,
            status: 'Завершен' as const,
          }));
        if (this.recentPlacements.length === 0) {
          this.recentPlacements = [
            {
              id: 1,
              productName: products[0]?.name || 'iPhone 15 Pro',
              barcode: products[0]?.barcode || '4000000000001',
              location: 'A-01-03',
              timestamp: '2026-05-18 10:15:00',
              quantity: 5,
              status: 'Завершен',
            },
          ];
        }
      });
    } catch (e) {
      runInAction(() => {
        this.error = 'Не удалось загрузить данные склада';
        console.error(e);
      });
    } finally {
      runInAction(() => {
        this.loading = false;
      });
    }
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
    const zone = this.zones.find(z => z.id === this.selectedZone);
    const code = zone?.name.match(/Зона\s+(\w)/)?.[1] || this.selectedZone.charAt(0);
    return this.aisles.filter(a => a.zoneId === code || a.zoneId === this.selectedZone);
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
      parseInt(this.quantity, 10) > 0
    );
  }

  setBarcodeInput(value: string) {
    this.barcodeInput = value;
  }

  setSelectedZone(value: string) {
    this.selectedZone = value;
    this.selectedAisle = '';
    this.selectedShelf = '';
  }

  setSelectedAisle(value: string) {
    this.selectedAisle = value;
    this.selectedShelf = '';
  }

  setSelectedShelf(value: string) {
    this.selectedShelf = value;
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
    const product = this.products.find(
      p => p.barcode === this.barcodeInput || p.barcode.includes(this.barcodeInput)
    );
    if (product) {
      this.scannedProduct = product;
      this.showSuccess = true;
      setTimeout(() => (this.showSuccess = false), 2000);
    } else {
      this.showError = true;
      this.errorMessage = 'Продукт не найден. Попробуйте: 4000000000001 или PRD12345';
      setTimeout(() => (this.showError = false), 3000);
    }
  }

  confirmPlacement(_user: string) {
    if (!this.isFormValid || !this.scannedProduct) {
      this.showError = true;
      this.errorMessage = 'Пожалуйста, заполните все обязательные поля';
      setTimeout(() => (this.showError = false), 3000);
      return;
    }
    const zoneName = this.zones.find(z => z.id === this.selectedZone)?.name || this.selectedZone;
    const newPlacement: Placement = {
      id: Date.now(),
      productName: this.scannedProduct.name,
      barcode: this.scannedProduct.barcode,
      location: `${zoneName}, ${this.selectedAisle}, ${this.selectedShelf}`,
      timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
      quantity: parseInt(this.quantity, 10),
      status: 'Завершен',
    };
    this.recentPlacements = [newPlacement, ...this.recentPlacements].slice(0, 12);
    void placementApi.updateProductLocation(this.scannedProduct.id, newPlacement.location);
    this.closeModal();
    this.showSuccess = true;
    setTimeout(() => (this.showSuccess = false), 2000);
  }

  acceptPlacement(placement: Placement) {
    const product = this.products.find(p => p.barcode === placement.barcode);
    if (product) {
      this.scannedProduct = product;
      this.barcodeInput = product.barcode;
      this.showModal = true;
    }
  }
}

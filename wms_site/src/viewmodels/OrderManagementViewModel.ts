import { makeAutoObservable } from 'mobx';
import { productApi } from '../services/productApi';
import { Product } from '../models/ProductModel';

function parseMeta(description?: string): Record<string, string> {
  const out: Record<string, string> = {};
  if (!description) return out;
  description.split('|').forEach(part => {
    const [key, value] = part.split(':');
    if (key && value) out[key.trim()] = value.trim();
  });
  return out;
}

function mapApiProduct(p: {
  id: number;
  sku: string;
  barcode: string;
  name: string;
  description?: string;
  location?: string;
  stock?: number;
}): Product {
  const meta = parseMeta(p.description);
  return {
    id: p.id,
    barcode: p.barcode || p.sku,
    name: p.name,
    brand: meta.brand || '—',
    country: meta.country || '—',
    category: meta.category || 'Electronics',
    image: '',
    weight: meta.weight || '—',
    dimensions: meta.dimensions || '—',
    status: 'pending',
    location: p.location,
  };
}

export class OrderManagementViewModel {
  products: Product[] = [];
  searchQuery = '';
  showModal = false;
  packageType = '';
  containerBarcode = '';
  selectedProduct: Product | null = null;
  loading = false;
  error: string | null = null;

  constructor() {
    makeAutoObservable(this);
    void this.loadProducts();
  }

  async loadProducts() {
    try {
      this.loading = true;
      this.error = null;
      const response = await productApi.getProducts({ limit: 100 });
      this.products = response.data.map(p =>
        mapApiProduct({
          id: p.id,
          sku: p.sku,
          barcode: p.barcode,
          name: p.name,
          description: (p as { description?: string }).description,
          location: (p as { location?: string }).location,
          stock: (p as { stock?: number }).stock,
        })
      );
    } catch (error) {
      this.error = 'Ошибка при загрузке списка товаров';
      console.error('Error loading products:', error);
    } finally {
      this.loading = false;
    }
  }

  setSearchQuery(query: string) {
    this.searchQuery = query;
  }

  get filteredProducts() {
    if (!this.searchQuery.trim()) return this.products;
    const q = this.searchQuery.toLowerCase();
    return this.products.filter(
      p =>
        p.barcode.toLowerCase().includes(q) ||
        p.name.toLowerCase().includes(q) ||
        p.brand.toLowerCase().includes(q) ||
        p.country.toLowerCase().includes(q) ||
        p.category.toLowerCase().includes(q)
    );
  }

  handleAccept(product: Product) {
    this.selectedProduct = product;
    this.showModal = true;
  }

  handleReject(product: Product) {
    const index = this.products.findIndex(p => p.id === product.id);
    if (index !== -1) {
      this.products[index] = { ...product, status: 'rejected' };
    }
  }

  handleModalSubmit() {
    if (!this.selectedProduct) return;

    const index = this.products.findIndex(p => p.id === this.selectedProduct!.id);
    if (index !== -1) {
      this.products[index] = {
        ...this.products[index],
        status: 'processing',
        packageType: this.packageType,
        containerBarcode: this.containerBarcode,
      };
    }

    this.showModal = false;
    this.packageType = '';
    this.containerBarcode = '';
    this.selectedProduct = null;
  }

  get isFormValid() {
    return this.packageType !== '' && this.containerBarcode !== '';
  }

  setPackageType(type: string) {
    this.packageType = type;
  }

  setContainerBarcode(barcode: string) {
    this.containerBarcode = barcode;
  }

  setShowModal(show: boolean) {
    this.showModal = show;
  }
}

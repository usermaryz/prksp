import { makeAutoObservable } from 'mobx';
import { orderApi } from '../services/orderApi';
import { Product } from '../models/ProductModel';

export class OrderManagementViewModel {
  products: Product[] = [];
  searchQuery = '';
  showModal = false;
  packageType = '';
  containerBarcode = '';
  selectedProduct: Product | null = null;
  loading: boolean = false;
  error: string | null = null;

  constructor() {
    makeAutoObservable(this);
    this.loadProducts();
  }

  async loadProducts() {
    try {
      this.loading = true;
      this.error = null;
      this.products = await orderApi.getProducts();
    } catch (error) {
      this.error = 'Ошибка при загрузке списка продуктов';
      console.error('Error loading products:', error);
    } finally {
      this.loading = false;
    }
  }

  async updateProductStatus(productId: number, status: Product['status']) {
    try {
      this.loading = true;
      this.error = null;
      const updatedProduct = await orderApi.updateProductStatus(productId, status);
      const index = this.products.findIndex(p => p.id === productId);
      if (index !== -1) {
        this.products[index] = updatedProduct;
      }
    } catch (error) {
      this.error = 'Ошибка при обновлении статуса продукта';
      console.error('Error updating product status:', error);
    } finally {
      this.loading = false;
    }
  }

  async updateProduct(productId: number, data: Partial<Product>) {
    try {
      this.loading = true;
      this.error = null;
      const updatedProduct = await orderApi.updateProduct(productId, data);
      const index = this.products.findIndex(p => p.id === productId);
      if (index !== -1) {
        this.products[index] = updatedProduct;
      }
    } catch (error) {
      this.error = 'Ошибка при обновлении продукта';
      console.error('Error updating product:', error);
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
    const updatedProduct = { ...product, status: 'rejected' as const };
    const index = this.products.findIndex(p => p.id === product.id);
    if (index !== -1) {
      this.products[index] = updatedProduct;
    }
  }

  handleModalSubmit() {
    if (!this.selectedProduct) return;

    this.updateProduct(this.selectedProduct.id, {
      status: 'processing',
      packageType: this.packageType,
      containerBarcode: this.containerBarcode,
    });

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

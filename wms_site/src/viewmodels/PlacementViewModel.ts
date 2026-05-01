import { makeAutoObservable } from 'mobx';
import { placementApi, PlacementZone } from '../services/placementApi';
import { Product } from '../models/ProductModel';

export class PlacementViewModel {
  products: Product[] = [];
  zones: PlacementZone[] = [];
  loading = false;
  error: string | null = null;
  searchQuery = '';
  zoneSearchQuery = '';

  constructor() {
    makeAutoObservable(this);
  }

  async loadData() {
    this.loading = true;
    this.error = null;
    try {
      const [products, zones] = await Promise.all([
        placementApi.getProducts(),
        placementApi.getZones(),
      ]);
      this.products = products;
      this.zones = zones;
    } catch (error) {
      this.error = 'Ошибка при загрузке данных';
      console.error('Error loading data:', error);
    } finally {
      this.loading = false;
    }
  }

  async searchProducts(query: string) {
    this.searchQuery = query;
    if (!query.trim()) {
      await this.loadData();
      return;
    }
    try {
      this.products = await placementApi.searchProducts(query);
    } catch (error) {
      console.error('Error searching products:', error);
    }
  }

  async searchZones(query: string) {
    this.zoneSearchQuery = query;
    if (!query.trim()) {
      await this.loadData();
      return;
    }
    try {
      this.zones = await placementApi.searchZones(query);
    } catch (error) {
      console.error('Error searching zones:', error);
    }
  }

  async updateProductLocation(productId: number, location: string) {
    try {
      const updatedProduct = await placementApi.updateProductLocation(productId, location);
      const index = this.products.findIndex(p => p.id === productId);
      if (index !== -1) {
        this.products[index] = updatedProduct;
      }
    } catch (error) {
      console.error('Error updating product location:', error);
      throw error;
    }
  }

  get loadPercentage() {
    if (this.zones.length === 0) return 0;
    const totalCapacity = this.zones.reduce((sum, zone) => sum + zone.capacity, 0);
    const totalLoad = this.zones.reduce((sum, zone) => sum + zone.currentLoad, 0);
    return (totalLoad / totalCapacity) * 100;
  }

  get filteredProducts() {
    return this.products;
  }

  get filteredZones() {
    return this.zones;
  }

  get availableZones() {
    return this.zones.filter(zone => zone.status === 'available');
  }

  get fullZones() {
    return this.zones.filter(zone => zone.status === 'full');
  }

  get maintenanceZones() {
    return this.zones.filter(zone => zone.status === 'maintenance');
  }

  get totalCapacity() {
    return this.zones.reduce((sum, zone) => sum + zone.capacity, 0);
  }

  get totalLoad() {
    return this.zones.reduce((sum, zone) => sum + zone.currentLoad, 0);
  }
}

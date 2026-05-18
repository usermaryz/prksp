import { productApi } from './productApi';
import { inventoryApi } from './inventoryApi';

export interface Product {
  id: number;
  barcode: string;
  name: string;
  brand: string;
  country: string;
  category: string;
  image: string;
  status?: 'pending' | 'processing' | 'completed';
  location?: string;
  packageType?: string;
  containerBarcode?: string;
}

export interface PlacementZone {
  id: number;
  name: string;
  capacity: number;
  currentLoad: number;
  status: 'available' | 'full' | 'maintenance';
}

function mapProduct(p: {
  id: number;
  sku: string;
  barcode?: string;
  name: string;
  stock?: number;
  location?: string | null;
}): Product {
  return {
    id: p.id,
    barcode: p.barcode || p.sku,
    name: p.name,
    brand: '',
    country: '',
    category: '',
    image: '',
    status: 'pending',
    location: p.location || undefined,
  };
}

function mapZone(z: {
  id: number;
  name: string;
  capacity: number;
  current_usage?: number;
  used?: number;
  is_active?: boolean;
}): PlacementZone {
  const load = z.current_usage ?? z.used ?? 0;
  const cap = z.capacity || 1;
  let status: PlacementZone['status'] = 'available';
  if (z.is_active === false) status = 'maintenance';
  else if (load >= cap) status = 'full';
  return {
    id: z.id,
    name: z.name,
    capacity: cap,
    currentLoad: load,
    status,
  };
}

export const placementApi = {
  async getProducts(): Promise<Product[]> {
    const res = await productApi.getProducts({ limit: 200 });
    return res.data.map(p =>
      mapProduct({
        id: p.id,
        sku: p.sku,
        barcode: p.barcode,
        name: p.name,
        stock: p.stock,
        location: p.location,
      })
    );
  },

  async getZones(): Promise<PlacementZone[]> {
    const zones = await inventoryApi.getZones();
    return zones.map(mapZone);
  },

  async updateProductLocation(productId: number, location: string): Promise<Product> {
    const products = await this.getProducts();
    const found = products.find(p => p.id === productId);
    if (!found) throw new Error('Product not found');
    return { ...found, location, status: 'completed' };
  },

  async searchProducts(query: string): Promise<Product[]> {
    const res = await productApi.getProducts({ search: query, limit: 50 });
    return res.data.map(p =>
      mapProduct({
        id: p.id,
        sku: p.sku,
        barcode: p.barcode,
        name: p.name,
        location: p.location,
      })
    );
  },

  async searchZones(query: string): Promise<PlacementZone[]> {
    const zones = await this.getZones();
    const q = query.toLowerCase();
    return zones.filter(z => z.name.toLowerCase().includes(q));
  },
};

export default placementApi;

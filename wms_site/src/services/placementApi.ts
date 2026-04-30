import axios from 'axios';
import { API_BASE_URL, API_TIMEOUT } from '../config/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерфейс для продукта
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

// Интерфейс для зоны размещения
export interface PlacementZone {
  id: number;
  name: string;
  capacity: number;
  currentLoad: number;
  status: 'available' | 'full' | 'maintenance';
}

// Моковые данные для продуктов
const mockProducts: Product[] = [
  {
    id: 1,
    barcode: 'PRD12345',
    name: 'Беспроводные наушники',
    brand: 'SoundCore',
    country: 'Китай',
    category: 'Electronics',
    image:
      'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=400&q=80',
    status: 'pending',
  },
  {
    id: 2,
    barcode: 'PRD23456',
    name: 'Белковый порошок',
    brand: 'OptimumNutrition',
    country: 'США',
    category: 'Health & Fitness',
    image:
      'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=400&q=80',
    status: 'processing',
    location: 'A-12-3',
  },
  {
    id: 3,
    barcode: 'PRD34567',
    name: 'Механическая клавиатура',
    brand: 'Logitech',
    country: 'Тайвань',
    category: 'Computer Accessories',
    image:
      'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80',
    status: 'completed',
    location: 'B-5-2',
    packageType: 'Box',
    containerBarcode: 'CNT123456',
  },
];

// Моковые данные для зон размещения
const mockZones: PlacementZone[] = [
  {
    id: 1,
    name: 'Зона A',
    capacity: 1000,
    currentLoad: 750,
    status: 'available',
  },
  {
    id: 2,
    name: 'Зона B',
    capacity: 800,
    currentLoad: 800,
    status: 'full',
  },
  {
    id: 3,
    name: 'Зона C',
    capacity: 1200,
    currentLoad: 400,
    status: 'available',
  },
  {
    id: 4,
    name: 'Зона D',
    capacity: 600,
    currentLoad: 0,
    status: 'maintenance',
  },
];

// Сервис для работы с размещением товаров
export const placementApi = {
  // Получить список продуктов
  getProducts: async (): Promise<Product[]> => {
    try {
      const response = await api.get('/placement/products');
      return response.data;
    } catch (error) {
      console.error('Error fetching products:', error);
      return mockProducts;
    }
  },

  // Получить список зон размещения
  getZones: async (): Promise<PlacementZone[]> => {
    try {
      const response = await api.get('/placement/zones');
      return response.data;
    } catch (error) {
      console.error('Error fetching zones:', error);
      return mockZones;
    }
  },

  // Обновить местоположение продукта
  updateProductLocation: async (productId: number, location: string): Promise<Product> => {
    try {
      const response = await api.patch(`/placement/products/${productId}`, { location });
      return response.data;
    } catch (error) {
      console.error('Error updating product location:', error);
      const product = mockProducts.find(p => p.id === productId);
      if (product) {
        product.location = location;
        return product;
      }
      throw error;
    }
  },

  // Поиск продуктов
  searchProducts: async (query: string): Promise<Product[]> => {
    try {
      const response = await api.get(`/placement/products/search?q=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error) {
      console.error('Error searching products:', error);
      const q = query.toLowerCase();
      return mockProducts.filter(
        p =>
          p.barcode.toLowerCase().includes(q) ||
          p.name.toLowerCase().includes(q) ||
          p.brand.toLowerCase().includes(q) ||
          p.country.toLowerCase().includes(q) ||
          p.category.toLowerCase().includes(q)
      );
    }
  },

  // Поиск зон размещения
  searchZones: async (query: string): Promise<PlacementZone[]> => {
    try {
      const response = await api.get(`/placement/zones/search?q=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error) {
      console.error('Error searching zones:', error);
      const q = query.toLowerCase();
      return mockZones.filter(z => z.name.toLowerCase().includes(q));
    }
  },
};

export default api;

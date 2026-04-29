/**
 * Products API Service
 * Сервис работы с товарами
 */

import api, { handleApiError, PaginatedResponse } from './api';

// Типы
export interface Product {
  id: number;
  sku: string;
  barcode: string;
  name: string;
  description?: string;
  price: number;
  cost_price?: number;
  weight?: number;
  length?: number;
  width?: number;
  height?: number;
  category_id?: number;
  category?: Category;
  brand_id?: number;
  brand?: Brand;
  status: 'active' | 'inactive' | 'discontinued';
  min_stock_level: number;
  max_stock_level: number;
  reorder_point: number;
  image_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: number;
  name: string;
  description?: string;
  parent_id?: number;
  sort_order: number;
  is_active: boolean;
}

export interface Brand {
  id: number;
  name: string;
  description?: string;
  logo_url?: string;
  is_active: boolean;
}

export interface ProductCreate {
  sku: string;
  barcode: string;
  name: string;
  description?: string;
  price: number;
  cost_price?: number;
  category_id?: number;
  brand_id?: number;
  min_stock_level?: number;
  max_stock_level?: number;
  reorder_point?: number;
  weight?: number;
  length?: number;
  width?: number;
  height?: number;
}

export interface ProductUpdate {
  name?: string;
  description?: string;
  price?: number;
  cost_price?: number;
  category_id?: number;
  brand_id?: number;
  status?: 'active' | 'inactive' | 'discontinued';
  min_stock_level?: number;
  max_stock_level?: number;
  reorder_point?: number;
}

export interface ProductFilters {
  page?: number;
  limit?: number;
  search?: string;
  category?: number;
  brand?: number;
  status?: string;
}

// API методы
export const productApi = {
  /**
   * Получить список товаров
   */
  async getProducts(filters: ProductFilters = {}): Promise<PaginatedResponse<Product>> {
    try {
      const params = new URLSearchParams();
      if (filters.page) params.append('page', filters.page.toString());
      if (filters.limit) params.append('limit', filters.limit.toString());
      if (filters.search) params.append('search', filters.search);
      if (filters.category) params.append('category', filters.category.toString());
      if (filters.brand) params.append('brand', filters.brand.toString());
      if (filters.status) params.append('status', filters.status);

      const response = await api.get<PaginatedResponse<Product>>(`/products?${params}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить товар по ID
   */
  async getProduct(id: number): Promise<Product> {
    try {
      const response = await api.get<Product>(`/products/${id}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить товар по штрихкоду
   */
  async getProductByBarcode(barcode: string): Promise<Product> {
    try {
      const response = await api.get<Product>(`/products/barcode/${barcode}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Поиск товаров
   */
  async searchProducts(query: string): Promise<Product[]> {
    try {
      const response = await api.get<Product[]>(`/products/search?q=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Создать товар
   */
  async createProduct(data: ProductCreate): Promise<Product> {
    try {
      const response = await api.post<Product>('/products', data);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Обновить товар
   */
  async updateProduct(id: number, data: ProductUpdate): Promise<Product> {
    try {
      const response = await api.patch<Product>(`/products/${id}`, data);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Обновить статус товара
   */
  async updateProductStatus(id: number, status: string): Promise<Product> {
    try {
      const response = await api.patch<Product>(`/products/${id}/status?status=${status}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Удалить товар
   */
  async deleteProduct(id: number): Promise<void> {
    try {
      await api.delete(`/products/${id}`);
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить категории
   */
  async getCategories(): Promise<Category[]> {
    try {
      const response = await api.get<Category[]>('/products/categories/');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Создать категорию
   */
  async createCategory(data: { name: string; description?: string; parent_id?: number }): Promise<Category> {
    try {
      const response = await api.post<Category>('/products/categories/', data);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Получить бренды
   */
  async getBrands(): Promise<Brand[]> {
    try {
      const response = await api.get<Brand[]>('/products/brands/');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Создать бренд
   */
  async createBrand(data: { name: string; description?: string }): Promise<Brand> {
    try {
      const response = await api.post<Brand>('/products/brands/', data);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

export default productApi;


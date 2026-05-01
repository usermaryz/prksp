export interface Product {
  id: number;
  barcode: string;
  name: string;
  brand: string;
  country: string;
  category: string;
  image: string;
  weight: string;
  dimensions: string;
  status?: 'pending' | 'processing' | 'completed' | 'rejected';
  location?: string;
  packageType?: string;
  containerBarcode?: string;
}

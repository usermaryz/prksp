export interface Placement {
  id: number;
  productName: string;
  barcode: string;
  location: string;
  timestamp: string;
  quantity: number;
  placedBy?: string;
  status: 'Завершен' | 'В обработке' | 'Ожидает размещения';
}

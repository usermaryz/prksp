export interface OrderCollection {
  id: string;
  customerName: string;
  customerEmail: string;
  items: { name: string; quantity: number }[];
  location: string;
  status: 'Pending Collection' | 'In Progress' | 'Completed';
}

export interface UserActivity {
  id: number;
  action: string;
  timestamp: string;
  status: 'success' | 'warning' | 'info';
  icon: string;
}

export interface UserAccountModel {
  id: string;
  fullName: string;
  role: string;
  avatar?: string;
  verified: boolean;
  premium: boolean;
  email: string;
  phone: string;
  location: string;
  timezone: string;
  stats: {
    totalOrders: number;
    pendingShipments: number;
    completedTasks: number;
    efficiency: number;
  };
  activities: UserActivity[];
}

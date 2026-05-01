export interface DashboardStat {
  icon: string;
  label: string;
  value: string;
  change: string;
  changeType: 'up' | 'down' | 'neutral';
  color: string;
}

export interface DashboardModel {
  stats: DashboardStat[];
}

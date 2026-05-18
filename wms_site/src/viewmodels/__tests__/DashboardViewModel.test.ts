import { DashboardViewModel } from '../DashboardViewModel';
import { dashboardApi } from '../../services/dashboardApi';

jest.mock('../../services/dashboardApi');

const mockMetrics = {
  orders: { total: 10, pending: 2, picking: 1, shipped: 3 },
  products: { total: 50, active: 45, low_stock: 5 },
  picking: { pending_tasks: 2, in_progress: 1 },
};

describe('DashboardViewModel', () => {
  beforeEach(() => {
    (dashboardApi.getMetrics as jest.Mock).mockResolvedValue(mockMetrics);
  });

  it('loads stats from API', async () => {
    const viewModel = new DashboardViewModel();
    await new Promise(r => setTimeout(r, 50));

    expect(viewModel.stats).toHaveLength(4);
    expect(viewModel.stats[0].label).toBe('Заказы всего');
    expect(viewModel.stats[0].value).toBe('10');
  });
});

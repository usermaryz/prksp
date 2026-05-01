import { DashboardViewModel } from '../DashboardViewModel';

describe('DashboardViewModel', () => {
  let viewModel: DashboardViewModel;

  beforeEach(() => {
    viewModel = new DashboardViewModel();
  });

  it('initializes with correct stats data', () => {
    const stats = viewModel.stats;

    expect(stats).toHaveLength(4);
    expect(stats[0].label).toBe('Общее количество заказов');
    expect(stats[1].label).toBe('Скорость обработки');
    expect(stats[2].label).toBe('Уровень инвентаризации');
    expect(stats[3].label).toBe('Коэффициент возврата');
  });

  it('has correct initial values', () => {
    const stats = viewModel.stats;

    expect(stats[0].value).toBe('1,284');
    expect(stats[1].value).toBe('98.3%');
    expect(stats[2].value).toBe('85.7%');
    expect(stats[3].value).toBe('3.8%');
  });

  it('has correct change indicators', () => {
    const stats = viewModel.stats;

    expect(stats[0].changeType).toBe('up');
    expect(stats[1].changeType).toBe('up');
    expect(stats[2].changeType).toBe('down');
    expect(stats[3].changeType).toBe('down');
  });

  it('has correct color classes', () => {
    const stats = viewModel.stats;

    expect(stats[0].color).toBe('bg-indigo-100 text-indigo-600');
    expect(stats[1].color).toBe('bg-blue-100 text-blue-600');
    expect(stats[2].color).toBe('bg-green-100 text-green-600');
    expect(stats[3].color).toBe('bg-red-100 text-red-600');
  });
});

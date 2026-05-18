import React from 'react';
import { render, screen } from '@testing-library/react';
import { DashboardStats } from '../DashboardStats';
import { DashboardStat } from '../../models/DashboardModel';

describe('DashboardStats', () => {
  const mockStats: DashboardStat[] = [
    {
      icon: 'fa-solid fa-box',
      label: 'Общее количество заказов',
      value: '1,284',
      change: '12.5%',
      changeType: 'up',
      color: 'bg-slate-100 text-slate-700',
    },
    {
      icon: 'fa-solid fa-chart-line',
      label: 'Скорость обработки',
      value: '98.3%',
      change: '3.2%',
      changeType: 'up',
      color: 'bg-blue-100 text-blue-600',
    },
  ];

  it('renders all stats correctly', () => {
    render(<DashboardStats stats={mockStats} />);

    // Проверяем, что все метки отображаются
    expect(screen.getByText('Общее количество заказов')).toBeInTheDocument();
    expect(screen.getByText('Скорость обработки')).toBeInTheDocument();

    // Проверяем, что все значения отображаются
    expect(screen.getByText('1,284')).toBeInTheDocument();
    expect(screen.getByText('98.3%')).toBeInTheDocument();
  });

  it('applies correct color classes', () => {
    render(<DashboardStats stats={mockStats} />);

    const statCards = document.querySelectorAll('.dashboard-stats__card');
    expect(statCards[0].querySelector('.bg-slate-100')).toBeInTheDocument();
    expect(statCards[1].querySelector('.bg-blue-100')).toBeInTheDocument();
  });

  it('displays correct change indicators', () => {
    render(<DashboardStats stats={mockStats} />);

    // Проверяем наличие иконок изменения
    const upArrows = document.querySelectorAll('.fa-arrow-up');
    expect(upArrows.length).toBe(2);

    // Проверяем отображение процентов изменения
    expect(screen.getByText('12.5%')).toBeInTheDocument();
    expect(screen.getByText('3.2%')).toBeInTheDocument();
  });
});

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { DashboardPage } from '../DashboardPage';

jest.mock('../../services/dashboardApi', () => ({
  dashboardApi: {
    getMetrics: jest.fn().mockResolvedValue({
      orders: { total: 3, pending: 1, picking: 1, shipped: 1 },
      products: { total: 10, active: 9, low_stock: 2 },
      picking: { pending_tasks: 2, in_progress: 1 },
    }),
  },
}));

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('DashboardPage', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it('renders dashboard title and description', () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    expect(screen.getByRole('heading', { name: 'Главная' })).toBeInTheDocument();
    expect(screen.getByText('Обзор операций склада')).toBeInTheDocument();
  });

  it('renders main sections', () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    expect(screen.getByText('Быстрые действия')).toBeInTheDocument();
    expect(screen.getByText('Инструкция')).toBeInTheDocument();
    expect(screen.getByText('Безопасность склада')).toBeInTheDocument();
  });

  it('navigates to error return form when button is clicked', () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    fireEvent.click(screen.getByText('Форма ошибки/возврата'));
    expect(mockNavigate).toHaveBeenCalledWith('/error-return-form');
  });
});

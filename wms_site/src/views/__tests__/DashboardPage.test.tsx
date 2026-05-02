import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { DashboardPage } from '../DashboardPage';

// Мокаем useNavigate
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

    // Используем getByRole для поиска заголовка
    expect(screen.getByRole('heading', { name: 'Дашборд' })).toBeInTheDocument();
    expect(screen.getByText('Мониторинг работы склада и ключевых метрик')).toBeInTheDocument();
  });

  it('renders all dashboard components', () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    // Проверяем наличие всех основных компонентов
    expect(screen.getByText('Инструкция')).toBeInTheDocument();
    expect(screen.getByText('Безопасность склада')).toBeInTheDocument();
    expect(screen.getByText('Основные правила безопасности')).toBeInTheDocument();
  });

  it('navigates to error return form when button is clicked', () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    const button = screen.getByText('Открыть форму ошибки/возврата');
    fireEvent.click(button);

    expect(mockNavigate).toHaveBeenCalledWith('/error-return-form');
  });

  it('displays all statistics cards', () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    // Проверяем наличие всех карточек статистики
    expect(screen.getByText('Общее количество заказов')).toBeInTheDocument();
    expect(screen.getByText('Скорость обработки')).toBeInTheDocument();
    expect(screen.getByText('Уровень инвентаризации')).toBeInTheDocument();
    expect(screen.getByText('Коэффициент возврата')).toBeInTheDocument();
  });

  it('has working download link for return policy', () => {
    render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );

    const downloadLink = screen.getByText('Скачать политику возврата');
    expect(downloadLink.closest('a')).toHaveAttribute('href', '/files/return-policy.rtf');
    expect(downloadLink.closest('a')).toHaveAttribute('download', 'Политика возврата.rtf');
  });
});

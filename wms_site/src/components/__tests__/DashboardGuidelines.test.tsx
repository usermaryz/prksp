import React from 'react';
import { render, screen } from '@testing-library/react';
import { DashboardGuidelines } from '../DashboardGuidelines';

describe('DashboardGuidelines', () => {
  it('renders title and subtitle correctly', () => {
    render(<DashboardGuidelines />);

    expect(screen.getByText('Инструкция')).toBeInTheDocument();
    expect(screen.getByText('Как обрабатывать ошибки и возвраты')).toBeInTheDocument();
  });

  it('renders all steps correctly', () => {
    render(<DashboardGuidelines />);

    // Проверяем наличие всех шагов
    expect(screen.getByText('Шаг 1: Сканируйте продукт')).toBeInTheDocument();
    expect(screen.getByText('Шаг 2: Опишите проблему')).toBeInTheDocument();
    expect(screen.getByText('Шаг 3: Приложите доказательства')).toBeInTheDocument();
    expect(screen.getByText('Шаг 4: Отправьте заявку')).toBeInTheDocument();
  });

  it('renders step descriptions correctly', () => {
    render(<DashboardGuidelines />);

    expect(
      screen.getByText(
        'Используйте сканер штрих-кода для идентификации продукта. Можно ввести штрих-код вручную.'
      )
    ).toBeInTheDocument();
    expect(
      screen.getByText('Выберите тип ошибки и опишите детали. Будьте максимально конкретны.')
    ).toBeInTheDocument();
    expect(
      screen.getByText('Загрузите фото повреждённого или неверного товара для подтверждения.')
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        'Отправьте форму на проверку. Отдел контроля качества рассмотрит заявку и примет меры.'
      )
    ).toBeInTheDocument();
  });

  it('renders important note correctly', () => {
    render(<DashboardGuidelines />);

    const importantNote = screen.getByText(
      /Все возвраты должны быть обработаны в течение 24 часов/
    );
    expect(importantNote).toBeInTheDocument();
  });

  it('has working download link', () => {
    render(<DashboardGuidelines />);

    const downloadLink = screen.getByText('Скачать политику возврата');
    expect(downloadLink.closest('a')).toHaveAttribute('href', '/files/return-policy.rtf');
    expect(downloadLink.closest('a')).toHaveAttribute('download', 'Политика возврата.rtf');
  });

  it('renders with correct styling classes', () => {
    render(<DashboardGuidelines />);

    const container = document.querySelector('.dashboard-guidelines');
    expect(container).toHaveClass('bg-white', 'rounded-xl', 'shadow', 'p-6', 'max-w-md');

    const downloadButton = screen.getByText('Скачать политику возврата').closest('a');
    expect(downloadButton).toHaveClass('bg-indigo-50', 'hover:bg-indigo-100', 'text-indigo-700');
  });
});

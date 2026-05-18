import React from 'react';
import { observer } from 'mobx-react-lite';
import { Link, useNavigate } from 'react-router-dom';
import { DashboardViewModel } from '../viewmodels/DashboardViewModel';
import AppLayout from '../components/layout/AppLayout';
import PageHeader from '../components/layout/PageHeader';
import { btnPrimary, pageCard, statCard } from '../components/layout/pageStyles';

const viewModel = new DashboardViewModel();

const quickActions = [
  { to: '/order-management', title: 'Новый заказ', desc: 'Создать или принять заказ' },
  { to: '/product-placement', title: 'Размещение', desc: 'Положить товар на склад' },
  { to: '/order-picking', title: 'Очередь сборки', desc: 'Задачи комплектации' },
  { to: '/error-return-form', title: 'Возврат / ошибка', desc: 'Оформить заявку' },
];

export const DashboardPage: React.FC = observer(() => {
  const navigate = useNavigate();

  return (
    <AppLayout>
      <PageHeader
        title="Главная"
        subtitle="Обзор операций склада"
        action={
          <button type="button" onClick={() => navigate('/error-return-form')} className={btnPrimary}>
            Форма ошибки/возврата
          </button>
        }
      />

      {viewModel.loading && <p className="text-slate-500 text-center py-8">Загрузка метрик...</p>}
      {viewModel.error && <p className="text-red-600 text-center py-4">{viewModel.error}</p>}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {viewModel.stats.map(stat => (
          <div key={stat.label} className={statCard}>
            <div className="text-sm font-medium text-slate-500">{stat.label}</div>
            <div className="text-3xl font-semibold text-slate-900 mt-1">{stat.value}</div>
            {stat.change && <div className="text-sm text-slate-400 mt-1">{stat.change}</div>}
          </div>
        ))}
      </div>

      <div className={`${pageCard} p-6`}>
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Быстрые действия</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map(action => (
            <Link
              key={action.to}
              to={action.to}
              className="p-4 border border-slate-200 rounded-lg hover:border-slate-300 hover:bg-slate-50 transition-colors"
            >
              <div className="text-slate-900 font-medium">{action.title}</div>
              <div className="text-sm text-slate-500 mt-1">{action.desc}</div>
            </Link>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div className={`${pageCard} p-6`}>
          <h2 className="text-lg font-semibold text-slate-900 mb-2">Инструкция</h2>
          <p className="text-slate-500 text-sm mb-4">Как обрабатывать ошибки и возвраты</p>
          <ol className="space-y-4 text-sm text-slate-600">
            <li><strong className="text-slate-900">1.</strong> Сканируйте продукт</li>
            <li><strong className="text-slate-900">2.</strong> Опишите проблему</li>
            <li><strong className="text-slate-900">3.</strong> Приложите фото</li>
          </ol>
        </div>
        <div className={`${pageCard} p-6`}>
          <h2 className="text-lg font-semibold text-slate-900 mb-2">Безопасность склада</h2>
          <p className="text-slate-500 text-sm mb-4">Основные правила</p>
          <ul className="space-y-3 text-sm text-slate-600">
            <li>Используйте средства защиты на складе</li>
            <li>Складывайте товары устойчиво</li>
            <li>Знайте расположение огнетушителей</li>
          </ul>
        </div>
      </div>
    </AppLayout>
  );
});

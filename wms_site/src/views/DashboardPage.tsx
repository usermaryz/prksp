import React from 'react';
import { observer } from 'mobx-react-lite';
import { DashboardViewModel } from '../viewmodels/DashboardViewModel';
import Navigation from '../components/Navigation';
import { useNavigate } from 'react-router-dom';

const viewModel = new DashboardViewModel();

export const DashboardPage: React.FC = observer(() => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Navigation active="Дашборд" />
      <div className="p-6 max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Дашборд</h1>
            <p className="text-gray-600 text-lg">Мониторинг работы склада и ключевых метрик</p>
          </div>
          <button
            onClick={() => navigate('/error-return-form')}
            className="inline-flex items-center px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200 text-sm font-medium shadow-sm hover:shadow-md"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Открыть форму ошибки/возврата
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {viewModel.stats.map(stat => (
            <div
              key={stat.label}
              className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 p-6 border border-gray-100"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="text-gray-600 text-sm font-medium">{stat.label}</div>
                <div className="w-10 h-10 rounded-full bg-indigo-50 flex items-center justify-center">
                  <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
              </div>
              <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 p-6 border border-gray-100">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Инструкция</h2>
            <p className="text-gray-600 mb-6">Как обрабатывать ошибки и возвраты</p>
            <ol className="space-y-6">
              <li className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center">
                  <span className="text-indigo-600 font-semibold">1</span>
                </div>
                <div>
                  <strong className="block text-gray-900 mb-1">Сканируйте продукт</strong>
                  <p className="text-gray-600 text-sm">Используйте сканер штрих-кода для идентификации продукта.</p>
                </div>
              </li>
              <li className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center">
                  <span className="text-indigo-600 font-semibold">2</span>
                </div>
                <div>
                  <strong className="block text-gray-900 mb-1">Опишите проблему</strong>
                  <p className="text-gray-600 text-sm">Выберите тип ошибки и опишите детали.</p>
                </div>
              </li>
              <li className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center">
                  <span className="text-indigo-600 font-semibold">3</span>
                </div>
                <div>
                  <strong className="block text-gray-900 mb-1">Приложите доказательства</strong>
                  <p className="text-gray-600 text-sm">Загрузите фото повреждённого товара.</p>
                </div>
              </li>
            </ol>
            <a
              href="/files/return-policy.rtf"
              download="Политика возврата.rtf"
              className="inline-flex items-center px-4 py-2 mt-6 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200 text-sm font-medium"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Скачать политику возврата
            </a>
          </div>

          <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 p-6 border border-gray-100">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Безопасность склада</h2>
            <p className="text-gray-600 mb-6">Основные правила безопасности</p>
            <ul className="space-y-6">
              <li className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                  <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <div>
                  <strong className="block text-gray-900 mb-1">Используйте средства защиты</strong>
                  <p className="text-gray-600 text-sm">Надевайте каски и перчатки на складе.</p>
                </div>
              </li>
              <li className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                  <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
                <div>
                  <strong className="block text-gray-900 mb-1">Правильная укладка</strong>
                  <p className="text-gray-600 text-sm">Складывайте товары устойчиво.</p>
                </div>
              </li>
              <li className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                  <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" />
                  </svg>
                </div>
                <div>
                  <strong className="block text-gray-900 mb-1">Пожарная безопасность</strong>
                  <p className="text-gray-600 text-sm">Знайте расположение огнетушителей.</p>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
});

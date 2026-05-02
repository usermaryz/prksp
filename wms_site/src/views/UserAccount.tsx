import React from 'react';
import { observer } from 'mobx-react-lite';
import { UserAccountViewModel } from '../viewmodels/UserAccountViewModel';
import Navigation from '../components/Navigation';

const viewModel = new UserAccountViewModel();

export const UserAccount: React.FC = observer(() => {
  const user = viewModel.user;
  if (!user) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Navigation active="Аккаунт" />
      <div className="p-6 max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xl font-bold">
              {user.fullName
                .split(' ')
                .map(n => n[0])
                .join('')}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{user.fullName}</h1>
              <p className="text-gray-600 text-lg">{user.role}</p>
            </div>
          </div>
          <button
            onClick={() => viewModel.logout()}
            className="inline-flex items-center px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200 text-sm font-medium shadow-sm hover:shadow-md"
          >
            <i className="fas fa-sign-out-alt mr-2"></i>
            Выйти
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 p-6 border border-gray-100">
            <div className="text-gray-600 text-sm font-medium mb-2">Всего заказов</div>
            <div className="text-2xl font-bold text-gray-900">{user.stats.totalOrders}</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 p-6 border border-gray-100">
            <div className="text-gray-600 text-sm font-medium mb-2">Ожидает отправки</div>
            <div className="text-2xl font-bold text-gray-900">{user.stats.pendingShipments}</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 p-6 border border-gray-100">
            <div className="text-gray-600 text-sm font-medium mb-2">Выполнено задач</div>
            <div className="text-2xl font-bold text-gray-900">{user.stats.completedTasks}</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 p-6 border border-gray-100">
            <div className="text-gray-600 text-sm font-medium mb-2">Эффективность</div>
            <div className="text-2xl font-bold text-gray-900">{user.stats.efficiency}%</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 p-6 border border-gray-100">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Последние действия</h2>
            <div className="space-y-4">
              {viewModel.recentActivities.map(activity => (
                <div key={activity.id} className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center">
                    <i className={`fas ${activity.icon} text-indigo-600`}></i>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                    <p className="text-xs text-gray-500">{activity.timestamp}</p>
                  </div>
                </div>
              ))}
            </div>
            <button
              onClick={() => viewModel.toggleAllActivities()}
              className="mt-4 text-sm text-indigo-600 hover:text-indigo-700 font-medium"
            >
              Смотреть все действия
              <i className="fas fa-arrow-right ml-1"></i>
            </button>
          </div>

          <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 p-6 border border-gray-100">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Данные аккаунта</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-600 mb-1">Почта</label>
                <div className="flex items-center">
                  {viewModel.isEditing.email ? (
                    <div className="flex-1 flex items-center space-x-2">
                      <input
                        type="email"
                        value={viewModel.tempValues.email}
                        onChange={e => viewModel.updateTempValue('email', e.target.value)}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                      <button
                        onClick={() => viewModel.saveField('email')}
                        className="text-green-600 hover:text-green-700"
                      >
                        <i className="fas fa-check"></i>
                      </button>
                      <button
                        onClick={() => viewModel.cancelEditing('email')}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        <i className="fas fa-times"></i>
                      </button>
                    </div>
                  ) : (
                    <>
                      <input
                        type="email"
                        value={user.email}
                        readOnly
                        className="flex-1 px-3 py-2 bg-gray-50 rounded-lg text-sm"
                      />
                      <button
                        onClick={() => viewModel.toggleEditing('email')}
                        className="ml-2 text-indigo-600 hover:text-indigo-700"
                      >
                        <i className="fas fa-pen"></i>
                      </button>
                    </>
                  )}
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Телефон</label>
                <div className="flex items-center">
                  {viewModel.isEditing.phone ? (
                    <div className="flex-1 flex items-center space-x-2">
                      <input
                        type="tel"
                        value={viewModel.tempValues.phone}
                        onChange={e => viewModel.updateTempValue('phone', e.target.value)}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                      <button
                        onClick={() => viewModel.saveField('phone')}
                        className="text-green-600 hover:text-green-700"
                      >
                        <i className="fas fa-check"></i>
                      </button>
                      <button
                        onClick={() => viewModel.cancelEditing('phone')}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        <i className="fas fa-times"></i>
                      </button>
                    </div>
                  ) : (
                    <>
                      <input
                        type="tel"
                        value={user.phone}
                        readOnly
                        className="flex-1 px-3 py-2 bg-gray-50 rounded-lg text-sm"
                      />
                      <button
                        onClick={() => viewModel.toggleEditing('phone')}
                        className="ml-2 text-indigo-600 hover:text-indigo-700"
                      >
                        <i className="fas fa-pen"></i>
                      </button>
                    </>
                  )}
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Локация</label>
                <div className="flex items-center">
                  {viewModel.isEditing.location ? (
                    <div className="flex-1 flex items-center space-x-2">
                      <input
                        type="text"
                        value={viewModel.tempValues.location}
                        onChange={e => viewModel.updateTempValue('location', e.target.value)}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                      <button
                        onClick={() => viewModel.saveField('location')}
                        className="text-green-600 hover:text-green-700"
                      >
                        <i className="fas fa-check"></i>
                      </button>
                      <button
                        onClick={() => viewModel.cancelEditing('location')}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        <i className="fas fa-times"></i>
                      </button>
                    </div>
                  ) : (
                    <>
                      <input
                        type="text"
                        value={user.location}
                        readOnly
                        className="flex-1 px-3 py-2 bg-gray-50 rounded-lg text-sm"
                      />
                      <button
                        onClick={() => viewModel.toggleEditing('location')}
                        className="ml-2 text-indigo-600 hover:text-indigo-700"
                      >
                        <i className="fas fa-pen"></i>
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Модальное окно со всеми действиями */}
      {viewModel.showAllActivities && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" aria-hidden="true">
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>
            <div className="inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6">
                <div className="sm:flex sm:items-start">
                  <div className="mt-3 text-center sm:mt-0 sm:text-left w-full">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">
                      История действий
                    </h3>
                    <div className="mt-2 max-h-96 overflow-y-auto">
                      <div className="space-y-4">
                        {viewModel.allActivities.map(activity => (
                          <div
                            key={activity.id}
                            className="flex items-start space-x-3 p-2 hover:bg-gray-50 rounded-lg transition-colors"
                          >
                            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center">
                              <i className={`fas ${activity.icon} text-indigo-600`}></i>
                            </div>
                            <div>
                              <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                              <p className="text-xs text-gray-500">{activity.timestamp}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  onClick={() => viewModel.toggleAllActivities()}
                  className="w-full inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm"
                >
                  Закрыть
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

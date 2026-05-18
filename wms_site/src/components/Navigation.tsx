import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { authApi } from '../services/authApi';
import { AppIcons } from './layout/AppIcons';

const navItems = [
  { path: '/dashboard', label: 'Главная', icon: AppIcons.dashboard },
  { path: '/order-management', label: 'Заказы', icon: AppIcons.orders },
  { path: '/order-picking', label: 'Сборка', icon: AppIcons.picking },
  { path: '/product-placement', label: 'Склад', icon: AppIcons.placement },
  { path: '/order-collection', label: 'Приёмка', icon: AppIcons.collection },
  { path: '/error-return-form', label: 'Возвраты', icon: AppIcons.returnForm },
];

const Navigation: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const user = JSON.parse(localStorage.getItem('user') || '{}') as {
    fullName?: string;
    role?: string;
  };

  const handleLogout = async () => {
    await authApi.logout();
    navigate('/login');
  };

  const initial = user.fullName?.charAt(0)?.toUpperCase() || 'U';

  return (
    <nav className="bg-white border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex justify-between h-14 items-center">
          <div className="flex items-center space-x-6 overflow-x-auto">
            <Link to="/dashboard" className="flex items-center space-x-2 shrink-0">
              <div className="w-8 h-8 bg-slate-900 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">W</span>
              </div>
              <span className="font-semibold text-slate-900 hidden sm:inline">WMS</span>
            </Link>
            <div className="flex items-center space-x-1">
              {navItems.map(item => {
                const active = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                      active
                        ? 'bg-slate-100 text-slate-900'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                    }`}
                  >
                    {item.icon}
                    <span className="hidden md:inline">{item.label}</span>
                  </Link>
                );
              })}
            </div>
          </div>
          <div className="relative shrink-0">
            <button
              type="button"
              onClick={() => setMenuOpen(!menuOpen)}
              className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-slate-50 transition-colors"
            >
              <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-slate-600">{initial}</span>
              </div>
              <span className="text-sm font-medium text-slate-700 hidden sm:inline max-w-[120px] truncate">
                {user.fullName || 'Пользователь'}
              </span>
              {AppIcons.chevronDown}
            </button>
            {menuOpen && (
              <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-slate-200 py-1 z-50">
                <Link
                  to="/account"
                  onClick={() => setMenuOpen(false)}
                  className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
                >
                  {AppIcons.user}
                  <span>Аккаунт</span>
                </Link>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                >
                  {AppIcons.logout}
                  <span>Выйти</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;

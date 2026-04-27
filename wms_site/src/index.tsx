import React, { useState, useEffect, createContext, useContext, useCallback } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import './index.css';

// =============================================================================
// API CONFIG
// =============================================================================
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// =============================================================================
// TYPES
// =============================================================================
interface Product {
  id: number;
  sku: string;
  name: string;
  description?: string;
  price: number;
  stock: number;
  location?: string;
  category_id?: number;
  created_at: string;
}

interface Order {
  id: number;
  order_number: string;
  customer_name?: string;
  customer_phone?: string;
  customer_address?: string;
  status: string;
  priority: string;
  total: number;
  items_count: number;
  created_at: string;
}

interface PickingTask {
  id: number;
  order_id?: number;
  order_number?: string;
  status: string;
  priority: string;
  assigned_to?: string;
  progress: number;
  items_count: number;
  created_at: string;
}

interface Zone {
  id: number;
  code: string;
  name: string;
  capacity: number;
  used: number;
}

interface Shipment {
  id: number;
  order_number?: string;
  tracking_number: string;
  carrier_name?: string;
  status: string;
  recipient_name?: string;
  delivery_address?: string;
  estimated_delivery?: string;
  created_at: string;
}

interface Notification {
  id: number;
  type: 'success' | 'error' | 'info';
  message: string;
}

// =============================================================================
// ICONS (SVG)
// =============================================================================
const Icons = {
  dashboard: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>,
  products: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" /></svg>,
  orders: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>,
  picking: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg>,
  placement: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>,
  logistics: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" /></svg>,
  search: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>,
  plus: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" /></svg>,
  trash: <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>,
  check: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>,
  clock: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
  truck: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0" /></svg>,
  logout: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>,
  user: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>,
  x: <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" /></svg>,
  chevronDown: <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>,
  play: <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
  eye: <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>,
};

// =============================================================================
// NOTIFICATION CONTEXT
// =============================================================================
const NotificationContext = createContext<{
  notifications: Notification[];
  addNotification: (type: 'success' | 'error' | 'info', message: string) => void;
}>({ notifications: [], addNotification: () => {} });

const NotificationProvider = ({ children }: { children: React.ReactNode }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = useCallback((type: 'success' | 'error' | 'info', message: string) => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, type, message }]);
    setTimeout(() => setNotifications(prev => prev.filter(n => n.id !== id)), 3000);
  }, []);

  return (
    <NotificationContext.Provider value={{ notifications, addNotification }}>
      {children}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {notifications.map(n => (
          <div key={n.id} className={`px-4 py-3 rounded-lg shadow-lg text-white text-sm font-medium animate-slide-in ${
            n.type === 'success' ? 'bg-emerald-600' : n.type === 'error' ? 'bg-red-600' : 'bg-slate-700'
          }`}>
            {n.message}
          </div>
        ))}
      </div>
    </NotificationContext.Provider>
  );
};

const useNotification = () => useContext(NotificationContext);

// =============================================================================
// MODAL
// =============================================================================
const Modal = ({ isOpen, onClose, title, children }: { isOpen: boolean; onClose: () => void; title: string; children: React.ReactNode }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center px-6 py-4 border-b border-slate-100">
          <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
          <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-lg transition-colors">{Icons.x}</button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
};

// =============================================================================
// NAVIGATION
// =============================================================================
const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', label: 'Главная', icon: Icons.dashboard },
    { path: '/products', label: 'Товары', icon: Icons.products },
    { path: '/orders', label: 'Заказы', icon: Icons.orders },
    { path: '/picking', label: 'Сборка', icon: Icons.picking },
    { path: '/placement', label: 'Склад', icon: Icons.placement },
    { path: '/logistics', label: 'Доставка', icon: Icons.logistics },
  ];

  return (
    <nav className="bg-white border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex justify-between h-14">
          <div className="flex items-center space-x-8">
            <Link to="/dashboard" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-slate-900 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">W</span>
              </div>
              <span className="font-semibold text-slate-900">WMS</span>
            </Link>
            <div className="flex items-center space-x-1">
              {navItems.map(item => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    location.pathname === item.path
                      ? 'bg-slate-100 text-slate-900'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </Link>
              ))}
            </div>
          </div>
          <div className="flex items-center">
            <div className="relative">
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-slate-50 transition-colors"
              >
                <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-slate-600">{user.fullName?.charAt(0) || 'U'}</span>
                </div>
                <span className="text-sm font-medium text-slate-700">{user.fullName || 'Пользователь'}</span>
                {Icons.chevronDown}
              </button>
              {menuOpen && (
                <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-slate-200 py-1 z-50">
                  <button onClick={handleLogout} className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors">
                    {Icons.logout}
                    <span>Выйти</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

const Layout = ({ children }: { children: React.ReactNode }) => (
  <div className="min-h-screen bg-slate-50">
    <Navigation />
    <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>
  </div>
);

// =============================================================================
// LOGIN PAGE
// =============================================================================
const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      localStorage.setItem('accessToken', response.data.access_token);
      localStorage.setItem('isLoggedIn', 'true');
      localStorage.setItem('user', JSON.stringify({
        fullName: response.data.user.full_name,
        role: response.data.user.role,
        email: response.data.user.email,
      }));
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка авторизации');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center mx-auto mb-4">
            <span className="text-slate-900 font-bold text-xl">W</span>
          </div>
          <h1 className="text-2xl font-semibold text-white">Добро пожаловать</h1>
          <p className="text-slate-400 mt-1">Система управления складом</p>
        </div>

        <div className="bg-white rounded-xl shadow-xl p-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Логин</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition"
                placeholder="admin"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Пароль</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2.5 border border-slate-200 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition"
                placeholder="••••••••"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-slate-900 text-white py-2.5 rounded-lg font-medium hover:bg-slate-800 disabled:opacity-50 transition-colors"
            >
              {loading ? 'Вход...' : 'Войти'}
            </button>
          </form>
          <p className="text-center text-slate-400 text-xs mt-4">Демо: admin / admin</p>
        </div>
      </div>
    </div>
  );
};

// =============================================================================
// DASHBOARD
// =============================================================================
const DashboardPage = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/dashboard/metrics').then(res => {
      setMetrics(res.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <Layout><div className="text-center py-20 text-slate-500">Загрузка...</div></Layout>;

  const stats = [
    { label: 'Всего товарввввв', value: metrics?.products?.total || 0, sublabel: `${metrics?.products?.active || 0} активных` },
    { label: 'Заказы', value: metrics?.orders?.total || 0, sublabel: `${metrics?.orders?.pending || 0} ожидают` },
    { label: 'Задачи сборки', value: metrics?.picking?.pending_tasks || 0, sublabel: `${metrics?.picking?.in_progress || 0} в работе` },
    { label: 'Мало на складе', value: metrics?.products?.low_stock || 0, sublabel: 'требуют пополнения' },
  ];

  return (
    <Layout>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-slate-900">Главная</h1>
        <p className="text-slate-500 mt-1">Обзор операций склада</p>
      </div>

      <div className="grid grid-cols-4 gap-6 mb-8">
        {stats.map((stat, i) => (
          <div key={i} className="bg-white rounded-xl border border-slate-200 p-6">
            <div className="text-sm font-medium text-slate-500">{stat.label}</div>
            <div className="text-3xl font-semibold text-slate-900 mt-1">{stat.value}</div>
            <div className="text-sm text-slate-400 mt-1">{stat.sublabel}</div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Быстрые действия</h2>
        <div className="grid grid-cols-4 gap-4">
          <Link to="/orders" className="p-4 border border-slate-200 rounded-lg hover:border-slate-300 hover:bg-slate-50 transition-colors">
            <div className="text-slate-900 font-medium">Новый заказ</div>
            <div className="text-sm text-slate-500 mt-1">Создать заказ</div>
          </Link>
          <Link to="/products" className="p-4 border border-slate-200 rounded-lg hover:border-slate-300 hover:bg-slate-50 transition-colors">
            <div className="text-slate-900 font-medium">Добавить товар</div>
            <div className="text-sm text-slate-500 mt-1">Новая позиция</div>
          </Link>
          <Link to="/picking" className="p-4 border border-slate-200 rounded-lg hover:border-slate-300 hover:bg-slate-50 transition-colors">
            <div className="text-slate-900 font-medium">Очередь сборки</div>
            <div className="text-sm text-slate-500 mt-1">Задачи</div>
          </Link>
          <Link to="/logistics" className="p-4 border border-slate-200 rounded-lg hover:border-slate-300 hover:bg-slate-50 transition-colors">
            <div className="text-slate-900 font-medium">Отправления</div>
            <div className="text-sm text-slate-500 mt-1">Отслеживание</div>
          </Link>
        </div>
      </div>
    </Layout>
  );
};

// =============================================================================
// PRODUCTS PAGE
// =============================================================================
const ProductsPage = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [newProduct, setNewProduct] = useState({ sku: '', name: '', price: '', stock: '' });
  const { addNotification } = useNotification();

  const loadProducts = useCallback(() => {
    setLoading(true);
    api.get('/products', { params: { search: search || undefined } })
      .then(res => { setProducts(res.data.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [search]);

  useEffect(() => { loadProducts(); }, [loadProducts]);

  const handleAdd = async () => {
    try {
      await api.post('/products', {
        sku: newProduct.sku,
        name: newProduct.name,
        price: Number(newProduct.price) || 0,
        stock: Number(newProduct.stock) || 0,
      });
      setShowModal(false);
      setNewProduct({ sku: '', name: '', price: '', stock: '' });
      loadProducts();
      addNotification('success', 'Товар добавлен');
    } catch { addNotification('error', 'Ошибка добавления'); }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/products/${id}`);
      loadProducts();
      addNotification('info', 'Товар удалён');
    } catch { addNotification('error', 'Ошибка удаления'); }
  };

  return (
    <Layout>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Товары</h1>
          <p className="text-slate-500 mt-1">Управление складскими запасами</p>
        </div>
        <button onClick={() => setShowModal(true)} className="flex items-center space-x-2 bg-slate-900 text-white px-4 py-2.5 rounded-lg font-medium hover:bg-slate-800 transition-colors">
          {Icons.plus}
          <span>Добавить товар</span>
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200">
        <div className="p-4 border-b border-slate-200">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">{Icons.search}</div>
            <input
              type="text"
              placeholder="Поиск товаров..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
            />
          </div>
        </div>

        {loading ? <p className="p-6 text-slate-500 text-center">Загрузка...</p> : (
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Артикул</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Название</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Цена</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Остаток</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Ячейка</th>
                <th className="px-6 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {products.map(p => (
                <tr key={p.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 font-mono text-sm text-slate-900">{p.sku}</td>
                  <td className="px-6 py-4">
                    <div className="text-slate-900 font-medium">{p.name}</div>
                    <div className="text-slate-400 text-sm truncate max-w-xs">{p.description}</div>
                  </td>
                  <td className="px-6 py-4 text-slate-900">{Number(p.price).toLocaleString('ru-RU')} ₽</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2.5 py-1 text-xs font-medium rounded-full ${
                      p.stock > 20 ? 'bg-emerald-50 text-emerald-700' : p.stock > 5 ? 'bg-amber-50 text-amber-700' : 'bg-red-50 text-red-700'
                    }`}>
                      {p.stock} шт
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono text-sm text-slate-500">{p.location}</td>
                  <td className="px-6 py-4">
                    <button onClick={() => handleDelete(p.id)} className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                      {Icons.trash}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Добавить товар">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Артикул</label>
            <input type="text" placeholder="PRD-007" value={newProduct.sku} onChange={(e) => setNewProduct({...newProduct, sku: e.target.value})} className="w-full px-3 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Название</label>
            <input type="text" placeholder="Название товара" value={newProduct.name} onChange={(e) => setNewProduct({...newProduct, name: e.target.value})} className="w-full px-3 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Цена</label>
              <input type="number" placeholder="0" value={newProduct.price} onChange={(e) => setNewProduct({...newProduct, price: e.target.value})} className="w-full px-3 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Количество</label>
              <input type="number" placeholder="0" value={newProduct.stock} onChange={(e) => setNewProduct({...newProduct, stock: e.target.value})} className="w-full px-3 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900" />
            </div>
          </div>
          <button onClick={handleAdd} className="w-full bg-slate-900 text-white py-2.5 rounded-lg font-medium hover:bg-slate-800 transition-colors">
            Добавить
          </button>
        </div>
      </Modal>
    </Layout>
  );
};

// =============================================================================
// ORDERS PAGE
// =============================================================================
const OrdersPage = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [newOrder, setNewOrder] = useState({ customer_name: '', customer_phone: '', customer_address: '' });
  const { addNotification } = useNotification();

  const loadOrders = useCallback(() => {
    setLoading(true);
    api.get('/orders', { params: { status: filter || undefined } })
      .then(res => { setOrders(res.data.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [filter]);

  useEffect(() => { loadOrders(); }, [loadOrders]);

  const handleCreate = async () => {
    try {
      await api.post('/orders', newOrder);
      setShowModal(false);
      setNewOrder({ customer_name: '', customer_phone: '', customer_address: '' });
      loadOrders();
      addNotification('success', 'Заказ создан');
    } catch { addNotification('error', 'Ошибка создания'); }
  };

  const updateStatus = async (id: number, status: string) => {
    try {
      await api.patch(`/orders/${id}/status?status=${status}`);
      loadOrders();
      addNotification('success', 'Статус обновлён');
    } catch { addNotification('error', 'Ошибка обновления'); }
  };

  const statusConfig: Record<string, { label: string; className: string }> = {
    pending: { label: 'Ожидает', className: 'bg-amber-50 text-amber-700' },
    picking: { label: 'Сборка', className: 'bg-blue-50 text-blue-700' },
    shipped: { label: 'Отправлен', className: 'bg-violet-50 text-violet-700' },
    delivered: { label: 'Доставлен', className: 'bg-emerald-50 text-emerald-700' },
  };

  return (
    <Layout>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Заказы</h1>
          <p className="text-slate-500 mt-1">Управление заказами клиентов</p>
        </div>
        <button onClick={() => setShowModal(true)} className="flex items-center space-x-2 bg-slate-900 text-white px-4 py-2.5 rounded-lg font-medium hover:bg-slate-800 transition-colors">
          {Icons.plus}
          <span>Новый заказ</span>
        </button>
      </div>

      <div className="flex gap-2 mb-4">
        {[
          { key: '', label: 'Все' },
          { key: 'pending', label: 'Ожидают' },
          { key: 'picking', label: 'Сборка' },
          { key: 'shipped', label: 'Отправлены' },
          { key: 'delivered', label: 'Доставлены' },
        ].map(s => (
          <button key={s.key} onClick={() => setFilter(s.key)} className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === s.key ? 'bg-slate-900 text-white' : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
          }`}>
            {s.label}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-slate-200">
        {loading ? <p className="p-6 text-slate-500 text-center">Загрузка...</p> : (
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Номер</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Клиент</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Статус</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Сумма</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Действия</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {orders.map(o => (
                <tr key={o.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 font-medium text-slate-900">{o.order_number}</td>
                  <td className="px-6 py-4">
                    <div className="text-slate-900">{o.customer_name}</div>
                    <div className="text-slate-400 text-sm">{o.customer_phone}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2.5 py-1 text-xs font-medium rounded-full ${statusConfig[o.status]?.className || 'bg-slate-100 text-slate-700'}`}>
                      {statusConfig[o.status]?.label || o.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-900 font-medium">{Number(o.total).toLocaleString('ru-RU')} ₽</td>
                  <td className="px-6 py-4">
                    <select value={o.status} onChange={(e) => updateStatus(o.id, e.target.value)} className="text-sm border border-slate-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-slate-900">
                      <option value="pending">Ожидает</option>
                      <option value="picking">Сборка</option>
                      <option value="shipped">Отправлен</option>
                      <option value="delivered">Доставлен</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Новый заказ">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Имя клиента</label>
            <input type="text" placeholder="Иван Иванов" value={newOrder.customer_name} onChange={(e) => setNewOrder({...newOrder, customer_name: e.target.value})} className="w-full px-3 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Телефон</label>
            <input type="text" placeholder="+7 999 123-45-67" value={newOrder.customer_phone} onChange={(e) => setNewOrder({...newOrder, customer_phone: e.target.value})} className="w-full px-3 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Адрес доставки</label>
            <input type="text" placeholder="Москва, ул. Примерная, д. 1" value={newOrder.customer_address} onChange={(e) => setNewOrder({...newOrder, customer_address: e.target.value})} className="w-full px-3 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900" />
          </div>
          <button onClick={handleCreate} className="w-full bg-slate-900 text-white py-2.5 rounded-lg font-medium hover:bg-slate-800 transition-colors">
            Создать заказ
          </button>
        </div>
      </Modal>
    </Layout>
  );
};

// =============================================================================
// PICKING PAGE
// =============================================================================
const PickingPage = () => {
  const [tasks, setTasks] = useState<PickingTask[]>([]);
  const [stats, setStats] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const { addNotification } = useNotification();

  const loadData = useCallback(() => {
    Promise.all([api.get('/picking/tasks'), api.get('/picking/stats')])
      .then(([t, s]) => { setTasks(t.data); setStats(s.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const startTask = async (id: number) => {
    try {
      await api.post(`/picking/tasks/${id}/start`);
      loadData();
      addNotification('info', 'Задача взята в работу');
    } catch { addNotification('error', 'Ошибка'); }
  };

  const completeTask = async (id: number) => {
    try {
      await api.post(`/picking/tasks/${id}/complete`);
      loadData();
      addNotification('success', 'Задача завершена');
    } catch { addNotification('error', 'Ошибка'); }
  };

  const statCards = [
    { label: 'Ожидают', value: stats.pending || 0, className: 'border-amber-200 bg-amber-50' },
    { label: 'В работе', value: stats.in_progress || 0, className: 'border-blue-200 bg-blue-50' },
    { label: 'Завершено сегодня', value: stats.completed_today || 0, className: 'border-emerald-200 bg-emerald-50' },
    { label: 'Среднее время', value: `${stats.average_time_minutes || 0} мин`, className: 'border-slate-200 bg-slate-50' },
  ];

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-900">Сборка заказов</h1>
        <p className="text-slate-500 mt-1">Задачи комплектации</p>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-6">
        {statCards.map((stat, i) => (
          <div key={i} className={`rounded-xl border p-4 ${stat.className}`}>
            <div className="text-2xl font-semibold text-slate-900">{stat.value}</div>
            <div className="text-sm text-slate-600">{stat.label}</div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-slate-200">
        {loading ? <p className="p-6 text-slate-500 text-center">Загрузка...</p> : tasks.filter(t => t.status !== 'completed').length === 0 ? (
          <div className="p-12 text-center">
            <div className="text-slate-400 mb-2">{Icons.check}</div>
            <p className="text-slate-500">Нет активных задач</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-200">
            {tasks.filter(t => t.status !== 'completed').map(task => (
              <div key={task.id} className="p-4 hover:bg-slate-50 transition-colors">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="flex items-center space-x-3">
                      <span className="font-medium text-slate-900">PICK-{String(task.id).padStart(3, '0')}</span>
                      <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                        task.status === 'in_progress' ? 'bg-blue-50 text-blue-700' : 'bg-amber-50 text-amber-700'
                      }`}>
                        {task.status === 'in_progress' ? 'В работе' : 'Ожидает'}
                      </span>
                    </div>
                    <div className="text-sm text-slate-500 mt-1">
                      Заказ: {task.order_number} · {task.items_count} позиций
                      {task.assigned_to && <span className="ml-2">· Исполнитель: {task.assigned_to}</span>}
                    </div>
                  </div>
                  <button
                    onClick={() => task.status === 'in_progress' ? completeTask(task.id) : startTask(task.id)}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                      task.status === 'in_progress'
                        ? 'bg-emerald-600 text-white hover:bg-emerald-700'
                        : 'bg-slate-900 text-white hover:bg-slate-800'
                    }`}
                  >
                    {task.status === 'in_progress' ? Icons.check : Icons.play}
                    <span>{task.status === 'in_progress' ? 'Завершить' : 'Начать'}</span>
                  </button>
                </div>
                {task.status === 'in_progress' && (
                  <div className="mt-3">
                    <div className="flex justify-between text-sm text-slate-500 mb-1">
                      <span>Прогресс</span>
                      <span>{task.progress}%</span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-1.5">
                      <div className="bg-blue-600 h-1.5 rounded-full transition-all" style={{width: `${task.progress}%`}} />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};

// =============================================================================
// PLACEMENT PAGE
// =============================================================================
const PlacementPage = () => {
  const [zones, setZones] = useState<Zone[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/inventory/zones').then(res => { setZones(res.data); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-900">Склад</h1>
        <p className="text-slate-500 mt-1">Заполненность зон хранения</p>
      </div>

      {loading ? <p className="text-slate-500">Загрузка...</p> : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {zones.map(zone => {
            const percent = Math.round((zone.used / zone.capacity) * 100);
            return (
              <div key={zone.id} className="bg-white rounded-xl border border-slate-200 p-5">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <div className="text-2xl font-semibold text-slate-900">{zone.code}</div>
                    <div className="text-sm text-slate-500">{zone.name}</div>
                  </div>
                  <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                    percent > 90 ? 'bg-red-50 text-red-700' : percent > 70 ? 'bg-amber-50 text-amber-700' : 'bg-emerald-50 text-emerald-700'
                  }`}>
                    {percent}%
                  </span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2">
                  <div className={`h-2 rounded-full transition-all ${
                    percent > 90 ? 'bg-red-500' : percent > 70 ? 'bg-amber-500' : 'bg-emerald-500'
                  }`} style={{width: `${percent}%`}} />
                </div>
                <div className="text-xs text-slate-400 mt-2">{zone.used.toLocaleString()} / {zone.capacity.toLocaleString()} мест</div>
              </div>
            );
          })}
        </div>
      )}
    </Layout>
  );
};

// =============================================================================
// LOGISTICS PAGE
// =============================================================================
const LogisticsPage = () => {
  const [shipments, setShipments] = useState<Shipment[]>([]);
  const [carriers, setCarriers] = useState<any[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [stats, setStats] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showTrackingModal, setShowTrackingModal] = useState<Shipment | null>(null);
  const [newShipment, setNewShipment] = useState({ order_id: '', carrier_id: '', delivery_method: 'courier' });
  const [creating, setCreating] = useState(false);
  const { addNotification } = useNotification();

  const loadData = useCallback(() => {
    Promise.all([
      api.get('/logistics/shipments'),
      api.get('/logistics/carriers'),
      api.get('/logistics/stats'),
      api.get('/orders', { params: { ready_for_shipping: true } })
    ])
      .then(([s, c, st, o]) => {
        setShipments(s.data);
        setCarriers(c.data);
        setStats(st.data);
        setOrders(o.data.data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const handleCreateShipment = async () => {
    if (!newShipment.order_id || !newShipment.carrier_id) {
      addNotification('error', 'Выберите заказ и перевозчика');
      return;
    }

    setCreating(true);
    try {
      await api.post('/logistics/shipments', {
        order_id: parseInt(newShipment.order_id),
        carrier_id: parseInt(newShipment.carrier_id),
        delivery_method: newShipment.delivery_method
      });
      setShowModal(false);
      setNewShipment({ order_id: '', carrier_id: '', delivery_method: 'courier' });
      loadData();
      addNotification('success', 'Отправление создано');
    } catch (err: any) {
      addNotification('error', err.response?.data?.detail || 'Ошибка создания');
    } finally {
      setCreating(false);
    }
  };

  const statusConfig: Record<string, { label: string; className: string }> = {
    pending: { label: 'Ожидает', className: 'bg-amber-50 text-amber-700' },
    in_transit: { label: 'В пути', className: 'bg-blue-50 text-blue-700' },
    delivered: { label: 'Доставлен', className: 'bg-emerald-50 text-emerald-700' },
  };

  const trackingHistory = [
    { time: '06.12.2024 14:30', status: 'Отправление создано', location: 'Склад WMS' },
    { time: '06.12.2024 18:00', status: 'Передано курьеру', location: 'Москва' },
    { time: '07.12.2024 09:15', status: 'В пути', location: 'Сортировочный центр' },
    { time: '07.12.2024 22:00', status: 'Прибыло в город', location: 'Пункт назначения' },
  ];

  return (
    <Layout>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Доставка</h1>
          <p className="text-slate-500 mt-1">Управление отправлениями</p>
        </div>
        <button onClick={() => setShowModal(true)} className="flex items-center space-x-2 bg-slate-900 text-white px-4 py-2.5 rounded-lg font-medium hover:bg-slate-800 transition-colors">
          {Icons.plus}
          <span>Создать отправление</span>
        </button>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <div className="text-2xl font-semibold text-slate-900">{stats.total || 0}</div>
          <div className="text-sm text-slate-500">Всего</div>
        </div>
        <div className="bg-amber-50 rounded-xl border border-amber-200 p-4">
          <div className="text-2xl font-semibold text-amber-700">{stats.pending || 0}</div>
          <div className="text-sm text-amber-600">Ожидают</div>
        </div>
        <div className="bg-blue-50 rounded-xl border border-blue-200 p-4">
          <div className="text-2xl font-semibold text-blue-700">{stats.in_transit || 0}</div>
          <div className="text-sm text-blue-600">В пути</div>
        </div>
        <div className="bg-emerald-50 rounded-xl border border-emerald-200 p-4">
          <div className="text-2xl font-semibold text-emerald-700">{stats.delivered || 0}</div>
          <div className="text-sm text-emerald-600">Доставлено</div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200">
        {loading ? <p className="p-6 text-slate-500 text-center">Загрузка...</p> : shipments.length === 0 ? (
          <div className="p-12 text-center">
            <div className="text-slate-300 mb-4">{Icons.truck}</div>
            <p className="text-slate-500">Нет отправлений</p>
            <p className="text-slate-400 text-sm">Создайте первое отправление</p>
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Трек-номер</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Заказ</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Получатель</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Перевозчик</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Статус</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Дата доставки</th>
                <th className="px-6 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {shipments.map(s => (
                <tr key={s.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 font-mono text-sm text-slate-900">{s.tracking_number}</td>
                  <td className="px-6 py-4 font-medium text-slate-900">{s.order_number}</td>
                  <td className="px-6 py-4">
                    <div className="text-slate-900">{s.recipient_name}</div>
                    <div className="text-slate-400 text-sm truncate max-w-[180px]">{s.delivery_address || '—'}</div>
                  </td>
                  <td className="px-6 py-4 text-slate-700">{s.carrier_name}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2.5 py-1 text-xs font-medium rounded-full ${statusConfig[s.status]?.className || 'bg-slate-100 text-slate-700'}`}>
                      {statusConfig[s.status]?.label || s.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-500">{s.estimated_delivery}</td>
                  <td className="px-6 py-4">
                    <button onClick={() => setShowTrackingModal(s)} className="flex items-center space-x-1 text-slate-500 hover:text-slate-900 hover:bg-slate-100 px-3 py-1.5 rounded-lg transition-colors">
                      {Icons.eye}
                      <span className="text-sm">Отследить</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Create Shipment Modal */}
      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Создать отправление">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Заказ</label>
            <select
              value={newShipment.order_id}
              onChange={(e) => setNewShipment({...newShipment, order_id: e.target.value})}
              className="w-full px-3 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
            >
              <option value="">Выберите заказ</option>
              {orders.map(o => (
                <option key={o.id} value={o.id}>
                  {o.order_number} — {o.customer_name} ({Number(o.total).toLocaleString('ru-RU')} ₽)
                </option>
              ))}
            </select>
            {orders.length === 0 && <p className="text-slate-400 text-sm mt-1">Нет заказов готовых к отправке</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Перевозчик</label>
            <select
              value={newShipment.carrier_id}
              onChange={(e) => setNewShipment({...newShipment, carrier_id: e.target.value})}
              className="w-full px-3 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
            >
              <option value="">Выберите перевозчика</option>
              {carriers.map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Способ доставки</label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { value: 'courier', label: 'Курьер' },
                { value: 'pickup', label: 'Пункт выдачи' },
                { value: 'post', label: 'Почта' },
              ].map(method => (
                <button
                  key={method.value}
                  type="button"
                  onClick={() => setNewShipment({...newShipment, delivery_method: method.value})}
                  className={`py-2.5 px-3 rounded-lg border text-sm font-medium transition-colors ${
                    newShipment.delivery_method === method.value
                      ? 'border-slate-900 bg-slate-900 text-white'
                      : 'border-slate-200 text-slate-700 hover:border-slate-300'
                  }`}
                >
                  {method.label}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleCreateShipment}
            disabled={creating || !newShipment.order_id || !newShipment.carrier_id}
            className="w-full bg-slate-900 text-white py-2.5 rounded-lg font-medium hover:bg-slate-800 disabled:opacity-50 transition-colors"
          >
            {creating ? 'Создание...' : 'Создать отправление'}
          </button>
        </div>
      </Modal>

      {/* Tracking Modal */}
      <Modal isOpen={!!showTrackingModal} onClose={() => setShowTrackingModal(null)} title="Отслеживание">
        {showTrackingModal && (
          <div className="space-y-4">
            <div className="bg-slate-50 rounded-lg p-4">
              <div className="text-xs text-slate-500 uppercase tracking-wider">Трек-номер</div>
              <div className="text-xl font-mono font-semibold text-slate-900 mt-1">{showTrackingModal.tracking_number}</div>
              <div className="text-sm text-slate-500 mt-2">
                {showTrackingModal.carrier_name} · {showTrackingModal.order_number}
              </div>
            </div>

            <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg">
              <span className="text-slate-600">Статус</span>
              <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${statusConfig[showTrackingModal.status]?.className}`}>
                {statusConfig[showTrackingModal.status]?.label}
              </span>
            </div>

            <div>
              <h4 className="text-sm font-medium text-slate-700 mb-3">История доставки</h4>
              <div className="space-y-0">
                {trackingHistory.map((event, i) => (
                  <div key={i} className="flex gap-3">
                    <div className="flex flex-col items-center">
                      <div className={`w-2 h-2 rounded-full ${i === trackingHistory.length - 1 ? 'bg-slate-900' : 'bg-slate-300'}`}></div>
                      {i < trackingHistory.length - 1 && <div className="w-px h-10 bg-slate-200"></div>}
                    </div>
                    <div className="pb-3">
                      <div className="text-sm font-medium text-slate-900">{event.status}</div>
                      <div className="text-xs text-slate-500">{event.location} · {event.time}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-slate-50 rounded-lg p-4">
              <div className="text-xs text-slate-500 uppercase tracking-wider mb-1">Получатель</div>
              <div className="font-medium text-slate-900">{showTrackingModal.recipient_name}</div>
              <div className="text-sm text-slate-500">{showTrackingModal.delivery_address || 'Адрес не указан'}</div>
            </div>
          </div>
        )}
      </Modal>
    </Layout>
  );
};

// =============================================================================
// PROTECTED ROUTE
// =============================================================================
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
  return isLoggedIn ? <>{children}</> : <Navigate to="/login" replace />;
};

// =============================================================================
// APP
// =============================================================================
const App = () => (
  <NotificationProvider>
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/products" element={<ProtectedRoute><ProductsPage /></ProtectedRoute>} />
        <Route path="/orders" element={<ProtectedRoute><OrdersPage /></ProtectedRoute>} />
        <Route path="/picking" element={<ProtectedRoute><PickingPage /></ProtectedRoute>} />
        <Route path="/placement" element={<ProtectedRoute><PlacementPage /></ProtectedRoute>} />
        <Route path="/logistics" element={<ProtectedRoute><LogisticsPage /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  </NotificationProvider>
);

const container = document.getElementById('root');
if (container) { createRoot(container).render(<App />); }

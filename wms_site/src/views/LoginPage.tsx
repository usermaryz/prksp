import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { authApi } from '../services/authApi';
import { handleApiError } from '../services/api';
import {
  AuthShell,
  authButtonClass,
  authErrorClass,
  authFieldClass,
  authLabelClass,
} from '../components/auth/AuthShell';

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const successMessage = (location.state as { message?: string } | null)?.message;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await authApi.login({ username, password });
      navigate('/dashboard');
    } catch (err) {
      const apiErr = handleApiError(err);
      setError(apiErr.message || 'Неверный логин или пароль');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthShell>
      {successMessage && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 px-4 py-3 rounded-lg mb-4 text-sm">
          {successMessage}
        </div>
      )}
      {error && <div className={authErrorClass}>{error}</div>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="username" className={authLabelClass}>
            Логин
          </label>
          <input
            id="username"
            name="username"
            type="text"
            required
            value={username}
            onChange={e => setUsername(e.target.value)}
            className={authFieldClass}
            placeholder="admin"
          />
        </div>
        <div>
          <label htmlFor="password" className={authLabelClass}>
            Пароль
          </label>
          <input
            id="password"
            name="password"
            type="password"
            required
            value={password}
            onChange={e => setPassword(e.target.value)}
            className={authFieldClass}
            placeholder="••••••••"
          />
        </div>
        <button type="submit" disabled={isLoading} className={authButtonClass}>
          {isLoading ? 'Вход...' : 'Войти'}
        </button>
      </form>

      <p className="text-center text-slate-400 text-xs mt-4">Демо: admin / admin</p>

      <p className="text-center text-sm text-slate-500 mt-6">
        Нет аккаунта?{' '}
        <Link to="/register" className="text-slate-900 font-medium hover:underline">
          Зарегистрироваться
        </Link>
      </p>
    </AuthShell>
  );
};

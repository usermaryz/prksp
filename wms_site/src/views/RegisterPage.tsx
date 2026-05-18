import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authApi } from '../services/authApi';
import { handleApiError } from '../services/api';
import {
  AuthShell,
  authButtonClass,
  authErrorClass,
  authFieldClass,
  authLabelClass,
} from '../components/auth/AuthShell';

export const RegisterPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== passwordConfirm) {
      setError('Пароли не совпадают');
      return;
    }

    if (password.length < 6) {
      setError('Пароль должен быть не короче 6 символов');
      return;
    }

    setIsLoading(true);
    try {
      await authApi.register({
        username,
        email,
        password,
        full_name: fullName,
        phone: phone.trim() || undefined,
      });
      navigate('/login', {
        state: { message: 'Регистрация успешна. Войдите с новым аккаунтом.' },
      });
    } catch (err) {
      const apiErr = handleApiError(err);
      setError(apiErr.message || 'Не удалось зарегистрироваться');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthShell title="Регистрация" subtitle="Создайте учётную запись WMS" wide>
      {error && <div className={authErrorClass}>{error}</div>}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="full_name" className={authLabelClass}>
            ФИО
          </label>
          <input
            id="full_name"
            name="full_name"
            type="text"
            required
            value={fullName}
            onChange={e => setFullName(e.target.value)}
            className={authFieldClass}
            placeholder="Иван Иванов"
          />
        </div>
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
            placeholder="ivanov"
          />
        </div>
        <div>
          <label htmlFor="email" className={authLabelClass}>
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            value={email}
            onChange={e => setEmail(e.target.value)}
            className={authFieldClass}
            placeholder="user@example.com"
          />
        </div>
        <div>
          <label htmlFor="phone" className={authLabelClass}>
            Телефон <span className="text-slate-400 font-normal">(необязательно)</span>
          </label>
          <input
            id="phone"
            name="phone"
            type="tel"
            value={phone}
            onChange={e => setPhone(e.target.value)}
            className={authFieldClass}
            placeholder="+7 999 000-00-00"
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
        <div>
          <label htmlFor="password_confirm" className={authLabelClass}>
            Повторите пароль
          </label>
          <input
            id="password_confirm"
            name="password_confirm"
            type="password"
            required
            value={passwordConfirm}
            onChange={e => setPasswordConfirm(e.target.value)}
            className={authFieldClass}
            placeholder="••••••••"
          />
        </div>
        <button type="submit" disabled={isLoading} className={authButtonClass}>
          {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
        </button>
      </form>

      <p className="text-center text-sm text-slate-500 mt-6">
        Уже есть аккаунт?{' '}
        <Link to="/login" className="text-slate-900 font-medium hover:underline">
          Войти
        </Link>
      </p>
    </AuthShell>
  );
};

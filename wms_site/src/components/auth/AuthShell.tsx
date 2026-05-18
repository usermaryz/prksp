import React from 'react';

interface AuthShellProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  wide?: boolean;
}

export const AuthShell: React.FC<AuthShellProps> = ({
  children,
  title = 'Добро пожаловать',
  subtitle = 'Система управления складом',
  wide = false,
}) => (
  <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
    <div className={`w-full ${wide ? 'max-w-md' : 'max-w-sm'}`}>
      <div className="text-center mb-8">
        <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center mx-auto mb-4">
          <span className="text-slate-900 font-bold text-xl">W</span>
        </div>
        <h1 className="text-2xl font-semibold text-white">{title}</h1>
        <p className="text-slate-400 mt-1">{subtitle}</p>
      </div>
      <div className="bg-white rounded-xl shadow-xl p-6">{children}</div>
    </div>
  </div>
);

export const authFieldClass =
  'w-full px-3 py-2.5 border border-slate-200 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition';

export const authLabelClass = 'block text-sm font-medium text-slate-700 mb-1.5';

export const authButtonClass =
  'w-full bg-slate-900 text-white py-2.5 rounded-lg font-medium hover:bg-slate-800 disabled:opacity-50 transition-colors';

export const authErrorClass =
  'bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm';

import React from 'react';

interface CardProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  className?: string;
}

const Card: React.FC<CardProps> = ({ children, title, subtitle, className = '' }) => (
  <div className={`bg-white rounded-xl border border-slate-200 ${className}`}>
    {(title || subtitle) && (
      <div className="px-6 py-4 border-b border-slate-100">
        {title && <h3 className="text-lg font-semibold text-slate-900">{title}</h3>}
        {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
      </div>
    )}
    {children}
  </div>
);

export default Card;

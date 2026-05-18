import React from 'react';
import Navigation from '../Navigation';

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => (
  <div className="min-h-screen bg-slate-50">
    <Navigation />
    <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>
  </div>
);

export default AppLayout;

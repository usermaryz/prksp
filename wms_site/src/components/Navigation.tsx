import React from 'react';
import { NavLink } from 'react-router-dom';

interface NavigationProps {
  active: string;
}

const navItems = [
  { name: 'Управление заказами', path: '/order-management' },
  { name: 'Размещение товара', path: '/product-placement' },
  { name: 'Сборка заказов', path: '/order-picking' },
  { name: 'Форма ошибки/возврата', path: '/error-return-form' },
  { name: 'Дашборд', path: '/dashboard' },
];

export const Navigation: React.FC<NavigationProps> = ({ active }) => (
  <nav style={{ backgroundColor: '#f8f9fa', padding: '10px 20px', borderBottom: '1px solid #dee2e6' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <span style={{ fontSize: '20px', fontWeight: 'bold', color: '#333', marginRight: '20px' }}>WMS Система</span>
        <div style={{ display: 'flex', gap: '15px' }}>
          {navItems.map(item => (
            <NavLink
              key={item.name}
              to={item.path}
              style={({ isActive }) => ({
                color: isActive ? '#000' : '#666',
                textDecoration: 'none',
                padding: '5px 10px',
                borderBottom: isActive ? '2px solid #007bff' : 'none'
              })}
            >
              {item.name}
            </NavLink>
          ))}
        </div>
      </div>
      <NavLink
        to="/account"
        style={({ isActive }) => ({
          color: isActive ? '#007bff' : '#666',
          textDecoration: 'none'
        })}
      >
        <div style={{
          width: '32px',
          height: '32px',
          backgroundColor: '#e9ecef',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <i className="fas fa-user"></i>
        </div>
      </NavLink>
    </div>
  </nav>
);

export default Navigation;

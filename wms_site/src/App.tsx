import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ProductPlacementPage from './views/ProductPlacementPage';
import OrderCollectionPage from './views/OrderCollectionPage';
import OrderManagementPage from './views/OrderManagementPage';
import { DashboardPage } from './views/DashboardPage';
import ErrorReturnFormPage from './views/ErrorReturnFormPage';
import { UserAccount } from './views/UserAccount';
import OrderPickingPage from './views/OrderPickingPage';
import { LoginPage } from './views/LoginPage';
import { RegisterPage } from './views/RegisterPage';
import { ProtectedRoute } from './components/ProtectedRoute';

const App: React.FC = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/product-placement"
        element={
          <ProtectedRoute>
            <ProductPlacementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/order-collection"
        element={
          <ProtectedRoute>
            <OrderCollectionPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/order-management"
        element={
          <ProtectedRoute>
            <OrderManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/order-picking"
        element={
          <ProtectedRoute>
            <OrderPickingPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/error-return-form"
        element={
          <ProtectedRoute>
            <ErrorReturnFormPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/account"
        element={
          <ProtectedRoute>
            <UserAccount />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  </BrowserRouter>
);

export default App;

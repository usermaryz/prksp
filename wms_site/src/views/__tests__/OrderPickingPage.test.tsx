import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import OrderPickingPage from '../OrderPickingPage';
import OrderPickingViewModel from '../../viewmodels/OrderPickingViewModel';

// Мокаем ViewModel
jest.mock('../../viewmodels/OrderPickingViewModel');

describe('OrderPickingPage', () => {
    beforeEach(() => {
        // Настраиваем мок ViewModel
        (OrderPickingViewModel as jest.Mock).mockImplementation(() => ({
            orders: [],
            selectedOrder: null,
            error: null,
            loadData: jest.fn(),
            searchOrders: jest.fn(),
            selectOrder: jest.fn(),
            markProductAsPicked: jest.fn(),
            updateOrderStatus: jest.fn()
        }));
    });

    it('renders search input', () => {
        render(
            <BrowserRouter>
                <OrderPickingPage />
            </BrowserRouter>
        );

        const searchInput = screen.getByPlaceholderText('Поиск заказов...');
        expect(searchInput).toBeInTheDocument();
    });
}); 
import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ProductPlacementPage from '../ProductPlacementPage';
import { ProductPlacementViewModel } from '../../viewmodels/ProductPlacementViewModel';

// Мокаем ViewModel
jest.mock('../../viewmodels/ProductPlacementViewModel');

describe('ProductPlacementPage', () => {
    const mockPlacements = [
        {
            id: 1,
            productName: 'Тестовый товар 1',
            barcode: '123456789',
            location: 'A-1-1',
            timestamp: '2024-03-20 10:00:00',
            quantity: 5,
            status: 'В обработке'
        },
        {
            id: 2,
            productName: 'Тестовый товар 2',
            barcode: '987654321',
            location: 'B-2-2',
            timestamp: '2024-03-20 11:00:00',
            quantity: 3,
            status: 'Завершен'
        }
    ];

    beforeEach(() => {
        // Настраиваем мок ViewModel
        (ProductPlacementViewModel as jest.Mock).mockImplementation(() => ({
            search: '',
            setSearch: jest.fn(),
            filteredPlacements: mockPlacements || [],
            loading: false,
            error: null,
            showModal: false,
            openModal: jest.fn(),
            closeModal: jest.fn(),
            setBarcodeInput: jest.fn(),
            scanProduct: jest.fn(),
            confirmPlacement: jest.fn(),
            acceptPlacement: jest.fn(),
            loadFromApi: jest.fn().mockResolvedValue(undefined),
        }));
    });

    it('renders search input', () => {
        render(
            <BrowserRouter>
                <ProductPlacementPage />
            </BrowserRouter>
        );

        const searchInput = screen.getByPlaceholderText('Поиск по товару или штрих-коду...');
        expect(searchInput).toBeInTheDocument();
    });
}); 
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { LoginPage } from '../LoginPage';
import { authApi } from '../../services/authApi';

// Мокаем authApi
jest.mock('../../services/authApi');

// Мокаем useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useNavigate: () => mockNavigate,
}));

describe('LoginPage', () => {
    beforeEach(() => {
        mockNavigate.mockClear();
        localStorage.clear();
    });

    it('renders login form correctly', () => {
        render(
            <BrowserRouter>
                <LoginPage />
            </BrowserRouter>
        );

        expect(screen.getByText('Вход в систему')).toBeInTheDocument();
        expect(screen.getByLabelText('Логин')).toBeInTheDocument();
        expect(screen.getByLabelText('Пароль')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Войти' })).toBeInTheDocument();
    });

    it('shows loading state during login', async () => {
        (authApi.login as jest.Mock).mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

        render(
            <BrowserRouter>
                <LoginPage />
            </BrowserRouter>
        );

        fireEvent.change(screen.getByLabelText('Логин'), { target: { value: 'admin' } });
        fireEvent.change(screen.getByLabelText('Пароль'), { target: { value: 'admin' } });
        fireEvent.click(screen.getByRole('button', { name: 'Войти' }));

        expect(screen.getByRole('button', { name: 'Вход...' })).toBeInTheDocument();
    });

    it('handles successful login', async () => {
        const mockUser = {
            fullName: 'Марк Кучер',
            role: 'Главный бригадир',
            email: 'mark.kucher@wms.com'
        };

        (authApi.login as jest.Mock).mockResolvedValue({ user: mockUser });

        render(
            <BrowserRouter>
                <LoginPage />
            </BrowserRouter>
        );

        fireEvent.change(screen.getByLabelText('Логин'), { target: { value: 'admin' } });
        fireEvent.change(screen.getByLabelText('Пароль'), { target: { value: 'admin' } });
        fireEvent.click(screen.getByRole('button', { name: 'Войти' }));

        await waitFor(() => {
            expect(localStorage.getItem('user')).toBe(JSON.stringify(mockUser));
            expect(localStorage.getItem('isLoggedIn')).toBe('true');
            expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
        });
    });

    it('handles login error', async () => {
        const errorMessage = 'Неверный логин или пароль';
        (authApi.login as jest.Mock).mockRejectedValue({
            response: { data: { message: errorMessage } }
        });

        render(
            <BrowserRouter>
                <LoginPage />
            </BrowserRouter>
        );

        fireEvent.change(screen.getByLabelText('Логин'), { target: { value: 'wrong' } });
        fireEvent.change(screen.getByLabelText('Пароль'), { target: { value: 'wrong' } });
        fireEvent.click(screen.getByRole('button', { name: 'Войти' }));

        await waitFor(() => {
            expect(screen.getByText(errorMessage)).toBeInTheDocument();
        });
    });

    it('validates required fields', () => {
        render(
            <BrowserRouter>
                <LoginPage />
            </BrowserRouter>
        );

        const loginButton = screen.getByRole('button', { name: 'Войти' });
        fireEvent.click(loginButton);

        expect(screen.getByLabelText('Логин')).toBeInvalid();
        expect(screen.getByLabelText('Пароль')).toBeInvalid();
    });
}); 
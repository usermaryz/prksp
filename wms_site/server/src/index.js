const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const port = 3001;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Простой пользователь
const adminUser = {
    username: 'admin',
    password: 'admin',
    fullName: 'Марк Кучер',
    role: 'Главный бригадир',
    email: 'mark.kucher@wms.com'
};

// Middleware для проверки авторизации
const checkAuth = (req, res, next) => {
    const { username, password } = req.body;
    if (username === adminUser.username && password === adminUser.password) {
        next();
    } else {
        res.status(401).json({ message: 'Неверный логин или пароль' });
    }
};

// Эндпоинт для входа
app.post('/api/auth/login', checkAuth, (req, res) => {
    res.json({
        user: {
            fullName: adminUser.fullName,
            role: adminUser.role,
            email: adminUser.email
        }
    });
});

// Эндпоинт для выхода
app.post('/api/auth/logout', (req, res) => {
    res.json({ message: 'Успешный выход из системы' });
});

// Моковые данные для продуктов
const products = [
    {
        id: 1,
        barcode: 'PRD12345',
        name: 'Беспроводные наушники',
        brand: 'SoundCore',
        country: 'Китай',
        category: 'Electronics',
        image: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=400&q=80',
        status: 'pending',
    },
    {
        id: 2,
        barcode: 'PRD23456',
        name: 'Белковый порошок',
        brand: 'OptimumNutrition',
        country: 'США',
        category: 'Health & Fitness',
        image: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=400&q=80',
        status: 'processing',
        location: 'A-12-3',
    },
    {
        id: 3,
        barcode: 'PRD34567',
        name: 'Механическая клавиатура',
        brand: 'Logitech',
        country: 'Тайвань',
        category: 'Computer Accessories',
        image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=400&q=80',
        status: 'completed',
        location: 'B-5-2',
        packageType: 'Box',
        containerBarcode: 'CNT123456',
    },
];

// Моковые данные для зон размещения
const zones = [
    {
        id: 1,
        name: 'Зона A',
        capacity: 1000,
        currentLoad: 750,
        status: 'available',
    },
    {
        id: 2,
        name: 'Зона B',
        capacity: 800,
        currentLoad: 800,
        status: 'full',
    },
    {
        id: 3,
        name: 'Зона C',
        capacity: 1200,
        currentLoad: 400,
        status: 'available',
    },
    {
        id: 4,
        name: 'Зона D',
        capacity: 600,
        currentLoad: 0,
        status: 'maintenance',
    },
];

// Моковые данные для метрик дашборда
const dashboardMetrics = [
    {
        icon: '📦',
        label: 'Всего товаров',
        value: '1,234',
        color: 'bg-blue-500'
    },
    {
        icon: '🚚',
        label: 'Заказов сегодня',
        value: '56',
        color: 'bg-green-500'
    },
    {
        icon: '⚠️',
        label: 'Ошибок',
        value: '3',
        color: 'bg-red-500'
    },
    {
        icon: '📊',
        label: 'Эффективность',
        value: '98%',
        color: 'bg-purple-500'
    }
];

// API endpoints

// Получить список продуктов
app.get('/api/placement/products', (req, res) => {
    res.json(products);
});

// Получить список зон размещения
app.get('/api/placement/zones', (req, res) => {
    res.json(zones);
});

// Обновить местоположение продукта
app.patch('/api/placement/products/:id', (req, res) => {
    const productId = parseInt(req.params.id);
    const { location } = req.body;

    const product = products.find(p => p.id === productId);
    if (!product) {
        return res.status(404).json({ error: 'Product not found' });
    }

    product.location = location;
    res.json(product);
});

// Поиск продуктов
app.get('/api/placement/products/search', (req, res) => {
    const query = req.query.q?.toLowerCase() || '';

    const filteredProducts = products.filter(
        p =>
            p.barcode.toLowerCase().includes(query) ||
            p.name.toLowerCase().includes(query) ||
            p.brand.toLowerCase().includes(query) ||
            p.country.toLowerCase().includes(query) ||
            p.category.toLowerCase().includes(query)
    );

    res.json(filteredProducts);
});

// Поиск зон размещения
app.get('/api/placement/zones/search', (req, res) => {
    const query = req.query.q?.toLowerCase() || '';

    const filteredZones = zones.filter(z =>
        z.name.toLowerCase().includes(query)
    );

    res.json(filteredZones);
});

// Эндпоинт для получения метрик дашборда
app.get('/api/dashboard/metrics', (req, res) => {
    res.json(dashboardMetrics);
});

// Запуск сервера
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
}); 
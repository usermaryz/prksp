const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();

const { setupSwagger } = require('./swagger');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Swagger Documentation
setupSwagger(app);

// Routes
app.use('/api/products', require('./routes/productRoutes'));
app.use('/api/orders', require('./routes/orderRoutes'));
app.use('/api/errors', require('./routes/errorRoutes'));

// TODO: Add these routes when implemented
// app.use('/api/auth', require('./routes/authRoutes'));
// app.use('/api/users', require('./routes/userRoutes'));
// app.use('/api/placement', require('./routes/placementRoutes'));
// app.use('/api/picking', require('./routes/pickingRoutes'));
// app.use('/api/dashboard', require('./routes/dashboardRoutes'));
// app.use('/api/logistics', require('./routes/logisticsRoutes'));
// app.use('/api/delivery', require('./routes/deliveryRoutes'));

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API info endpoint
app.get('/api', (req, res) => {
    res.json({
        name: 'WMS API',
        version: '1.0.0',
        description: 'Warehouse Management System API',
        documentation: '/api-docs',
        endpoints: {
            auth: '/api/auth',
            users: '/api/users',
            products: '/api/products',
            orders: '/api/orders',
            placement: '/api/placement',
            picking: '/api/picking',
            dashboard: '/api/dashboard',
            logistics: '/api/logistics',
            delivery: '/api/delivery',
        },
    });
});

// MongoDB connection (optional - server will work without it for Swagger docs)
if (process.env.MONGODB_URI || process.env.ENABLE_DB === 'true') {
    mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/wms_db', {
        useNewUrlParser: true,
        useUnifiedTopology: true
    })
        .then(() => console.log('✅ Connected to MongoDB'))
        .catch(err => console.error('❌ MongoDB connection error:', err));
} else {
    console.log('ℹ️  Running without MongoDB (Swagger docs only mode)');
}

// 404 handler
app.use((req, res, next) => {
    res.status(404).json({
        success: false,
        error: 'Endpoint not found',
        path: req.path,
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({
        success: false,
        error: 'Something went wrong!',
        message: process.env.NODE_ENV === 'development' ? err.message : undefined,
    });
});

const PORT = process.env.PORT || 3002;
app.listen(PORT, () => {
    console.log(`🚀 Server is running on port ${PORT}`);
    console.log(`📚 API Documentation: http://localhost:${PORT}/api-docs`);
});

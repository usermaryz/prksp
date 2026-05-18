-- =============================================================================
-- Product Service Database
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Categories
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES categories(id),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Brands
CREATE TABLE IF NOT EXISTS brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    logo_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    barcode VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(12, 2),
    cost_price DECIMAL(12, 2),
    weight DECIMAL(10, 3),
    length DECIMAL(10, 2),
    width DECIMAL(10, 2),
    height DECIMAL(10, 2),
    category_id INTEGER REFERENCES categories(id),
    brand_id INTEGER REFERENCES brands(id),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'discontinued')),
    min_stock_level INTEGER DEFAULT 0,
    max_stock_level INTEGER DEFAULT 1000,
    reorder_point INTEGER DEFAULT 10,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand_id);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);

-- Initial data
INSERT INTO categories (name, description, sort_order) VALUES
('Электроника', 'Смартфоны, планшеты, ноутбуки', 1),
('Аудио', 'Наушники, колонки, аудиотехника', 2),
('Компьютеры', 'Ноутбуки, ПК, комплектующие', 3),
('Бытовая техника', 'Техника для дома', 4),
('Одежда', 'Одежда и аксессуары', 5)
ON CONFLICT DO NOTHING;

INSERT INTO brands (name, description) VALUES
('Apple', 'Apple Inc.'),
('Samsung', 'Samsung Electronics'),
('Sony', 'Sony Corporation'),
('Xiaomi', 'Xiaomi Corporation'),
('LG', 'LG Electronics')
ON CONFLICT DO NOTHING;

INSERT INTO products (sku, barcode, name, description, price, category_id, brand_id) VALUES
('PRD-001', '4000000000001', 'iPhone 15 Pro', 'Смартфон Apple iPhone 15 Pro 256GB', 99990, 1, 1),
('PRD-002', '4000000000002', 'Samsung Galaxy S24', 'Смартфон Samsung Galaxy S24 Ultra', 84990, 1, 2),
('PRD-003', '4000000000003', 'Sony WH-1000XM5', 'Беспроводные наушники', 34990, 2, 3),
('PRD-004', '4000000000004', 'MacBook Pro 14', 'Ноутбук Apple MacBook Pro 14" M3 Pro', 199990, 3, 1),
('PRD-005', '4000000000005', 'iPad Air', 'Планшет Apple iPad Air 5 256GB', 64990, 1, 1),
('PRD-006', '4000000000006', 'AirPods Pro 2', 'Беспроводные наушники Apple', 24990, 2, 1)
ON CONFLICT (sku) DO NOTHING;


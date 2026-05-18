-- =============================================================================
-- Order Service Database
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Customers
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20) NOT NULL,
    company_name VARCHAR(200),
    inn VARCHAR(20),
    is_corporate BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Addresses
CREATE TABLE IF NOT EXISTS addresses (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    city VARCHAR(100) NOT NULL,
    street VARCHAR(200) NOT NULL,
    building VARCHAR(50) NOT NULL,
    apartment VARCHAR(20),
    postal_code VARCHAR(20),
    entrance VARCHAR(10),
    floor VARCHAR(10),
    intercom VARCHAR(20),
    notes TEXT,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    external_id VARCHAR(100),
    customer_id INTEGER REFERENCES customers(id),
    shipping_address_id INTEGER REFERENCES addresses(id),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'picking', 'packed', 'shipped', 'delivered', 'cancelled')),
    priority VARCHAR(10) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    delivery_method VARCHAR(20) DEFAULT 'courier' CHECK (delivery_method IN ('courier', 'pickup', 'post', 'transport')),
    subtotal DECIMAL(12, 2) DEFAULT 0,
    discount DECIMAL(12, 2) DEFAULT 0,
    shipping_cost DECIMAL(12, 2) DEFAULT 0,
    total DECIMAL(12, 2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP
);

-- Order items
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL,
    product_barcode VARCHAR(50),
    product_name VARCHAR(255),
    quantity INTEGER NOT NULL,
    picked_quantity INTEGER DEFAULT 0,
    unit_price DECIMAL(12, 2),
    total_price DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_orders_number ON orders(order_number);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);

-- Initial data
INSERT INTO customers (name, email, phone, is_corporate) VALUES
('Иван Иванов', 'ivan@example.com', '+7 999 123-45-67', false),
('ООО Ромашка', 'info@romashka.ru', '+7 495 111-22-33', true)
ON CONFLICT DO NOTHING;

INSERT INTO addresses (customer_id, city, street, building, apartment, postal_code, is_default) VALUES
(1, 'Москва', 'ул. Ленина', '15', '42', '101000', true),
(2, 'Москва', 'ул. Тверская', '1', null, '125009', true)
ON CONFLICT DO NOTHING;


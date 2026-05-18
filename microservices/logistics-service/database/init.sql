-- =============================================================================
-- Logistics Service Database
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Carriers
CREATE TABLE IF NOT EXISTS carriers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    tracking_url_template VARCHAR(500),
    api_url VARCHAR(500),
    api_key VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Shipments
CREATE TABLE IF NOT EXISTS shipments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    order_number VARCHAR(50) NOT NULL,
    tracking_number VARCHAR(100) UNIQUE NOT NULL,
    carrier_id INTEGER REFERENCES carriers(id),
    delivery_method VARCHAR(20) CHECK (delivery_method IN ('courier', 'pickup_point', 'post')),
    status VARCHAR(30) DEFAULT 'pending' CHECK (status IN ('pending', 'label_created', 'picked_up', 'in_transit', 'out_for_delivery', 'delivered', 'failed', 'returned')),
    recipient_name VARCHAR(100) NOT NULL,
    recipient_phone VARCHAR(20) NOT NULL,
    delivery_address TEXT NOT NULL,
    delivery_city VARCHAR(100),
    delivery_postal_code VARCHAR(20),
    estimated_delivery DATE,
    actual_delivery TIMESTAMP,
    weight DECIMAL(10, 3),
    declared_value DECIMAL(12, 2),
    shipping_cost DECIMAL(12, 2),
    label_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tracking events
CREATE TABLE IF NOT EXISTS tracking_events (
    id SERIAL PRIMARY KEY,
    shipment_id INTEGER REFERENCES shipments(id) ON DELETE CASCADE,
    status VARCHAR(30),
    location VARCHAR(200),
    description TEXT,
    event_time TIMESTAMP,
    raw_status VARCHAR(100),
    source VARCHAR(50) DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Delivery rates cache
CREATE TABLE IF NOT EXISTS delivery_rates (
    id SERIAL PRIMARY KEY,
    carrier_id INTEGER REFERENCES carriers(id),
    from_city VARCHAR(100),
    to_city VARCHAR(100),
    weight_min DECIMAL(10, 3),
    weight_max DECIMAL(10, 3),
    price DECIMAL(12, 2),
    estimated_days INTEGER,
    valid_from DATE,
    valid_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_shipments_order ON shipments(order_id);
CREATE INDEX IF NOT EXISTS idx_shipments_tracking ON shipments(tracking_number);
CREATE INDEX IF NOT EXISTS idx_shipments_status ON shipments(status);
CREATE INDEX IF NOT EXISTS idx_shipments_carrier ON shipments(carrier_id);
CREATE INDEX IF NOT EXISTS idx_tracking_events_shipment ON tracking_events(shipment_id);

-- Initial carriers
INSERT INTO carriers (code, name, tracking_url_template) VALUES
('cdek', 'СДЭК', 'https://www.cdek.ru/ru/tracking?order_id={tracking}'),
('boxberry', 'Boxberry', 'https://boxberry.ru/tracking?id={tracking}'),
('russian_post', 'Почта России', 'https://www.pochta.ru/tracking#{tracking}'),
('dpd', 'DPD', 'https://www.dpd.ru/ols/trace2/standard.do?parcelNumber={tracking}'),
('dellin', 'Деловые Линии', 'https://www.dellin.ru/tracker/?docNumber={tracking}')
ON CONFLICT (code) DO NOTHING;


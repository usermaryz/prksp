-- =============================================================================
-- Inventory Service Database
-- Таблицы: warehouses, zones (warehouse_zones), locations (storage_locations), inventory
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Склады (warehouses)
CREATE TABLE IF NOT EXISTS warehouses (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    address TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Зоны склада (zones) — в коде ORM: warehouse_zones
CREATE TABLE IF NOT EXISTS warehouse_zones (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER REFERENCES warehouses(id),
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    zone_type VARCHAR(20) DEFAULT 'storage' CHECK (zone_type IN ('storage', 'picking', 'receiving', 'shipping', 'staging')),
    capacity INTEGER DEFAULT 1000,
    current_usage INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ячейки / локации (locations) — в коде ORM: storage_locations
CREATE TABLE IF NOT EXISTS storage_locations (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER REFERENCES warehouse_zones(id),
    code VARCHAR(20) UNIQUE NOT NULL,
    aisle VARCHAR(10),
    rack VARCHAR(10),
    shelf VARCHAR(10),
    bin VARCHAR(10),
    location_type VARCHAR(20) DEFAULT 'bulk' CHECK (location_type IN ('bulk', 'pick', 'reserve')),
    max_weight DECIMAL(10, 2),
    max_volume DECIMAL(10, 2),
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Остатки
CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    location_id INTEGER REFERENCES storage_locations(id),
    quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER DEFAULT 0,
    lot_number VARCHAR(50),
    expiry_date DATE,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_counted_at TIMESTAMP,
    UNIQUE(product_id, location_id, lot_number)
);

CREATE TABLE IF NOT EXISTS stock_movements (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    from_location_id INTEGER REFERENCES storage_locations(id),
    to_location_id INTEGER REFERENCES storage_locations(id),
    quantity INTEGER NOT NULL,
    movement_type VARCHAR(20) CHECK (movement_type IN ('receive', 'ship', 'transfer', 'adjustment', 'return')),
    reference_type VARCHAR(50),
    reference_id INTEGER,
    reason TEXT,
    performed_by INTEGER,
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Псевдонимы для отчёта / SQL-запросов
CREATE OR REPLACE VIEW zones AS SELECT * FROM warehouse_zones;
CREATE OR REPLACE VIEW locations AS SELECT * FROM storage_locations;

CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_location ON inventory(location_id);
CREATE INDEX IF NOT EXISTS idx_locations_zone ON storage_locations(zone_id);
CREATE INDEX IF NOT EXISTS idx_zones_warehouse ON warehouse_zones(warehouse_id);

INSERT INTO warehouses (code, name, address) VALUES
('WH-01', 'Центральный склад', 'г. Москва, ул. Складская, 1')
ON CONFLICT (code) DO NOTHING;

INSERT INTO warehouse_zones (warehouse_id, code, name, zone_type, capacity) VALUES
(1, 'A', 'Зона A - Электроника', 'storage', 1000),
(1, 'B', 'Зона B - Бытовая техника', 'storage', 800),
(1, 'C', 'Зона C - Одежда', 'storage', 1200),
(1, 'D', 'Зона D - Продукты', 'storage', 500),
(1, 'R', 'Зона приёмки', 'receiving', 200),
(1, 'S', 'Зона отгрузки', 'shipping', 200)
ON CONFLICT (code) DO NOTHING;

INSERT INTO storage_locations (zone_id, code, aisle, rack, shelf, bin, location_type) VALUES
(1, 'A-01-01', 'A', '01', '01', '01', 'pick'),
(1, 'A-01-02', 'A', '01', '01', '02', 'pick'),
(1, 'A-01-03', 'A', '01', '01', '03', 'pick'),
(1, 'A-02-01', 'A', '02', '01', '01', 'bulk'),
(2, 'B-01-01', 'B', '01', '01', '01', 'pick'),
(3, 'C-01-01', 'C', '01', '01', '01', 'pick')
ON CONFLICT (code) DO NOTHING;

INSERT INTO inventory (product_id, location_id, quantity) VALUES
(1, 1, 45),
(2, 2, 32),
(3, 5, 18)
ON CONFLICT DO NOTHING;

-- =============================================================================
-- Picking Service Database
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Picking tasks
CREATE TABLE IF NOT EXISTS picking_tasks (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    order_number VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'assigned', 'in_progress', 'completed', 'cancelled')),
    priority VARCHAR(10) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    assigned_to INTEGER,
    assigned_to_name VARCHAR(100),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Picking items
CREATE TABLE IF NOT EXISTS picking_items (
    id SERIAL PRIMARY KEY,
    picking_task_id INTEGER REFERENCES picking_tasks(id) ON DELETE CASCADE,
    order_item_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(255),
    product_barcode VARCHAR(50),
    location_id INTEGER,
    location_code VARCHAR(20),
    quantity_to_pick INTEGER NOT NULL,
    quantity_picked INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'picked', 'short')),
    picked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Picking stats (aggregated daily)
CREATE TABLE IF NOT EXISTS picking_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    tasks_created INTEGER DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0,
    items_picked INTEGER DEFAULT 0,
    average_time_minutes DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_picking_tasks_order ON picking_tasks(order_id);
CREATE INDEX IF NOT EXISTS idx_picking_tasks_status ON picking_tasks(status);
CREATE INDEX IF NOT EXISTS idx_picking_tasks_assigned ON picking_tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_picking_items_task ON picking_items(picking_task_id);
CREATE INDEX IF NOT EXISTS idx_picking_items_product ON picking_items(product_id);


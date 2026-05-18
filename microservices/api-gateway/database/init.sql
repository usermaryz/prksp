-- =============================================================================
-- API Gateway Database (для rate limiting и логов)
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Rate limiting
CREATE TABLE IF NOT EXISTS rate_limits (
    id SERIAL PRIMARY KEY,
    client_ip VARCHAR(45),
    endpoint VARCHAR(200),
    request_count INTEGER DEFAULT 1,
    window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Request logs
CREATE TABLE IF NOT EXISTS request_logs (
    id SERIAL PRIMARY KEY,
    request_id UUID DEFAULT uuid_generate_v4(),
    method VARCHAR(10),
    path VARCHAR(500),
    query_params TEXT,
    client_ip VARCHAR(45),
    user_id INTEGER,
    status_code INTEGER,
    response_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_rate_limits_ip ON rate_limits(client_ip);
CREATE INDEX IF NOT EXISTS idx_request_logs_created ON request_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_request_logs_user ON request_logs(user_id);


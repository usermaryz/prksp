// API Configuration (подставляется webpack DefinePlugin из REACT_APP_API_URL).
// Для same-origin за nginx задайте при сборке REACT_APP_API_URL=/api
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
export const API_TIMEOUT = 30000;

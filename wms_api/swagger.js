/**
 * Swagger Configuration
 * Конфигурация Swagger UI для WMS API
 */

const swaggerUi = require('swagger-ui-express');
const YAML = require('yamljs');
const path = require('path');

// Загружаем OpenAPI спецификацию из YAML файла
const swaggerDocument = YAML.load(path.join(__dirname, 'api-contracts.yaml'));

// Опции для Swagger UI
const swaggerOptions = {
    customCss: `
        .swagger-ui .topbar { display: none }
        .swagger-ui .info { margin: 30px 0 }
        .swagger-ui .info .title { color: #3b82f6 }
    `,
    customSiteTitle: 'WMS API Documentation',
    customfavIcon: '/favicon.ico',
    swaggerOptions: {
        persistAuthorization: true,
        displayRequestDuration: true,
        docExpansion: 'none',
        filter: true,
        showExtensions: true,
        showCommonExtensions: true,
        tagsSorter: 'alpha',
        operationsSorter: 'alpha',
    },
};

/**
 * Настройка Swagger для Express приложения
 * @param {Express} app - Express приложение
 */
function setupSwagger(app) {
    // Swagger UI доступен по /api-docs
    app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument, swaggerOptions));
    
    // JSON версия спецификации
    app.get('/api-docs.json', (req, res) => {
        res.setHeader('Content-Type', 'application/json');
        res.send(swaggerDocument);
    });
    
    // YAML версия спецификации
    app.get('/api-docs.yaml', (req, res) => {
        res.setHeader('Content-Type', 'text/yaml');
        res.sendFile(path.join(__dirname, 'api-contracts.yaml'));
    });
    
    console.log('📚 Swagger UI available at /api-docs');
}

module.exports = { setupSwagger, swaggerDocument };


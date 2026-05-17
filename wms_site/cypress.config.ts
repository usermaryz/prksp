import { defineConfig } from 'cypress';

export default defineConfig({
    component: {
        devServer: {
            framework: 'react',
            bundler: 'webpack',
            webpackConfig: require('./webpack.config.js')
        },
        specPattern: 'src/**/*.cy.{js,jsx,ts,tsx}',
        supportFile: 'cypress/support/component.tsx',
        indexHtmlFile: 'cypress/support/component-index.html'
    },
    e2e: {
        baseUrl: 'http://localhost:3000',
        defaultCommandTimeout: 10000,
        specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
        supportFile: 'cypress/support/e2e.ts',
        setupNodeEvents(on, config) {
            const webpack = require('@cypress/webpack-preprocessor');
            on('file:preprocessor', webpack({ webpackOptions: require('./cypress/webpack.config.js') }));
            return config;
        }
    },
}); 
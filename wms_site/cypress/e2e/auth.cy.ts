describe('Авторизация', () => {
    beforeEach(() => {
        cy.clearLocalStorage();
        cy.visit('/login');
    });

    it('успешная авторизация', () => {
        cy.get('input[type="text"]').first().clear().type('admin');
        cy.get('input[type="password"]').clear().type('admin');
        cy.get('button[type="submit"]').click();

        cy.window().its('localStorage').should('have.property', 'isLoggedIn', 'true');
        cy.window().its('localStorage').should('have.property', 'accessToken');
        cy.url().should('include', '/dashboard');
    });

    it('отображение ошибки при неверных данных', () => {
        cy.get('input[type="text"]').first().clear().type('wrong');
        cy.get('input[type="password"]').clear().type('wrong');
        cy.get('button[type="submit"]').click();

        cy.contains('Неверный логин или пароль', { timeout: 10000 }).should('be.visible');
    });

    it('форма входа отображается', () => {
        cy.contains('Добро пожаловать').should('be.visible');
        cy.contains('Система управления складом').should('be.visible');
        cy.get('input[type="text"]').should('have.length.at.least', 1);
        cy.get('input[type="password"]').should('be.visible');
        cy.contains('Демо: admin / admin').should('be.visible');
    });
});

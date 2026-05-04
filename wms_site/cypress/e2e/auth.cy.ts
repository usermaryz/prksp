describe('Авторизация', () => {
    beforeEach(() => {
        cy.visit('/login');
    });

    it('успешная авторизация', () => {
        cy.get('input[name="username"]').type('admin');
        cy.get('input[name="password"]').type('admin');
        cy.get('button[type="submit"]').click();

        // Проверяем, что данные сохранились в localStorage
        cy.window().its('localStorage').should('have.property', 'isLoggedIn', 'true');
        cy.window().its('localStorage').should('have.property', 'user');

        // Проверяем редирект на dashboard
        cy.url().should('include', '/dashboard');
    });

    it('отображение ошибки при неверных данных', () => {
        cy.get('input[name="username"]').type('wrong');
        cy.get('input[name="password"]').type('wrong');
        cy.get('button[type="submit"]').click();

        // Проверяем сообщение об ошибке
        cy.get('[role="alert"]').should('be.visible');
        cy.get('[role="alert"]').should('contain', 'Неверный логин или пароль');
    });

    it('валидация обязательных полей', () => {
        cy.get('button[type="submit"]').click();

        // Проверяем, что поля помечены как required
        cy.get('input[name="username"]').should('have.attr', 'required');
        cy.get('input[name="password"]').should('have.attr', 'required');
    });
}); 
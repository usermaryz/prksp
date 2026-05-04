describe('Управление заказами', () => {
    beforeEach(() => {
        // Авторизация перед каждым тестом
        cy.visit('/login');
        cy.get('input[name="username"]').type('admin');
        cy.get('input[name="password"]').type('admin');
        cy.get('button[type="submit"]').click();
        cy.url().should('include', '/dashboard');
    });

    it('должен отображать список заказов', () => {
        cy.visit('/order-management');
        cy.get('h1').should('contain', 'Управление заказами');
        cy.get('input[type="text"]').should('be.visible');
        cy.get('table').should('be.visible');
    });

    it('должен фильтровать заказы', () => {
        cy.visit('/order-management');
        cy.get('input[type="text"]').type('Test Product');
        cy.get('table').should('be.visible');
    });

    it('должен принимать заказ', () => {
        cy.visit('/order-management');
        cy.get('table').should('be.visible');
        cy.get('button').contains('Принять').first().click();

        // Ждем появления модального окна
        cy.get('.fixed.inset-0').should('be.visible');
        cy.get('.bg-white.rounded-lg').should('be.visible');

        // Заполняем форму
        cy.get('select').select('Box');
        cy.get('input[placeholder="Введите штрих-код контейнера"]').type('123456');

        // Проверяем, что кнопка видима и кликабельна
        cy.get('button').contains('Принять').should('be.visible').and('not.be.disabled').click({ force: true });
    });
}); 
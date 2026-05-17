describe('Управление заказами', () => {
    beforeEach(() => {
        cy.clearLocalStorage();
        cy.visit('/login');
        cy.get('input[type="text"]').first().clear().type('admin');
        cy.get('input[type="password"]').clear().type('admin');
        cy.get('button[type="submit"]').click();
        cy.url().should('include', '/dashboard');
    });

    it('отображает список заказов', () => {
        cy.visit('/orders');
        cy.contains('h1', 'Заказы').should('be.visible');
        cy.get('table').should('be.visible');
    });

    it('фильтрует заказы по статусу', () => {
        cy.visit('/orders');
        cy.contains('button', 'Ожидают').click();
        cy.get('table').should('be.visible');
    });

    it('открывает форму создания заказа', () => {
        cy.visit('/orders');
        cy.contains('button', 'Новый заказ').click();
        cy.contains('Новый заказ').should('be.visible');
        cy.get('input[placeholder="Иван Иванов"]').should('be.visible');
    });
});

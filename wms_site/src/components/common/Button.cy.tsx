import React from 'react';
import { mount } from '@cypress/react';
import Button from './Button';

describe('Компонент Кнопка', () => {
    it('отображает кнопку с правильным текстом', () => {
        mount(<Button>Click me</Button>);
        cy.get('button').should('contain', 'Click me');
    });

    it('обрабатывает события клика', () => {
        const onClickSpy = cy.spy().as('onClickSpy');
        mount(<Button onClick={onClickSpy}>Click me</Button>);
        cy.get('button').click();
        cy.get('@onClickSpy').should('have.been.called');
    });

    it('применяет стили основного варианта', () => {
        mount(<Button variant="primary">Primary Button</Button>);
        cy.get('button').should('have.class', 'bg-slate-900');
    });

    it('применяет стили вторичного варианта', () => {
        mount(<Button variant="secondary">Secondary Button</Button>);
        cy.get('button').should('have.class', 'bg-gray-200');
    });

    it('применяет стили варианта опасности', () => {
        mount(<Button variant="danger">Danger Button</Button>);
        cy.get('button').should('have.class', 'bg-red-600');
    });

    it('отключает кнопку при disabled=true', () => {
        mount(<Button disabled>Disabled Button</Button>);
        cy.get('button').should('be.disabled');
        cy.get('button').should('have.class', 'opacity-50');
    });

    it('применяет пользовательский класс', () => {
        mount(<Button className="custom-class">Custom Button</Button>);
        cy.get('button').should('have.class', 'custom-class');
    });

    it('применяет разные размеры', () => {
        mount(<Button size="sm">Small Button</Button>);
        cy.get('button').should('have.class', 'px-3');

        mount(<Button size="md">Medium Button</Button>);
        cy.get('button').should('have.class', 'px-4');

        mount(<Button size="lg">Large Button</Button>);
        cy.get('button').should('have.class', 'px-6');
    });
}); 
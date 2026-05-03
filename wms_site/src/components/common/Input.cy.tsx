import React from 'react';
import { mount } from '@cypress/react';
import Input from './Input';

describe('Компонент Поле ввода', () => {
    it('отображает поле с правильным плейсхолдером', () => {
        mount(<Input placeholder="Enter text" />);
        cy.get('input').should('have.attr', 'placeholder', 'Enter text');
    });

    it('обрабатывает изменения в поле ввода', () => {
        const onChangeSpy = cy.spy().as('onChangeSpy');
        mount(<Input onChange={onChangeSpy} />);
        cy.get('input').type('test');
        cy.get('@onChangeSpy').should('have.been.called');
    });

    it('отображает сообщение об ошибке при наличии ошибки', () => {
        mount(<Input error="This field is required" />);
        cy.get('.text-red-500').should('contain', 'This field is required');
    });

    it('применяет состояние отключения', () => {
        mount(<Input disabled />);
        cy.get('input').should('be.disabled');
    });

    it('применяет пользовательский класс', () => {
        mount(<Input className="custom-input" />);
        cy.get('input').should('have.class', 'custom-input');
    });

    it('обрабатывает разные типы полей ввода', () => {
        mount(<Input type="password" />);
        cy.get('input').should('have.attr', 'type', 'password');
    });

    it('отображает метку при её наличии', () => {
        mount(<Input label="Username" />);
        cy.get('label').should('contain', 'Username');
    });

    it('обрабатывает значение поля', () => {
        mount(<Input value="test value" />);
        cy.get('input').should('have.value', 'test value');
    });
}); 
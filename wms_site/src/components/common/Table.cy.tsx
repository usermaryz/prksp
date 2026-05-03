import React from 'react';
import { mount } from '@cypress/react';
import Table from './Table';

describe('Компонент Таблица', () => {
    const mockData = [
        { id: 1, name: 'Item 1', status: 'Active' },
        { id: 2, name: 'Item 2', status: 'Inactive' },
    ];

    const mockColumns = [
        { header: 'Name', accessor: 'name' },
        { header: 'Status', accessor: 'status' },
    ];

    beforeEach(() => {
        mount(
            <Table
                data={mockData}
                columns={mockColumns}
                onRowClick={() => { }}
            />
        );
    });

    it('отображает правильное количество строк', () => {
        cy.get('table tbody tr').should('have.length', mockData.length);
    });

    it('корректно отображает заголовки таблицы', () => {
        mockColumns.forEach(column => {
            cy.get('table thead th').contains(column.header).should('be.visible');
        });
    });

    it('отображает правильные данные в ячейках', () => {
        mockData.forEach((row, index) => {
            cy.get(`table tbody tr:nth-child(${index + 1}) td`).should(($cells) => {
                expect($cells[0]).to.contain(row.name);
                expect($cells[1]).to.contain(row.status);
            });
        });
    });

    it('вызывает onRowClick при клике на строку', () => {
        const onRowClickSpy = cy.spy().as('onRowClickSpy');
        mount(
            <Table
                data={mockData}
                columns={mockColumns}
                onRowClick={onRowClickSpy}
            />
        );
        cy.get('table tbody tr').first().click();
        cy.get('@onRowClickSpy').should('have.been.calledWith', mockData[0]);
    });
}); 
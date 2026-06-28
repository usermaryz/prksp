from __future__ import annotations

from ..queries import (
    GetProductQuery,
    ListCategoriesQuery,
    ListProductsQuery,
    ListZonesQuery,
)
from ..services.catalog_query_service import CatalogQueryService
from ..services.product_application_service import ProductApplicationService


def handle_get_product(query: GetProductQuery, service: ProductApplicationService):
    return service.get_product(query.product_id)


def handle_list_products(query: ListProductsQuery, service: ProductApplicationService):
    return service.list_products(
        search=query.search,
        category=query.category,
        page=query.page,
        limit=query.limit,
    )


def handle_list_categories(_query: ListCategoriesQuery, catalog: CatalogQueryService):
    return catalog.list_categories()


def handle_list_zones(_query: ListZonesQuery, catalog: CatalogQueryService):
    return catalog.list_zones()

from __future__ import annotations

from sqlalchemy.orm import Session

from ...infrastructure.persistence.models import CategoryModel, WarehouseZoneModel


class CatalogQueryService:
    """Read-side queries for product catalog metadata."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_categories(self) -> list[CategoryModel]:
        return (
            self._db.query(CategoryModel)
            .filter(CategoryModel.is_active == True)  # noqa: E712
            .all()
        )

    def list_zones(self) -> list[WarehouseZoneModel]:
        return (
            self._db.query(WarehouseZoneModel)
            .filter(WarehouseZoneModel.is_active == True)  # noqa: E712
            .all()
        )

from typing import List, Optional
from sqlalchemy.orm import Session

from ...domain.entities.carrier import Carrier
from ...domain.repositories.carrier_repository import CarrierRepository
from .models import CarrierModel


class SQLAlchemyCarrierRepository(CarrierRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, carrier_id: int) -> Optional[Carrier]:
        model = self._session.query(CarrierModel).filter(
            CarrierModel.id == carrier_id
        ).first()
        if not model:
            return None

        return self._to_entity(model)

    def find_all_active(self) -> List[Carrier]:
        models = self._session.query(CarrierModel).filter(
            CarrierModel.is_active == 1
        ).all()

        return [self._to_entity(m) for m in models]

    def save(self, carrier: Carrier) -> Carrier:
        model = CarrierModel(
            id=carrier.id,
            code=carrier.code,
            name=carrier.name,
            is_active=1 if carrier.is_active else 0,
        )
        self._session.merge(model)
        self._session.commit()

        return carrier

    def _to_entity(self, model: CarrierModel) -> Carrier:
        return Carrier(
            id=model.id,
            code=model.code,
            name=model.name,
            is_active=bool(model.is_active),
        )

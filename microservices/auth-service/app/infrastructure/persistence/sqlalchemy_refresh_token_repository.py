from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from .models import RefreshTokenModel


@dataclass
class RefreshTokenRecord:
    id: int
    user_id: int
    token: str
    expires_at: datetime
    revoked_at: Optional[datetime]


class SQLAlchemyRefreshTokenRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def find_by_jti(self, jti: str) -> Optional[RefreshTokenRecord]:
        row = (
            self._db.query(RefreshTokenModel)
            .filter(RefreshTokenModel.token == jti)
            .first()
        )
        if row is None:
            return None
        return self._to_record(row)

    def create(self, user_id: int, jti: str, expires_at: datetime) -> RefreshTokenRecord:
        row = RefreshTokenModel(user_id=user_id, token=jti, expires_at=expires_at)
        self._db.add(row)
        self._db.flush()
        return self._to_record(row)

    def revoke(self, jti: str) -> bool:
        row = (
            self._db.query(RefreshTokenModel)
            .filter(RefreshTokenModel.token == jti)
            .first()
        )
        if row is None or row.revoked_at is not None:
            return False
        row.revoked_at = datetime.utcnow()
        return True

    @staticmethod
    def _to_record(row: RefreshTokenModel) -> RefreshTokenRecord:
        return RefreshTokenRecord(
            id=row.id,
            user_id=row.user_id,
            token=row.token,
            expires_at=row.expires_at,
            revoked_at=row.revoked_at,
        )

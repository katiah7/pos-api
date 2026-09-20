from typing import Generic, TypeVar

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int):
        return db.get(self.model, id)

    def get_all(self, db: Session):
        return db.query(self.model).all()

    def create(self, db: Session, data: dict):
        db_obj = self.model(**data)
        db.add(db_obj)
        self._commit(db)
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, data: dict):
        for field, value in data.items():
            setattr(db_obj, field, value)
        self._commit(db)
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: ModelType):
        db.delete(db_obj)
        self._commit(db)

    @staticmethod
    def _commit(db: Session):
        try:
            db.commit()
        except IntegrityError:
            db.rollback()  
            raise

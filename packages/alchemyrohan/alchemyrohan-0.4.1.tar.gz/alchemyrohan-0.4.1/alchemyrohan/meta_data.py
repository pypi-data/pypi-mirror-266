

__all__ = ['MetaDataHolder']


from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine


class MetaDataHolder:
    def __init__(self, engine: Engine, table: str) -> None:
        self.name = table
        self.rdbms = engine.name

        inspector = inspect(engine)
        self.schema = inspector.default_schema_name
        self.columns = self._get_columns(inspector, table)
        self.primary_key = self._get_primary_key(inspector, table)
        self.foreign_keys = self._get_foreign_keys(inspector, table)
        self.multi_foreign_keys = self._get_multi_foreign_keys(inspector)
        self.unique_keys = self._get_unique_cons(inspector, table)

    @staticmethod
    def _get_columns(inspector, table):
        try:
            return inspector.get_columns(table)
        except SQLAlchemyError as e:
            raise SQLAlchemyError(e) from e

    @staticmethod
    def _get_primary_key(inspector, table):
        try:
            return inspector.get_pk_constraint(table)
        except SQLAlchemyError as e:
            raise SQLAlchemyError(e) from e
    
    @staticmethod
    def _get_foreign_keys(inspector, table):
        try:
            return inspector.get_foreign_keys(table)
        except SQLAlchemyError as e:
            raise SQLAlchemyError(e) from e
    
    @staticmethod
    def _get_multi_foreign_keys(inspector):
        try:
            return inspector.get_multi_foreign_keys()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(e) from e

    @staticmethod
    def _get_unique_cons(inspector, table):
        try:
            return inspector.get_unique_constraints(table)
        except SQLAlchemyError as e:
            raise SQLAlchemyError(e) from e

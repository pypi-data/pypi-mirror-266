

__all__ = ['get_model', 'str_print']


import importlib

from typing import Optional
from typing import TypeVar
from sqlalchemy.orm import declarative_base

from alchemyrohan.meta_data import MetaDataHolder


T = TypeVar('T', bound=declarative_base)


def str_print(code_holder: dict, table_meta_data: MetaDataHolder) -> None:

    tmp = []
    a = "f'User("
    for c in table_meta_data.columns:
        tmp.append(f"{c['name']}={{self.{c['name']}}}")
    b = ",'\\\n\t\t\tf'".join(tmp)
    c = ")'"
    d = a + b + c
    txt = f"""
        return {d}
"""
    
    code_holder.update({'str_print': txt})


def get_model(table_name: str, py_path_to_model: str) -> Optional[T]:
    """
    Retrieves the desired database object of the SqlAlchemy model

    Args:
        table_name (str): Name of the database table.
        py_path_to_model (str): Pythonic path to the models in 
            the project.

    Returns:
        Union[Type[DeclarativeMeta], None]: A SQLAlchemy model 
            class if found, or None if not found.
            
    """

    module = importlib.import_module(
        f'{py_path_to_model}.{table_name.capitalize()}')
    
    if hasattr(module, table_name.capitalize()):
        return getattr(module, table_name.capitalize())
    else:
        return None

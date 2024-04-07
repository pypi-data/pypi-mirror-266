

__all__ = [
    'generate_model',
    'generate_code',
    'generate_init_file',
    'construct_model'
    ]

import os

from sqlalchemy.exc import SQLAlchemyError
from alchemyrohan.meta_data import MetaDataHolder

std_imports = ['from sqlalchemy import Column']


def _write_template(file: str, mode: str, template: str) -> None:
    with open(file, mode) as f:
        f.write(template)
        f.close()


def generate_model(
        filename: str, model_template: str, path: str) -> None:
    if os.path.isdir(path):
        file = os.path.join(path, filename.capitalize() + '.py')
    else:
        raise SQLAlchemyError(f'No path: {path}')
    
    try:
        _write_template(file, 'w', model_template)
    except SQLAlchemyError as e:
        raise SQLAlchemyError(e) from e


def generate_code(
        table_meta_data: MetaDataHolder, py_path_to_model: str) -> dict:

    imp = f'from {py_path_to_model} import Base'
    if imp not in std_imports:
        std_imports.append(f'from {py_path_to_model} import Base')

    code_holder = {
        'name': table_meta_data.name,
        'py_path_to_model': py_path_to_model,
        'imports': std_imports,
        'class_name': f'class {table_meta_data.name.capitalize()}(Base):',
        'table_name': f"__tablename__ = '{table_meta_data.name}'",
    }    
    
    if table_meta_data.rdbms == 'sqlite':
        
        from alchemyrohan.sqlite import read_sqlite_and_build_code

        read_sqlite_and_build_code(code_holder, table_meta_data)

    elif table_meta_data.rdbms == 'mysql':  
        ...
        # TODO

    elif table_meta_data.rdbms == 'oracle':  
        
        from alchemyrohan.oracle import read_oracle_and_build_code

        read_oracle_and_build_code(code_holder, table_meta_data)
    
    else:
        raise SQLAlchemyError(
            f'No supported dialect: {table_meta_data.rdbms}')

    return code_holder


def construct_model(code_holder: dict) -> str:

    def _add(tmp_list: list) -> str:
        for e in tmp_list:
            yield e

    backslash = '\n'

    template = f"""

{f'{backslash}'.join(_add(code_holder['imports']))}


{code_holder['class_name']}
    {code_holder['table_name']}

{''.join(_add(code_holder['columns']))}

{''.join(_add(code_holder['relations']))}

    def validate(self):
{''.join(code_holder['validations'])}
    
    def __str__(self):
{code_holder['str_print']}
"""
    
    return template


def generate_init_file(table_name: str, path: str, py_path: str) -> None:

    file = os.path.join(path, '__init__.py')

    if os.path.isfile(file):
        model_name = table_name.capitalize()
        template = f'\nfrom {py_path}.{model_name} import {model_name}'

        _write_template(file, 'a', template)
    else:
        model_name = table_name.capitalize()

        template = f"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()

from {py_path}.{model_name} import {model_name}
"""
        
        _write_template(file, 'w', template)

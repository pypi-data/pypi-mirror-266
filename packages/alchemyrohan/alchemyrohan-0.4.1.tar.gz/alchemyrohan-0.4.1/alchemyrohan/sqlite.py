

__all__ = ['read_sqlite_and_build_code']


from typing import Any
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.dialects.sqlite import INTEGER
from sqlalchemy.dialects.sqlite import REAL
from sqlalchemy.dialects.sqlite import BLOB

from alchemyrohan.meta_data import MetaDataHolder
from alchemyrohan.utils import str_print


dialect_imports = []


def _get_default(typ: str) -> Any:
    if typ == 'TEXT':
        return "' '"
    elif typ == 'INTEGER':
        return 0
    elif typ == 'REAL':
        return 0.0
    elif typ == 'BLOB':
        return b"' '"


def _get_type(typ: Any) -> str:
    if isinstance(typ, TEXT):
        return 'TEXT'
    elif isinstance(typ, INTEGER):
        return 'INTEGER'
    elif isinstance(typ, REAL):
        return 'REAL'
    elif isinstance(typ, BLOB):
        return 'BLOB'
    

def _get_validation(typ: str, col: str) -> str:
    
    tmp: str = ''
    if typ == 'TEXT':
        tmp = f"""
        if self.{col} and not isinstance(self.{col}, str):
            try:
                self.{col} = str(self.{col})
            except:
                raise SyntaxError(f'< {{self.{col}}} > is not string')
        """

    elif typ == 'INTEGER':
        tmp = f"""
        if self.{col} and not isinstance(self.{col}, int):
            try:
                self.{col} = int(self.{col})
            except:
                raise SyntaxError(f'< {{self.{col}}} > is not integer')
        """

    elif typ == 'REAL':
        tmp = f"""
        if self.{col} and not isinstance(self.{col}, float):
            try:
                self.{col} = float(self.{col})
            except:
                raise SyntaxError(f'< {{self.{col}}} > is not float')
        """

    elif typ == 'BLOB':
        tmp = f"""
        if self.{col} and not isinstance(self.{col}, bytes):
            try:
                self.{col} = int(self.{col})
            except:
                raise SyntaxError(f'< {{self.{col}}} > is not bytes')
        """

    return tmp


def _validations(code_holder: dict, table_meta_data: MetaDataHolder) -> None:

    col = []
    for c in table_meta_data.columns:
        col.append(
            _get_validation(_get_type(c['type']), c['name']))

    code_holder.update({'validations': col})


def _columns(code_holder: dict, table_meta_data: MetaDataHolder) -> None:
    
    col = []
    for c in table_meta_data.columns:
        
        tmp = f"{c['name']} = Column("
        tmp = ''.join([tmp, _get_type(c['type'])])
        imp = f"from sqlalchemy.dialects.sqlite import {_get_type(c['type'])}"
        if imp not in dialect_imports:
            dialect_imports.append(imp)

        if c['primary_key'] == 1:
            tmp = ', '.join([tmp, 'primary_key=True'])
        else:

            for f in table_meta_data.foreign_keys:
                for fk in f['constrained_columns']:
                    if fk == c['name'] and f['referred_columns']:
                        ref_col = f['referred_columns'][0]
                        ref_table = f['referred_table'].lower()
                        tmp = ', '.join(
                            [tmp, f"ForeignKey('{ref_table}.{ref_col}')"])
                        code_holder['imports'].append(
                            'from sqlalchemy import ForeignKey')
                        break

            if c['nullable']:
                tmp = ', '.join([tmp, 'nullable=True', 'default=None'])
            else:
                if c['default']:
                    tmp = ', '.join([
                        tmp, 'nullable=False', f"default={c['default']}"]
                        )
                else:
                    tmp = ', '.join([
                        tmp, 
                        'nullable=False', 
                        f"default={_get_default(_get_type(c['type']))}"
                        ]
                        )         

            for u in table_meta_data.unique_keys:
                for e in u['column_names']:
                    if c['name'] == e:
                        tmp = ', '.join([tmp, 'unique=True'])
                        break

        tmp = ''.join([tmp, ')'])

        tmp = f"""
    {tmp}"""
        
        col.append(tmp)
       
    code_holder.update({'columns': col})


def _relations(
        code_holder: dict, table_meta_data: MetaDataHolder) -> None:

    rel = []
    for f in table_meta_data.foreign_keys:
        referred_table = f['referred_table']

        tmp = f'parent_{referred_table.capitalize()}'\
            f' = relationship("{referred_table.capitalize()}",'\
            f' back_populates="children_{table_meta_data.name.capitalize()}",'\
            ' lazy="joined")'
        
        tmp = f"""
    {tmp}""" 
        
        rel.append(tmp)

    for k, v in table_meta_data.multi_foreign_keys.items():
        if k[1] == table_meta_data.name and not v:
            for child_table, r in table_meta_data.multi_foreign_keys.items():
                if r:
                    for rt in r:
                        if rt['referred_table'] == table_meta_data.name \
                        or rt['referred_table'] == table_meta_data.name.capitalize():
                            tmp = f'children_{child_table[1].capitalize()}'\
                            f' = relationship("{child_table[1].capitalize()}",'\
                            f' back_populates="parent_{table_meta_data.name.capitalize()}",'\
                            ' lazy="joined")'
        
                            tmp = f"""
    {tmp}""" 

                            rel.append(tmp)

            break
                    
    if rel:
        imp = 'from sqlalchemy.orm import relationship'
        if imp not in dialect_imports:
            dialect_imports.append(imp)

    code_holder.update(
        {'imports': code_holder['imports'] + dialect_imports}
        )
    code_holder.update({'relations': rel})


def read_sqlite_and_build_code(
        code_holder: dict, table_meta_data: MetaDataHolder) -> None:

    _columns(code_holder, table_meta_data)
    _relations(code_holder, table_meta_data)
    _validations(code_holder, table_meta_data)
    str_print(code_holder, table_meta_data)

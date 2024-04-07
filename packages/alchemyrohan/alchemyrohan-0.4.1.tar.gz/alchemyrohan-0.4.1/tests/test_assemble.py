

import sys
import os
import unittest


sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests'))

from sqlalchemy.exc import SQLAlchemyError
from alchemyrohan.assemble import assemble_models


class TestAssemble(unittest.TestCase):

    def test_assemble_model_sqlite_db(self):

        path = os.path.dirname(__file__)
        conn_str = f"sqlite:///{path}{os.sep}test_sqlite{os.sep}test.db"
        path = os.path.join(path, 'test_models')
        py_path = 'tests.test_models'

        table_names = ['parent', 'child']

        try:
            assemble_models(conn_str, table_names, path,py_path)
        except SQLAlchemyError as e:
            self.fail(
                f"Sqlite - Function raised an unexpected exception: {e}")


if __name__ == '__main__':
    unittest.main()

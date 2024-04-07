

import sys
import os
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy.exc import SQLAlchemyError
from alchemyrohan.assemble import assemble_models


class TestAssembleError(unittest.TestCase):

    @unittest.expectedFailure
    def test_assemble_model_with_error(self):

        path = '/workspace/projects/bubu/'
        conn_str = f"sqlite:///{path}{os.sep}test_sqlite{os.sep}test.db"
        path = os.path.join(path, 'test_models')
        print(path)
        py_path = 'error.path'

        table_names = ['parent', 'child']

        assemble_models(conn_str, table_names, path, py_path)

        with self.assertRaises(SQLAlchemyError):
            raise SQLAlchemyError("This is an expected error")


if __name__ == '__main__':
    unittest.main()

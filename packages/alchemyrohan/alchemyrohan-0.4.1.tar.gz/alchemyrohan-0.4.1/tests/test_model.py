

import sys
import os
import unittest

sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests'))


from alchemyrohan import get_model
from tests.test_models.Parent import Parent
from tests.test_models.Child import Child


class TestModels(unittest.TestCase):

    def test_get_models(self):

        py_path = 'tests.test_models'
        test_cases = [('parent', Parent), ('child', Child)]

        for table_name, expected_result in test_cases:
            result = get_model(table_name, py_path)
            self.assertEqual(result, expected_result)

    def test_validation(self):

        parent = Parent(id=1, name='alice', age=23)

        parent.validate()


if __name__ == '__main__':
    unittest.main()











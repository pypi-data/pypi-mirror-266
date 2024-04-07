
from sqlalchemy.orm import declarative_base

Base = declarative_base()

from tests.test_models.Parent import Parent
from tests.test_models.Child import Child

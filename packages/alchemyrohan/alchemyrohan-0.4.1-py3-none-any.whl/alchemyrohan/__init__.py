

"""

Alchemyrohan is a tool for SqlAlchemy that helps to create 
database models based on the database schema.

More in < README.md > file.

"""

__title__ = 'alchemyrohan'
__summary__ = 'Tool to create database models'
__url__ = 'https://github.com/wamberger/alchemyrohan'

__version__ = '0.4.0'

__author__ = 'Alan Wamberger'
__email__ = 'awamberger@proton.me'

__license__ = 'MIT'
__copyright__ = '2023 %s' % __author__


from alchemyrohan.assemble import assemble_models
from alchemyrohan.utils import get_model

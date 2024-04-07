


# Alchemyrohan

 ![pypi v23.x](https://img.shields.io/badge/pypi-v23.x-yellow) ![Python 3.12](https://img.shields.io/badge/python-3.12-blue) ![SqlAlchemy](https://img.shields.io/badge/SqlAlchemy-2.0-red)


Alchemyrohan is a helpful tool for creating **[SqlAlchemy](https://www.sqlalchemy.org/)** models 
based on the database schema.

---

## 📖 Content

- [How to Install](#-How-to-Install)
- [Database Support](#-Database-Support)
- [How to use](#-How-to-use)
  - [In Command-Line](#-In-Command-Line)
  - [As Script](#-As-Script)
    - [Functions](#-Functions)
      - [Main Function](#-Main-Function)
      - [Optional Function](#-Optional-Function)
- [Models](#-Models)
- [Dependencies](#-Dependencies)
- [Important Note](#Important-Note)
- [Release Notes](#-Release-Notes)
- [License](#-License-and-Third-Party-Licenses)

---


## 🔧 How to Install

With pip package installer from **[PyPI](https://pypi.org/project/pip/)** directly:

```
pip install alchemyrohan
```

or from source:

```
pip install pdm
git clone https://github.com/wamberger/alchemyrohan.git
pdm install
```


## 🗄 Database Support

This project is currently designed to work with the following databases:

- **SqLite**
- **Oracle**


## 🔨 How to use

### ⌨️ In Command-Line

You can execute the tool by entering the following command along with its arguments:

> arohan -c sqlite:///path/to/database/test.db -y tests.test_models -p /path/to/save/models/ -m table1 table2 table3

Arguments:

        -c, --conn_str:
            Connection string to connect with the database.
            Required argument. Accepts a string.

        -p, --path:
            Path where to save the models.
            Optional argument. Defaults to the current working directory.
            Accepts a string.

        -y, --py_path:
            Pythonic path to models in the project.
            Optional argument. Defaults to 'py_path'.
            Accepts a string.

        -m, --models:
            Names of the database tables.
            Required argument. Accepts one or more strings.

        --verbose:
            Enables verbose mode.
            Optional argument. Activates verbose mode if provided.
            Does not require any additional argument value.


### 💻 As Script 

You can find an example script in the directory *help_file/*.

#### 🪄 Functions

##### 🔮 Main Function

**assemble_models()** is the main function. This function is used to create a 
SqlAlchemy database model and is accepting the following arguments:
 
| argument      | description |
|---------------| --------- |
| *conn_str*    | Credential string to connect to the database |
| *table_names* | Names of the tables |
| *path*        | Absolute path to the location where the created models will be saved |
| *py_path*     | pythonic path to the models |

**Simple example how to use the function *assemble_models()*:**

~~~python


import os

from sqlalchemy.exc import SQLAlchemyError
from alchemyrohan import assemble_models


def main():

    path = os.path.dirname(__file__)

    # Sqlite example
    conn_str = f"sqlite:///{path}{os.sep}test_sqlite{os.sep}test.db"
    # Oracle-Database example
    # db_creds = f'oracle+oracledb://{username}:{password}@{hostname}:{port}/{service_name}'

    path = os.path.join(path, 'test_models') # path to save models
    py_path = 'tests.test_models' # pythonic path to models

    table_names = ['parent', 'child'] # all names will be capitilized

    try:
        assemble_models(conn_str, table_names, path,py_path)
    except SQLAlchemyError as e:
        raise SQLAlchemyError(e) from e


if __name__ == '__main__':
    main()


~~~

##### 💉 Optional Function

**get_model():** It retrieves the desired database object of the SqlAlchemy model. It requires the *table_name* and *py_path_to_model* arguments.

~~~python

from alchemyrohan import get_model

~~~

## 🗂 Models

Created SqlAlchemy models have some additional features:

- Default values.
- Parent-child relationships.
- The *validate* method is used for validation.
- When 'printing', the string will contain the model/object name and attribute names with their values.

All models are named with the same convention as they are in the database, with one difference: they are capitalized according to Python class naming conventions.


**Example of one created model**:

~~~python


from sqlalchemy import Column
from tests.test_models import Base
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.sqlite import INTEGER
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.orm import relationship


class Child(Base):
    __tablename__ = 'child'


    id = Column(INTEGER, primary_key=True)
    parent_id = Column(INTEGER, ForeignKey('parent.id'), nullable=True, default=None)
    name = Column(TEXT, nullable=True, default=None)
    grade = Column(INTEGER, nullable=True, default=None)


    parent_Parent = relationship("Parent", back_populates="children_Child", lazy="joined")

    def validate(self):

        if self.id and not isinstance(self.id, int):
            try:
                self.id = int(self.id)
            except:
                raise SyntaxError(f'< {self.id} > is not integer')
        
        if self.parent_id and not isinstance(self.parent_id, int):
            try:
                self.parent_id = int(self.parent_id)
            except:
                raise SyntaxError(f'< {self.parent_id} > is not integer')
        
        if self.name and not isinstance(self.name, str):
            try:
                self.name = str(self.name)
            except:
                raise SyntaxError(f'< {self.name} > is not string')
        
        if self.grade and not isinstance(self.grade, int):
            try:
                self.grade = int(self.grade)
            except:
                raise SyntaxError(f'< {self.grade} > is not integer')
        
    
    def __str__(self):

        return f'User(id={self.id},'\
			f'parent_id={self.parent_id},'\
			f'name={self.name},'\
			f'grade={self.grade})'


~~~ 


## 📚 Dependencies

- **sqlalchemy** (version 2.x.x) is an ORM and provides code for its models.
- **oracledb** (version 2.x.x) is used to shape a database table model with an Oracle table schema.


## ❗Important Note

You should always check the code and correct it manually if necessary. 
This may be necessary in cases when:

- You add the wrong path.

- You are creating only one model which has relationships to other tables, 
 thus you will need to create those models or delete the relevant part of the code.

- Your tables have no primary keys. SQLAlchemy requires at least one primary key.

- Your database may have some data types or features which have not yet been tested - Please report!


## 📋 Release Notes

- ***v0.4.1*** - Some vital changes! Please look at CHANGELOG.md. In short:
  - New command-line: *arohan*.
  - Removed functions: *is_model()*, *reload_module()*, *is_module()*.
  - Changing parameter names in the function *assemble_models()*.
  - Bug fixing (*relationship*).
  - In models, method *validate*.

- ***v0.4.0*** - Main update! Not compatible with previous versions. Changes:
  - Changed function name from *assemble_model()* to *assemble_models()*.
  - Updated parameters of the *assemble_models()* function.
  - Revised code structure of the *assemble_models()* function.
  - Adjusted naming or added text in *utils.py*, *wizard.py* and *__init__py*.
  - Updated README.md file.
- ***v0.3.2*** - text fixing and adding third party licenses
- ***v0.3.1*** - bug fixing
- ***v0.3.0*** - added additional functions
- ***v0.2.0*** - tested with Oracle database
- ***v0.1.0*** - creation of the initial code and tested with SqLite database


## 📄 License and Third-Party Licenses

Alchemyrohan is MIT licensed, as stated in the [LICENSE][1] file.

The following software components are included in this project:

* SqlAlchemy (MIT License)
* python-oracledb (Apache License 2.0) 

[THIRD PARTY LICENSES][2]


[1]: https://github.com/wamberger/alchemyrohan/blob/master/LICENSE
[2]: https://github.com/wamberger/alchemyrohan/blob/master/THIRD_PARTY_LICENSES
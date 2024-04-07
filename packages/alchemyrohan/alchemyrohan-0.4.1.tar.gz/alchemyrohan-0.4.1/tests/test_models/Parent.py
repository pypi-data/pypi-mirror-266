

from sqlalchemy import Column
from tests.test_models import Base
from sqlalchemy.dialects.sqlite import INTEGER
from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy.dialects.sqlite import REAL
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.orm import relationship


class Parent(Base):
    __tablename__ = 'parent'


    id = Column(INTEGER, primary_key=True)
    name = Column(TEXT, nullable=True, default=None)
    age = Column(INTEGER, nullable=True, default=None)
    height = Column(REAL, nullable=True, default=None)
    is_active = Column(BLOB, nullable=True, default=None)


    children_Child = relationship("Child", back_populates="parent_Parent", lazy="joined")

    def validate(self):

        if self.id and not isinstance(self.id, int):
            try:
                self.id = int(self.id)
            except:
                raise SyntaxError(f'< {self.id} > is not integer')
        
        if self.name and not isinstance(self.name, str):
            try:
                self.name = str(self.name)
            except:
                raise SyntaxError(f'< {self.name} > is not string')
        
        if self.age and not isinstance(self.age, int):
            try:
                self.age = int(self.age)
            except:
                raise SyntaxError(f'< {self.age} > is not integer')
        
        if self.height and not isinstance(self.height, float):
            try:
                self.height = float(self.height)
            except:
                raise SyntaxError(f'< {self.height} > is not float')
        
        if self.is_active and not isinstance(self.is_active, bytes):
            try:
                self.is_active = int(self.is_active)
            except:
                raise SyntaxError(f'< {self.is_active} > is not bytes')
        
    
    def __str__(self):

        return f'User(id={self.id},'\
			f'name={self.name},'\
			f'age={self.age},'\
			f'height={self.height},'\
			f'is_active={self.is_active})'


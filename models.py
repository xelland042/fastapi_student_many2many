from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine('sqlite:///./database.sqlite3', connect_args={'check_same_thread': False}, echo=True)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime, default=func.now())
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now())


class Student(BaseModel):
    __tablename__ = 'students'

    first_name = Column(String, default=None, nullable=True)
    last_name = Column(String, default=None, nullable=True)
    age = Column(Integer)
    subjects = relationship('Subject', secondary='students_subjects', back_populates='students')

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __repr__(self):
        return f'{self.id} - {self.full_name()}'


class Subject(BaseModel):
    __tablename__ = 'subjects'
    name = Column(String)
    students = relationship('Student', secondary='students_subjects', back_populates='subjects')

    def __repr__(self):
        return f'{self.id} - {self.name}'


class StudentSubject(Base):
    __tablename__ = 'students_subjects'

    student = Column('student_id', ForeignKey('students.id'), primary_key=True)
    subject = Column('subject_id', ForeignKey('subjects.id'), primary_key=True)
    created_on = Column(DateTime, default=func.now())
    updated_on = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'{self.student} - {self.subject}'


class User(BaseModel):
    __tablename__ = 'user'

    username = Column(String, unique=True)
    first_name = Column(String, default=None, nullable=True)
    last_name = Column(String, default=None, nullable=True)
    email = Column(String, unique=True)
    hashed_password = Column(String, default=None, nullable=True)

    def __repr__(self):
        return f'{self.id} - {self.username}'

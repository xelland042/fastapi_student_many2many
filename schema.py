from pydantic import BaseModel
from typing import List


class StudentBase(BaseModel):
    id: int
    first_name: str
    last_name: str
    age: int

    class Config:
        orm_mode = True


class SubjectBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class IdScheme(BaseModel):
    id: int


class Student(BaseModel):
    first_name: str
    last_name: str
    age: int


class StudentSchema(StudentBase):
    subjects: List[SubjectBase]


class SubjectSchema(SubjectBase):
    students: List[StudentSchema]


class CreateStudent(BaseModel):
    first_name: str
    last_name: str
    age: int
    subjects: List[IdScheme]

    class Config:
        orm_mode = True


class CreateSubject(BaseModel):
    name: str
    students: List[IdScheme]

    class Config:
        orm_mode = True

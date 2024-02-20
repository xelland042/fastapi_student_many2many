from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from schema import StudentSchema, SubjectSchema, CreateStudent, CreateSubject

from models import get_db, Student, Subject, StudentSubject, Base, engine
import users

app = FastAPI(
    title='Student Subject API',
    docs_url='/',
)

app.include_router(users.router)

Base.metadata.create_all(engine)


@app.get('/students/', response_model=List[StudentSchema], tags=['Students and Subjects List'])
async def list_students(db: Session = Depends(get_db)):
    students = db.query(Student).options(joinedload(Student.subjects)).all()
    return students


@app.get('/subjects/', response_model=List[SubjectSchema], tags=['Students and Subjects List'])
async def list_subjects(db: Session = Depends(get_db)):
    subjects = db.query(Subject).options(joinedload(Subject.students)).all()
    return subjects


@app.get('/students/{student_id}/', response_model=StudentSchema, tags=['Students and Subjects Details'])
async def student_detail(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).options(joinedload(Student.subjects)).where(Student.id == student_id).one()
    return student


@app.get('/subjects/{subject_id}/', response_model=StudentSchema, tags=['Students and Subjects Details'])
async def subject_detail(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).options(joinedload(Subject.students)).where(Subject.id == subject_id).one()
    return subject


@app.post('/students/', tags=['Students and Subjects Create'])
async def crete_student(student: CreateStudent, db: Session = Depends(get_db)):
    subjects = []
    for i in student.subjects:
        subjects.append(db.query(Subject).filter(Subject.id == i.id).first())
    print(subjects)
    new_student = Student(first_name=student.first_name, last_name=student.last_name, age=student.age,
                          subjects=subjects)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


@app.post('/subjects/', tags=['Students and Subjects Create'])
async def crete_subject(subject: CreateSubject, db: Session = Depends(get_db)):
    students = []
    for i in subject.students:
        students.append(db.query(Student).filter(Student.id == i.id).first())
    print(students)
    new_subject = Subject(name=subject.name, students=students)
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return new_subject


@app.patch('/students/{student_id}/', response_model=StudentSchema, tags=['Students and Subjects Update'])
async def update_student(updated_student: CreateStudent, student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).get(student_id)
    new_subjects = []
    if student:
        if updated_student.subjects:
            for i in updated_student.subjects:
                new_subjects.append(db.query(Subject).filter(Subject.id == i.id).first())
        student.first_name = updated_student.first_name
        student.last_name = updated_student.last_name
        student.age = updated_student.age
        student.subjects = new_subjects
        db.commit()
        db.refresh(student)
        return student
    raise HTTPException(detail='No such student!', status_code=status.HTTP_400_BAD_REQUEST)


@app.patch('/subjects/{subject_id}/', response_model=StudentSchema, tags=['Students and Subjects Update'])
async def update_subject(updated_subject: CreateSubject, subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).get(subject_id)
    new_students = []
    if subject:
        if updated_subject.students:
            for i in updated_subject.students:
                new_students.append(db.query(Student).filter(Student.id == i.id).first())
        subject.name = updated_subject.name
        subject.students = new_students
        db.commit()
        db.refresh(subject)
        return subject
    raise HTTPException(detail='No such subject!', status_code=status.HTTP_400_BAD_REQUEST)


@app.delete('/students/{student_id}/', response_model=StudentSchema, tags=['Students and Subjects Delete'])
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).get(student_id)
    if student:
        db.delete(student)
        db.commit()
        return {"message": "Student deleted successfully"}
    raise HTTPException(status_code=404, detail='Student not found!')


@app.delete('/subjects/{subject_id}/', response_model=StudentSchema, tags=['Students and Subjects Delete'])
async def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).get(subject_id)
    if subject:
        db.delete(subject)
        db.commit()
        return {"message": "Subject deleted successfully"}
    raise HTTPException(status_code=404, detail='Subject not found!')

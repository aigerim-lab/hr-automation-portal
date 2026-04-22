from fastapi import FastAPI, Depends

from fastapi.templating import Jinja2Templates
from fastapi import Request

from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app import models
from app.models import Employee

from pydantic import BaseModel
# ВАЖНО: сначала создаём app
app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

# создаём таблицы
Base.metadata.create_all(bind=engine)

class EmployeeCreate(BaseModel):
    full_name: str
    department: str
    position: str


@app.get("/")
def home():
    return {"message": "HR Automation Portal is running"}


@app.post("/employees")
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db)
):
    new_employee = Employee(
        full_name=employee.full_name,
        department=employee.department,
        position=employee.position
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_employee

@app.get("/employees")
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

@app.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    employees = db.query(Employee).all()

    return templates.TemplateResponse(
        request=request,               # Передаём request как именованный аргумент
        name="dashboard.html",          # Явно указываем имя шаблона
        context={"employees": employees} # Весь ваш набор данных кладём в context
    )
from fastapi import FastAPI, Depends, Request, UploadFile, File, HTTPException
from pathlib import Path

from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi import Request

from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app import models
from app.models import Employee, Document
from app.services.pdf_parser import extract_text_from_pdf

from pydantic import BaseModel
# ВАЖНО: сначала создаём app
app = FastAPI()
UPLOAD_DIR = Path("app/services")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


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
        context={
        "request": request,
        "employees": employees
    } # Весь ваш набор данных кладём в context
    )

@app.post("/employees/{employee_id}/upload-pdf")
async def upload_pdf(
    employee_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    extracted_text = extract_text_from_pdf(file_path)

    document = Document(
        employee_id=employee.id,
        filename=file.filename,
        extracted_text=extracted_text
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "message": "PDF uploaded successfully",
        "document_id": document.id,
        "filename": document.filename,
        "extracted_text_preview": extracted_text[:500]
    }

@app.get("/employees/{employee_id}")
def employee_detail(
    employee_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return templates.TemplateResponse(
        request=request,
        name="employee_detail.html",
        context={
            "request": request,
            "employee": employee
        }
    )


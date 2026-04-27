from fastapi import FastAPI, Depends, Request, UploadFile, File, HTTPException, Form

from fastapi.staticfiles import StaticFiles

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

from app.models import WorkExperience
# ВАЖНО: сначала создаём app
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

UPLOAD_DIR = Path("app/uploads")
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
def dashboard(
    request: Request,
    search: str = "",
    department: str = "",
    position: str = "",
    db: Session = Depends(get_db)
):
    query = db.query(Employee)

    if search:
        query = query.filter(Employee.full_name.ilike(f"%{search}%"))

    if department:
        query = query.filter(Employee.department.ilike(f"%{department}%"))

    if position:
        query = query.filter(Employee.position.ilike(f"%{position}%"))

    employees = query.all()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "employees": employees,
            "search": search,
            "department": department,
            "position": position
        }
    )




@app.get("/employees/new")
def new_employee_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="employee_form.html",
        context={"request": request}
    )

@app.post("/employees/new")
def create_employee_from_form(
    full_name: str = Form(...),
    department: str = Form(...),
    position: str = Form(...),
    experience_summary: str = Form(""),
    db: Session = Depends(get_db)
):
    new_employee = Employee(
        full_name=full_name,
        department=department,
        position=position,
        experience_summary=experience_summary
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )



@app.get("/employees/{employee_id}/edit")
def edit_employee_form(
    employee_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return templates.TemplateResponse(
        request=request,
        name="employee_edit.html",
        context={
            "request": request,
            "employee": employee
        }
    )


@app.post("/employees/{employee_id}/edit")
def update_employee(
    employee_id: int,
    full_name: str = Form(...),
    department: str = Form(...),
    position: str = Form(...),
    experience_summary: str = Form(""),
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee.full_name = full_name
    employee.department = department
    employee.position = position
    employee.experience_summary = experience_summary

    db.commit()

    return RedirectResponse(
        url=f"/employees/{employee_id}",
        status_code=303
    )


@app.post("/employees/{employee_id}/delete")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(employee)
    db.commit()

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )

@app.post("/employees/{employee_id}/experience")
def add_experience(
    employee_id: int,
    organization: str = Form(...),
    job_title: str = Form(...),
    city: str = Form(""),
    period: str = Form(""),
    bin: str = Form(""),
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    exp = WorkExperience(
        employee_id=employee_id,
        organization=organization,
        job_title=job_title,
        city=city,
        period=period,
        bin=bin
    )

    db.add(exp)
    db.commit()

    return RedirectResponse(
        url=f"/employees/{employee_id}",
        status_code=303
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

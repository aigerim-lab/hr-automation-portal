from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


# ------------------------
# EMPLOYEE TABLE
# ------------------------
class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    department = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    experience_summary = Column(Text, nullable=True)

    # relationships
    experiences = relationship(
        "WorkExperience",
        back_populates="employee",
        cascade="all, delete-orphan"
    )

    documents = relationship(
        "Document",
        back_populates="employee",
        cascade="all, delete-orphan"
    )


# ------------------------
# WORK EXPERIENCE TABLE
# ------------------------
class WorkExperience(Base):
    __tablename__ = "work_experiences"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    organization = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    years = Column(String(100), nullable=True)

    # relationship back
    employee = relationship("Employee", back_populates="experiences")


# ------------------------
# DOCUMENT TABLE
# ------------------------
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    filename = Column(String(255), nullable=False)
    extracted_text = Column(Text, nullable=True)

    # relationship back
    employee = relationship("Employee", back_populates="documents")
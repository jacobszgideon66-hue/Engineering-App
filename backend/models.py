from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from database import Base
import datetime
import enum

class MachineType(enum.Enum):
    CONSTRUCTION = "construction"
    MINING = "mining"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    role = Column(String) # 'mechanic', 'manager', 'admin'
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

class Machine(Base):
    __tablename__ = "machines"
    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, unique=True, index=True)
    model = Column(String)
    category = Column(Enum(MachineType))

class InventoryItem(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    part_number = Column(String, unique=True, index=True)
    name = Column(String)
    category = Column(String) # e.g., 'Tool', 'Part', 'Consumable'
    location = Column(String) # Toolstore bin/shelf location
    stock_level = Column(Integer, default=0)
    price = Column(Float)

class Quotation(Base):
    __tablename__ = "quotations"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String)
    total_amount = Column(Float)
    status = Column(String, default="draft")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    quotation_id = Column(Integer, ForeignKey("quotations.id"), unique=True, nullable=False)
    customer_name = Column(String)
    total_amount = Column(Float)
    status = Column(String, default="issued") # e.g., 'issued', 'paid', 'overdue'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    quotation = relationship("Quotation", backref="invoice", uselist=False) # One-to-one relationship

class JobCard(Base):
    __tablename__ = "job_cards"
    id = Column(Integer, primary_key=True, index=True)
    mechanic_id = Column(Integer, ForeignKey("users.id"))
    machine_id = Column(Integer, ForeignKey("machines.id"))
    problem_description = Column(Text)
    work_performed = Column(Text)
    image_report_path = Column(String)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class SafetyDocument(Base):
    __tablename__ = "safety_documents"
    id = Column(Integer, primary_key=True, index=True)
    job_card_id = Column(Integer, ForeignKey("job_cards.id"))
    job_card = relationship("JobCard")
    title = Column(String)
    is_signed = Column(Integer, default=0)
    manager_signature = Column(Text)
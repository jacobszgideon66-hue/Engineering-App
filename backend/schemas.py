from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class InventoryBase(BaseModel):
    part_number: str
    name: str
    category: Optional[str] = "Part"
    location: Optional[str] = None
    stock_level: int = 0
    price: float

class InventoryCreate(InventoryBase):
    pass

class Inventory(InventoryBase):
    id: int
    class Config:
        orm_mode = True

class JobCardCreate(BaseModel):
    machine_id: int
    mechanic_id: int
    problem_description: str

class JobCard(BaseModel):
    id: int
    status: str
    image_report_path: Optional[str] = None # Add this field
    created_at: datetime
    class Config:
        orm_mode = True

class QuotationCreate(BaseModel):
    customer_name: str
    total_amount: float

class Quotation(QuotationCreate):
    id: int
    status: str
    created_at: datetime
    class Config:
        orm_mode = True

class InvoiceBase(BaseModel):
    quotation_id: int

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    id: int
    customer_name: str
    total_amount: float
    status: str
    created_at: datetime
    class Config:
        orm_mode = True

# --- User Authentication Schemas ---
class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    role: str # e.g., 'mechanic', 'manager', 'admin'
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

# --- Safety Document Schemas (existing) ---
# ... (rest of your SafetyDocument schemas remain unchanged)


class SafetyDocumentBase(BaseModel):
    job_card_id: int
    title: str

class SafetyDocumentCreate(SafetyDocumentBase):
    pass

class SafetyDocumentSign(BaseModel):
    signature_data: str # Base64 encoded signature image data

class SafetyDocument(SafetyDocumentBase):
    id: int
    is_signed: int
    manager_signature: Optional[str] = None
    class Config:
        orm_mode = True
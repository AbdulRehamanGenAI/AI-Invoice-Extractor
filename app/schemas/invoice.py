from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class InvoiceCreate(BaseModel):
    invoice_number: str
    vendor_id: int
    invoice_date: date
    due_date: date | None = None
    amount: Decimal = Field(gt=0)
    currency: str = "INR"
    status: str = "PENDING"

class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    vendor_id: int
    invoice_date: date
    due_date: date | None = None
    amount: Decimal
    currency: str
    status: str
    model_config = ConfigDict(from_attributes=True)
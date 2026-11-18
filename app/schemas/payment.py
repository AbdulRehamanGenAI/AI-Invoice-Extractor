from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict,Field

class PaymentCreate(BaseModel):
    invoice_id:int
    payment_date:date
    amount:Decimal=Field(gt=0)
    payment_method:str | None = None
    reference_number:str | None = None
    status:str="COMPLETED"

class PaymentResponse(BaseModel):
    id:int
    invoice_id:int
    payment_date:date
    amount:Decimal
    payment_method:str | None = None
    reference_number:str | None = None
    status:str
    
    model_config=ConfigDict(from_attributes=True)
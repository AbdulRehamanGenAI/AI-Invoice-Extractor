from sqlalchemy import Column,Numeric, Integer,String,Date,ForeignKey,DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class Payment(Base):
    __tablename__="payments"
    id=Column(Integer,primary_key=True,index=True)
    invoice_id=Column(Integer,ForeignKey("invoices.id"),nullable=False)
    payment_date=Column(Date,nullable=False)
    amount=Column(Numeric(12,2),nullable=False)
    reference_number=Column(String(100),unique=True ,nullable=False)
    status=Column(String(100),default="COMPLETED",nullable=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now())

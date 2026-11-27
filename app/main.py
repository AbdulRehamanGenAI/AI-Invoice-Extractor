from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from app.schemas.invoice import InvoiceCreate, InvoiceResponse
from app.db.session import Base, engine, get_db
from app.models.vendor import Vendor
from app.models.invoice import Invoice
from app.models.payment import Payment
from pydantic import BaseModel, Field
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.schemas.vendor import VendorCreate, VendorResponse
from app.models.invoice_embedding import InvoiceEmbedding
from app.services.docx_extractor import extract_text_from_docx
from app.services.ai_invoice_extractor import extract_invoice_fields
from fastapi import UploadFile, File
from app.services.invoice_extractor import extract_pages_from_pdf, extract_text_from_pdf
from app.services.docx_extractor import extract_text_from_docx
from app.services.semantic_search import search_invoice_embeddings
from app.services.rag_service import answer_invoice_question
from app.services.embedding_storage import store_invoice_embedding
from app.services.text_preprocessor import preprocess_text

app = FastAPI(
title="AI Invoice Extractor",
description="AI-powered invoice extraction and finance assistant",
version="0.1.0"
)

# Create database tables

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {
    "message": "Welcome to AI Invoice Extractor!",
    "status": "Application is running"
    }

@app.get("/health")
def health_check():
    return {
    "status": "healthy"
    }

# Create a new vendor

@app.post("/vendors", response_model=VendorResponse, status_code=201)
def create_vendor(
vendor_data: VendorCreate,
db: Session = Depends(get_db)
):
    existing_vendor = db.query(Vendor).filter(
    Vendor.vendor_code == vendor_data.vendor_code
    ).first()

    if existing_vendor:
        raise HTTPException(
            status_code=409,
            detail="Vendor code already exists"
        )

    new_vendor = Vendor(
        vendor_name=vendor_data.vendor_name,
        vendor_code=vendor_data.vendor_code,
        email=str(vendor_data.email) if vendor_data.email else None
    )

    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)

    return new_vendor

# Get all vendors

@app.get("/vendors", response_model=list[VendorResponse])
def get_vendors(db: Session = Depends(get_db)):
    vendors = db.query(Vendor).order_by(Vendor.id).all()
    return vendors

#Get a vendor by ID
@app.get("/vendors/{vendor_id}",response_model=VendorResponse)
def get_vendor(vendor_id: int,db: Session= Depends(get_db)):
    vendor=db.query(Vendor).filter(Vendor.id==vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404,detail="Vendor not found") 
    return vendor

# Create a new invoice

@app.post("/invoices", response_model=InvoiceResponse, status_code=201)
def create_invoice(
invoice_data: InvoiceCreate,
db: Session = Depends(get_db)
):
    existing_invoice = db.query(Invoice).filter(
    Invoice.invoice_number == invoice_data.invoice_number
    ).first()

    if existing_invoice:
        raise HTTPException(
            status_code=409,
            detail="Invoice number already exists"
        )

    vendor = db.query(Vendor).filter(
        Vendor.id == invoice_data.vendor_id
    ).first()

    if vendor is None:
        raise HTTPException(
            status_code=404,
            detail="Vendor not found"
        )

    new_invoice = Invoice(
        invoice_number=invoice_data.invoice_number,
        vendor_id=invoice_data.vendor_id,
        invoice_date=invoice_data.invoice_date,
        due_date=invoice_data.due_date,
        amount=invoice_data.amount,
        currency=invoice_data.currency,
        status=invoice_data.status
    )

    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    return new_invoice
#Get all invoices
@app.get("/invoices", response_model=list[InvoiceResponse])
def get_invoices(db: Session=Depends(get_db)):
    invoice=db.query(Invoice).order_by(Invoice.id).all()
    return invoice

#Get Invoice by ID
@app.get("/invoices/{invoice_id}",response_model=InvoiceResponse)
def get_invoice(invoice_id:int,db:Session=Depends(get_db)):
    invoice=db.query(Invoice).filter(Invoice.id==invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404,detail="Invoice not found")
    return invoice

# Create a new payment
@app.post("/payments",response_model=PaymentResponse,status_code=201)
def create_payment(payment_data:PaymentCreate,db:Session=Depends(get_db)):
    existing_payment=db.query(Payment).filter(Payment.reference_number==payment_data.reference_number).first()
    if existing_payment:
        raise HTTPException(status_code=409,detail="Payment reference number already exists")
    invoice=db.query(Invoice).filter(Invoice.id==payment_data.invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404,detail="Invoice not found")
    
    new_payment=Payment(
        invoice_id=payment_data.invoice_id,
        payment_date=payment_data.payment_date,
        amount=payment_data.amount,
        reference_number=payment_data.reference_number,
        status=payment_data.status
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment

# Get all payments

@app.get("/payments", response_model=list[PaymentResponse])
def get_payments(db: Session = Depends(get_db)):
    payments = db.query(Payment).order_by(Payment.id).all()
    return payments

#Get Invoice Summary by ID
@app.get("/invoices/{invoice_id}/summary")
def get_invoice_summary(invoice_id:int,db:Session=Depends(get_db)):
    invoice=db.query(Invoice).filter(Invoice.id==invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404,detail="Invoice not found")
    payments=db.query(Payment).filter(Payment.invoice_id==invoice_id).all()
    total_paid=sum(payment.amount for payment in payments)
    balance_due=invoice.amount-total_paid
    return {
        "invoice_id":invoice.id,
        "invoice_number":invoice.invoice_number,
        "vendor_id":invoice.vendor_id,
        "invoice_date":invoice.invoice_date,
        "due_date":invoice.due_date,
        "amount":invoice.amount,
        "currency":invoice.currency,
        "status":invoice.status,
        "total_paid":total_paid,
        "balance_due":balance_due
    }

# Upload an invoice PDF and extract its text

@app.post("/invoices/extract-text")
async def extract_invoice_text(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
        status_code=400,
        detail="Please upload a PDF file."
        )
    file_bytes = await file.read()
    try:
        extracted_text = extract_text_from_pdf(file_bytes)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    return {
        "filename": file.filename,
        "extracted_text": extracted_text
    }


@app.post("/invoices/extract")
async def extract_invoice(file: UploadFile = File(...)):
    """
    Upload a PDF invoice and extract structured fields using Gemini AI.
    """

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file."
        )

    file_bytes = await file.read()

    try:
        extracted_text = extract_text_from_pdf(file_bytes)

        invoice_data = extract_invoice_fields(extracted_text)

        return {
            "filename": file.filename,
            "invoice_data": invoice_data
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    finally:
        await file.close()


@app.post("/invoices/extract-and-save")
async def extract_and_save_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Extract invoice details using Gemini AI
    and save the invoice and page-wise embeddings to PostgreSQL.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is missing."
        )
    file_extension = file.filename.lower().rsplit(".", 1)[-1]

    if file_extension not in ["pdf", "docx"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
            )

    file_bytes = await file.read()

    try:
        # Step 1: Extract text based on file format

        if file_extension == "pdf":
            pages = extract_pages_from_pdf(file_bytes)
            cleaned_pages = []
            for page in pages:
                cleaned_pages.append({
                    "page_number": page["page_number"],
                    "text": preprocess_text(page["text"])
                })
        else:
            extracted_text = extract_text_from_docx(file_bytes)
            cleaned_text = preprocess_text(extracted_text)
            cleaned_pages = [{
                "page_number": None,
                "text": cleaned_text
            }]

        # Step 2: Combine text for Gemini extraction
        cleaned_text = "\n\n".join(
            page["text"] for page in cleaned_pages
        )
        # Step 4: Extract invoice fields using Gemini
        invoice_data = extract_invoice_fields(cleaned_text)

        invoice_number = invoice_data.get("invoice_number")
        vendor_name = invoice_data.get("vendor_name")
        invoice_date = invoice_data.get("invoice_date")
        amount = invoice_data.get("amount")
        currency = invoice_data.get("currency") or "INR"
        due_date = invoice_data.get("due_date")

        # Step 5: Validate required fields
        if not all([
            invoice_number,
            vendor_name,
            invoice_date,
            amount
        ]):
            raise HTTPException(
                status_code=400,
                detail="Required invoice fields are missing."
            )

        # Step 6: Check duplicate invoice
        existing_invoice = db.query(Invoice).filter(
            Invoice.invoice_number == invoice_number
        ).first()

        if existing_invoice:
            raise HTTPException(
                status_code=409,
                detail="This invoice number already exists."
            )

        # Step 7: Find vendor
        vendor = db.query(Vendor).filter(
            Vendor.vendor_name.ilike(vendor_name)
        ).first()

        if not vendor:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Vendor '{vendor_name}' was not found. "
                    "Create the vendor first, then upload the invoice again."
                )
            )

        # Step 8: Create invoice record
        invoice = Invoice(
            invoice_number=invoice_number,
            vendor_id=vendor.id,
            invoice_date=invoice_date,
            due_date=due_date,
            amount=amount,
            currency=currency,
            status="PENDING"
        )

        db.add(invoice)
        db.commit()
        db.refresh(invoice)

        # Step 9: Generate and store page-wise embeddings
        embedding_records = store_invoice_embedding(
            db=db,
            invoice_id=invoice.id,
            pages=cleaned_pages
        )

        # Step 10: Return response
        return {
            "message": "Invoice extracted and saved successfully.",
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "vendor_name": vendor.vendor_name,
            "amount": float(invoice.amount),
            "currency": invoice.currency,
            "status": invoice.status,
            "total_chunks_stored": len(embedding_records)
        }

    except HTTPException:
        db.rollback()
        raise

    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except Exception as error:
        db.rollback()
        print("ACTUAL ERROR:", repr(error))
        raise HTTPException(
                status_code=500,
                detail=str(error)
        ) from error
    finally:
        await file.close()


class SemanticSearchRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    limit: int = Field(default=5, ge=1, le=20)


@app.post("/invoices/semantic-search")
def semantic_search_invoices(
    request: SemanticSearchRequest,
    db: Session = Depends(get_db)
):
    try:
        results = search_invoice_embeddings(
            db=db,
            question=request.question,
            limit=request.limit
        )

        return {
            "question": request.question,
            "results_found": len(results),
            "results": results
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


class InvoiceQuestionRequest(BaseModel):
    question: str


@app.post("/invoices/ask")
def ask_invoice_question(
    request: InvoiceQuestionRequest,
    db: Session = Depends(get_db)
):
    return answer_invoice_question(
        db=db,
        question=request.question
    )
    
    
from app.services.invoice_agent import ask_invoice_agent

router = APIRouter()


class AgentQuestion(BaseModel):
    question: str


@app.post("/invoices/agent")
def invoice_agent_endpoint(request: AgentQuestion):

    answer = ask_invoice_agent(request.question)

    return {
        "question": request.question,
        "answer": answer
    }
from pydantic import BaseModel, ConfigDict, EmailStr

class VendorCreate(BaseModel):
    vendor_name: str
    vendor_code: str
    email: EmailStr | None = None

class VendorResponse(BaseModel):
    id: int
    vendor_name: str
    vendor_code: str
    email: str | None = None
    model_config = ConfigDict(from_attributes=True)
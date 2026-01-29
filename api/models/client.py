import re
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


class ClientCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: str
    nip: str
    accountNumber: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if not re.fullmatch(r"\+?\d{9,15}", v):
            raise ValueError("Invalid phone number")
        return v

    @field_validator("nip")
    @classmethod
    def validate_nip(cls, v: str) -> str:
        nip = v.replace("-", "").strip()

        if not nip.isdigit() or len(nip) != 10:
            raise ValueError("NIP must contain exactly 10 digits")

        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(nip[i]) * weights[i] for i in range(9)) % 11

        if checksum == 10 or checksum != int(nip[9]):
            raise ValueError("Invalid NIP checksum")

        return nip


class ClientRead(ClientCreate):
    id: int
    owner_id: int

    model_config = {
        "from_attributes": True
    }


class ClientNIPRequest(BaseModel):
    nip: str


class ClientListResponse(BaseModel): 
    total: int 
    limit: int 
    offset: int 
    items: list[ClientRead]
from datetime import date

from pydantic import BaseModel


class ClientInfo(BaseModel):
    id: int
    name: str
    vat_number: str | None = None
    tax_code: str | None = None
    email: str | None = None
    phone: str | None = None
    address_street: str | None = None
    address_postal_code: str | None = None
    address_city: str | None = None
    address_province: str | None = None


class ClientSearchResponse(BaseModel):
    clients: list[ClientInfo]


class DeclarationRequest(BaseModel):
    client_id: int
    declaration_date: date | None = None
    declaration_number: str | None = None
    notes: str | None = None


class ErrorResponse(BaseModel):
    error: str

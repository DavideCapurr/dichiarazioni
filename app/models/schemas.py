from datetime import date

from pydantic import BaseModel, Field


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


class AllegatiFlags(BaseModel):
    # 3 voci DICHIARA — decide l'utente (default unchecked)
    dichiara_norma: bool = False
    dichiara_componenti: bool = False
    dichiara_controllo: bool = False
    # 6 Allegati obbligatori — sempre pre-checked
    allegato_progetto: bool = True
    allegato_relazione: bool = True
    allegato_schema: bool = True
    allegato_precedenti: bool = True
    allegato_certificato: bool = True
    allegato_conformita: bool = True


class DeclarationRequest(BaseModel):
    client_id: int
    declaration_date: date | None = Field(None)
    tipo_impianto: str | None = Field(None)
    descrizione_impianto: str | None = Field(None)
    comune_installazione: str | None = Field(None)
    via_installazione: str | None = Field(None)
    proprietario: str | None = Field(None)
    uso_edificio: str | None = Field(None)
    allegati: AllegatiFlags = Field(default_factory=AllegatiFlags)


class ErrorResponse(BaseModel):
    error: str

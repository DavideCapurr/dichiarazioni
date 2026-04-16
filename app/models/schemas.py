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
    """Flag per le checkbox degli allegati.
    I primi 3 sono decisi dall'utente; gli ultimi 3 sono obbligatori (default True).
    """
    # Decidere dall'utente
    allegato_progetto: bool = False
    allegato_relazione: bool = False
    allegato_schema: bool = False
    # Obbligatori — pre-checked di default
    allegato_precedenti: bool = True
    allegato_certificato: bool = True
    allegato_conformita: bool = True


class DeclarationRequest(BaseModel):
    client_id: int
    declaration_date: date | None = Field(None, description="Data della dichiarazione")
    tipo_impianto: str | None = Field(None, description="Es. nuovo impianto idraulico")
    descrizione_impianto: str | None = Field(None, description="Descrizione dettagliata")
    comune_installazione: str | None = Field(None, description="Comune di installazione (override indirizzo cliente)")
    via_installazione: str | None = Field(None, description="Via di installazione (override indirizzo cliente)")
    proprietario: str | None = Field(None, description="Proprietario dell'immobile")
    uso_edificio: str | None = Field(None, description="Es. civile, commerciale, industriale")
    allegati: AllegatiFlags = Field(default_factory=AllegatiFlags)


class ErrorResponse(BaseModel):
    error: str

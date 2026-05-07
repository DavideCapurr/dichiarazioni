from datetime import date

from fastapi import APIRouter
from fastapi.responses import Response

from app.config import settings
from app.models.schemas import DeclarationRequest
from app.services.fattureincloud import get_client
from app.services.pdf_generator import generate_declaration

router = APIRouter(prefix="/api/declarations", tags=["declarations"])


@router.post("/generate")
def generate(request: DeclarationRequest):
    """Generate a compiled Dichiarazione di Conformità PDF for the given client."""
    client = get_client(request.client_id)

    # Build extra_fields from the request (only set non-empty values so the
    # PDF generator falls back to client data for address fields).
    decl_date = request.declaration_date or date.today()

    extra_fields: dict[str, str] = {
        "data": decl_date.strftime("%d/%m/%Y"),
    }
    for field in ("tipo_impianto", "descrizione_impianto", "proprietario",
                  "uso_edificio", "comune_installazione", "via_installazione"):
        val = getattr(request, field)
        if val:
            extra_fields[field] = val

    allegati_dict = request.allegati.model_dump()

    pdf_bytes = generate_declaration(
        client=client,
        template_path=settings.docx_template_abs_path,
        extra_fields=extra_fields,
        allegati=allegati_dict,
    )

    safe_name = client.name.replace(" ", "_").replace("/", "_")
    filename = f"dichiarazione_{safe_name}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

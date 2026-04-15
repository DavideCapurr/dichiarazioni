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

    extra_fields: dict[str, str] = {}
    if request.declaration_date:
        extra_fields["declaration_date"] = request.declaration_date.strftime("%d/%m/%Y")
    else:
        extra_fields["declaration_date"] = date.today().strftime("%d/%m/%Y")
    if request.declaration_number:
        extra_fields["declaration_number"] = request.declaration_number
    if request.notes:
        extra_fields["notes"] = request.notes

    pdf_bytes = generate_declaration(
        client=client,
        template_path=settings.pdf_template_abs_path,
        extra_fields=extra_fields,
    )

    safe_name = client.name.replace(" ", "_").replace("/", "_")
    filename = f"dichiarazione_{safe_name}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

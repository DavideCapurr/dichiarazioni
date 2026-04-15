from fastapi import APIRouter, Query

from app.models.schemas import ClientInfo, ClientSearchResponse
from app.services.fattureincloud import get_client, search_clients

router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("", response_model=ClientSearchResponse)
def list_clients(q: str = Query(..., min_length=1, description="Termine di ricerca")):
    """Search clients on Fatture in Cloud by name."""
    clients = search_clients(q)
    return ClientSearchResponse(clients=clients)


@router.get("/{client_id}", response_model=ClientInfo)
def get_client_detail(client_id: int):
    """Get a single client's details by ID."""
    return get_client(client_id)

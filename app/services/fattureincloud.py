import logging

import fattureincloud_python_sdk
from fattureincloud_python_sdk.api import clients_api

from app.config import settings
from app.models.schemas import ClientInfo

logger = logging.getLogger(__name__)


class FattureInCloudError(Exception):
    pass


class FattureInCloudAuthError(FattureInCloudError):
    pass


class FattureInCloudNotFoundError(FattureInCloudError):
    pass


def _get_api_client() -> fattureincloud_python_sdk.ApiClient:
    configuration = fattureincloud_python_sdk.Configuration()
    configuration.access_token = settings.fic_access_token
    return fattureincloud_python_sdk.ApiClient(configuration)


def _entity_to_client_info(entity) -> ClientInfo:
    return ClientInfo(
        id=entity.id,
        name=entity.name or "",
        vat_number=entity.vat_number,
        tax_code=entity.tax_code,
        email=entity.email,
        phone=entity.phone,
        address_street=entity.address_street,
        address_postal_code=entity.address_postal_code,
        address_city=entity.address_city,
        address_province=entity.address_province,
    )


def search_clients(query: str) -> list[ClientInfo]:
    """Search clients on Fatture in Cloud by name or VAT number."""
    with _get_api_client() as api_client:
        api = clients_api.ClientsApi(api_client)
        try:
            response = api.list_clients(
                company_id=settings.fic_company_id,
                q=f"name like '%{query}%'",
                fieldset="detailed",
                per_page=20,
            )
        except fattureincloud_python_sdk.ApiException as e:
            if e.status == 401:
                raise FattureInCloudAuthError(
                    "Token non valido o scaduto."
                ) from e
            logger.error("Errore API Fatture in Cloud: %s", e)
            raise FattureInCloudError(
                f"Errore nella comunicazione con Fatture in Cloud: {e.reason}"
            ) from e

    clients = []
    if response.data:
        for entity in response.data:
            clients.append(_entity_to_client_info(entity))
    return clients


def get_client(client_id: int) -> ClientInfo:
    """Get a single client by ID from Fatture in Cloud."""
    with _get_api_client() as api_client:
        api = clients_api.ClientsApi(api_client)
        try:
            response = api.get_client(
                company_id=settings.fic_company_id,
                client_id=client_id,
                fieldset="detailed",
            )
        except fattureincloud_python_sdk.ApiException as e:
            if e.status == 401:
                raise FattureInCloudAuthError(
                    "Token non valido o scaduto."
                ) from e
            if e.status == 404:
                raise FattureInCloudNotFoundError(
                    f"Cliente con ID {client_id} non trovato."
                ) from e
            logger.error("Errore API Fatture in Cloud: %s", e)
            raise FattureInCloudError(
                f"Errore nella comunicazione con Fatture in Cloud: {e.reason}"
            ) from e

    return _entity_to_client_info(response.data)

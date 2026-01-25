from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy.orm import Session

from api.config.db import get_db
from api.models.user import User
from api.services.auth_service import get_current_active_user
from api.services.client_service import add_client
from api.models.client import ClientCreate, ClientRead, ClientNIPRequest

import httpx
import datetime


router = APIRouter(
    prefix="/clients",
    tags=["clients"],
)


@router.post("/",
             status_code=status.HTTP_201_CREATED,
             response_model=ClientRead,
             summary="Create a new client",
             description="""
Create a new client.

    - Requires authentication.
    - Email and phone are empty by default and can be filled later.
    - Returns 201 with the created client.
    - Raises 409 if client with the same NIP already exists.
""")
async def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        db_client = add_client(db, client, owner_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return db_client


@router.post("/by-nip",
             status_code=status.HTTP_201_CREATED,
             response_model=ClientRead,
             summary="Create a new client by NIP",
             description="""
Create a new client by providing only the NIP number.  

    - Requires authentication.
    - Fetches client data from the external API (MF.gov.pl).
    - Email and phone are empty by default and can be filled later.
    - Returns 201 with the created client.
    - Raises 404 if the client is not found in the external API.
    - Raises 409 if a client with the same NIP already exists.

""")
async def create_client_by_nip(
    request_data: ClientNIPRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    nip = request_data.nip.replace("-", "").strip()
    date = datetime.date.today().strftime("%Y-%m-%d")

    url = f"https://wl-api.mf.gov.pl/api/search/nip/{nip}?date={date}"

    async with httpx.AsyncClient() as client:
        resp = await client.get(url)

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"Unable to fetch data for NIP {nip}"
        )

    api_data = resp.json().get("result", {}).get("subject", {})
    if not api_data:
        raise HTTPException(
            status_code=404, detail="Client not found in external API")

    client_create = ClientCreate(
        name=api_data.get("name", ""),
        email=None,  # fill later
        phone=None,  # fill later
        accountNumber=api_data.get("accountNumbers", [None])[0], # accountNumber can be empty list
        address=api_data.get("residenceAddress", ""),
        nip=api_data.get("nip", nip)
    )

    try:
        db_client = add_client(db, client_create, owner_id=current_user.id)
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))

    return db_client

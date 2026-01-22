from fastapi import Depends, APIRouter, status, HTTPException
from api.models.user import User
from api.services.auth_service import get_current_active_user
from api.services.client_service import add_client, get_client_by_id, update_client_data, is_nip_taken
from api.models.client import ClientCreate, ClientRead, ClientNIPRequest, ClientUpdate

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
    current_user: User = Depends(get_current_active_user),
):
    try:
        db_client = add_client(client, owner_id=current_user.id)
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

    accounts = api_data.get("accountNumbers") or []
    account_number = accounts[0] if accounts else None

    client_create = ClientCreate(
        name=api_data.get("name", ""),
        email=None,  # fill later
        phone=None,  # fill later
        accountNumber=account_number,
        address=api_data.get("residenceAddress", ""),
        nip=api_data.get("nip", nip)
    )

    try:
        db_client = add_client(client_create, owner_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return db_client


@router.put("/{id}",
            response_model=ClientRead,
            status_code=status.HTTP_200_OK,
            summary="Update client",
            description="""
Update client data.

    - Requires authentication.
    - Returns 200 with the updated client.
    - Raises 404 if the client is not found.
    - Raises 403 if the client is inactive.
    - Raises 409 if the client with the same NIP already exists.
    - Raises 403 if the user is not the owner of the client.
    """,
            )
async def update_client(
    id: int,
    data: ClientUpdate,
    current_user: User = Depends(get_current_active_user),
):
    db_client = get_client_by_id(id)
    # 404 – client not exist
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    # 403 – forbidden
    if db_client.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # block inactive client
    if not db_client.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive client cannot be edited"
        )
    # 409 – client with this NIP already exists
    if is_nip_taken(data.nip, exclude_id=db_client.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Client with this NIP already exists"
        )

    db_client = update_client_data(db_client, data)
    return db_client

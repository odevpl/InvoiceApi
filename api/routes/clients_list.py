from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.config.db import get_db
from api.models.db_user import UserDB
from api.models.client import ClientListResponse
from api.services.client_service import list_clients
from api.services.auth_service import get_current_active_user


router = APIRouter(
    prefix="/clients",
    tags=["clients"]
)


@router.get(
    "/list",
    response_model=ClientListResponse,
    status_code=status.HTTP_200_OK,
    summary="List clients of the current user",
    description="""
Returns a paginated list of clients belonging to the authenticated user.

- Requires JWT authentication.
- Sorted by name ascending.
- Supports pagination: limit (default 20), offset (default 0).
- Returns only active clients.
"""
)
def get_clients(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_active_user),
):
    clients, total = list_clients(
        db=db,
        owner_id=current_user.id,
        limit=limit,
        offset=offset
    )

    return ClientListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=clients
    )

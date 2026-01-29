from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from api.models.client import ClientCreate
from api.models.db_client import Client


def add_client(db: Session, client_data: ClientCreate, owner_id: int) -> Client:
    # Check if client with this NIP already exists
    existing_client = db.query(Client).filter(
        Client.nip == client_data.nip).first()
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Client with this NIP already exists"
        )
    client = Client(**client_data.dict(), owner_id=owner_id)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def list_clients(db: Session) -> list[Client]:
    return db.query(Client).all()

from sqlalchemy.orm import Session 
from fastapi import HTTPException, status

from api.models.db_client import Client
from api.models.client import ClientCreate


def add_client(db: Session, client_data: ClientCreate, owner_id: int) -> Client: 
    # Check if client with this NIP already exists 
    existing = db.query(Client).filter(Client.nip == client_data.nip).first() 
    if existing: 
        raise HTTPException( 
        status_code=status.HTTP_400_BAD_REQUEST, 
        detail="Client with this NIP already exists" 
        )

    client = Client( 
        name=client_data.name, 
        email=client_data.email, 
        phone=client_data.phone, 
        address=client_data.address, 
        nip=client_data.nip, 
        accountNumber=client_data.accountNumber, 
        owner_id=owner_id 
    ) 
    
    db.add(client) 
    db.commit() 
    db.refresh(client) 
    
    return client


def list_clients(
    db: Session,
    owner_id: int,
    limit: int = 20,
    offset: int = 0
):
    query = (
        db.query(Client)
        .filter(Client.owner_id == owner_id)
        .order_by(Client.name.asc())
    )

    total = query.count()
    clients = query.offset(offset).limit(limit).all()

    return clients, total

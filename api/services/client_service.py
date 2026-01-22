from api.models.client import ClientORM, ClientCreate, ClientUpdate

# Fake in-memory DB
db_clients: list[ClientORM] = []


def add_client(client_data: ClientCreate, owner_id: int) -> ClientORM:
    # Check if client with this NIP already exists
    for c in db_clients:
        if c.nip == client_data.nip:
            raise ValueError("Client with this NIP already exists")
    client = ClientORM(**client_data.dict(),
                       owner_id=owner_id, id=len(db_clients) + 1)
    db_clients.append(client)
    return client


def list_clients() -> list[ClientORM]:
    return db_clients


def get_client_by_id(id: int) -> ClientORM:
    for c in db_clients:
        if c.id == id:
            return c
    return None


def update_client_data(db_client: ClientORM, data: ClientUpdate) -> ClientORM:
    db_client.name = data.name
    db_client.email = data.email
    db_client.phone = data.phone
    db_client.address = data.address
    db_client.nip = data.nip
    db_client.accountNumber = data.accountNumber
    return db_client


def is_nip_taken(nip: str, exclude_id: int | None = None) -> bool:
    for c in db_clients:
        if c.nip == nip and c.id != exclude_id:
            return True
    return False

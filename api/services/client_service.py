from api.models.client import Client, ClientCreate

# Fake in-memory DB
db_clients: list[Client] = []


def add_client(client_data: ClientCreate, owner_id: int) -> Client:
    # Check if client with this NIP already exists
    for c in db_clients:
        if c.nip == client_data.nip:
            raise ValueError("Client with this NIP already exists")
    client = Client(**client_data.dict(),
                    owner_id=owner_id, id=len(db_clients)+1)
    db_clients.append(client)
    return client


def list_clients() -> list[Client]:
    return db_clients

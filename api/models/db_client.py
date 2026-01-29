from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from api.config.db import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    address = Column(String)
    nip = Column(String, nullable=False, unique=True, index=True)
    accountNumber = Column(String, nullable=True)

    owner_id = Column(ForeignKey("users.id"), nullable=False)

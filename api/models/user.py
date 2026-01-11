from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    email: str or None = None
    full_name: str or None = None
    role: str or None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str

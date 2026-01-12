
from api.models.user import UserInDB
from api.utils.password import verify_password


# Fake User DB
db = {
    "user": {
        "id": 1,
        "username": "user",
        "email": "user@example.com",
        "full_name": "User",
        "hashed_password": "$2b$12$PllgJv9J/vxzpa0ahieplOYMHYitrid5ZdWaseqMsPg6CEdpbky9K",  # password
        "role": "user",
        "disabled": False,
    }
}


def get_user(users_db, username: str):
    if username in users_db:
        user_dict = users_db[username]
        return UserInDB(**user_dict)


def authenticate_user(users_db, username: str, password: str):
    user = get_user(users_db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

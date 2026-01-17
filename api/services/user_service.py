from fastapi import HTTPException, status 
from sqlalchemy.orm import Session
from api.models.user import UserInDB
from api.models.db_user import User
from api.utils.password import verify_password, get_password_hash


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

def create_user(db: Session, username: str, email: str, password: str) -> User: 
    # Check email uniqueness 
    existing_email = db.query(User).filter(User.email == email).first() 
    if existing_email: 
        raise HTTPException ( 
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email is already registered" 
        ) 
    # Check username uniqueness
    existing_username = db.query(User).filter(User.username == username).first() 
    if existing_username: 
        raise HTTPException ( 
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username is already taken" 
        ) 
    
    # Hash the password
    hashed = get_password_hash(password) 
    
    # Create the user instance 
    new_user = User( 
        username=username, 
        email=email, 
        hashed_password=hashed, 
        role="user",  
        disabled=False 
    ) 
    
    # Save to the database 
    db.add(new_user) 
    db.commit() 
    db.refresh(new_user)
    
    return new_user

from pydantic_settings import BaseSettings
from pydantic import computed_field

class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @computed_field 
    def DATABASE_URL(self) -> str: 
        return ( 
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}" 
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}" 
        )

    class Config:
        env_file = ".env"

settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


class Settings(BaseSettings):
    DB_DIALECT: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    ADMIN_PASSWORD: str
    ADMIN_SECRET_KEY: str

    RESEND_API_KEY: str = ""

    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["*"]

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        if self.DB_DIALECT.startswith("sqlite"):
            return f"{self.DB_DIALECT}:///{self.DB_NAME}"
        return f"{self.DB_DIALECT}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=".env" if __import__("os").path.exists(".env") else None,
        env_file_encoding="utf-8",
    )


settings = Settings()

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# Принудительно загружаем .env и .env-example
load_dotenv(encoding="utf-8")


class RunModel(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8008


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"


class ApiPrefix(BaseModel):
    prefix: str = "api"
    v1: ApiV1Prefix = ApiV1Prefix()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env-template", ".env"),
        case_sensitive=False,
    )
    # postgres
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    pgdata: str

    # backend
    debug: bool = False
    secret_key: str
    allow_hosts: str
    celery_broker_url: str

    # redis
    redis_host: str
    redis_port: str
    redis_db: int

    # other
    run: RunModel = RunModel()
    api: ApiPrefix = ApiPrefix()


pydantic_settings = Settings()
# pprint(pydantic_settings.model_dump())

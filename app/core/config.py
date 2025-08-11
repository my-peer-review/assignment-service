import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str = "unit-test"

    jwt_algorithm: str = ""
    jwt_public_key_path: str = ""
    jwt_private_key_path: str = ""
    mongo_uri: str = ""
    mongo_db_name: str = ""

    class Config:
        env_file = None  # di default


# Leggi ENV
env = os.getenv("ENV", "unit-test")

if env == "unit-test":
    # Non carica nessun file, valori restano vuoti
    settings = Settings()

elif env == "test-integrazione":
    settings = Settings(_env_file=".env.integration")

elif env == "produzione":
    settings = Settings(_env_file=".env.prod")

else:
    # fallback per eventuali ambienti locali di sviluppo
    settings = Settings(_env_file=".env")

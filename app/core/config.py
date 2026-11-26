from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "SoporteIA API"
    app_version: str = "1.0.0"
    environment: str = "production"
    api_prefix: str = "/api/v1"
    seed_data: bool = True


settings = Settings()

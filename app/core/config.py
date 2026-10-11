from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Clerivon AgentOps"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    logistics_tracking_max_age_hours: int = 6
    approval_ttl_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)


settings = Settings()

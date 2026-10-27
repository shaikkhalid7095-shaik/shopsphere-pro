from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ShopSphere Pro"
    debug: bool = True

    # mysql connection - filled from .env
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "shopsphere"
    # if this is set it wins (used by tests -> sqlite)
    database_url: str = ""

    jwt_secret: str = "change-this-secret"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    refresh_token_days: int = 7

    currency: str = "INR"
    # leave stripe keys empty to use the built in sandbox gateway
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    sandbox_webhook_secret: str = "sandbox-webhook-secret"
    # courier companies send tracking updates with this token
    provider_webhook_token: str = "courier-token-123"

    # email / sms. provider "console" just prints to terminal
    email_provider: str = "console"
    sms_provider: str = "console"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "no-reply@shopsphere.local"

    upload_dir: str = "uploads"
    export_dir: str = "exports"
    return_window_days: int = 7

    scheduler_enabled: bool = True
    summary_interval_minutes: int = 1440
    outbox_interval_seconds: int = 60

    @property
    def db_url(self) -> str:
        if self.database_url:
            return self.database_url
        # quote_plus so passwords with @ or # don't break the url
        password = quote_plus(self.db_password)
        return (
            f"mysql+pymysql://{self.db_user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )


settings = Settings()
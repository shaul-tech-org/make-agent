from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "make-agent"
    app_version: str = "0.1.0"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173"]
    log_level: str = "INFO"

    # GitHub
    github_token: str = ""

    # Database
    database_url: str = "postgresql+asyncpg://make_agent:make_agent_dev@localhost:5436/make_agent"
    database_echo: bool = False

    model_config = {"env_prefix": "APP_"}


settings = Settings()

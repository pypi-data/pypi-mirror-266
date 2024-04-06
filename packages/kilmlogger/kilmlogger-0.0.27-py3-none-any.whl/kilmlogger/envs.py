from pydantic_settings import BaseSettings


class Env(BaseSettings):
    # The name of the environment.
    ENVIRONMENT: str | None = None
    SCRIBE_TIMEOUT: float = 0.05

    SCRIBE_HOST: str | None = None
    SCRIBE_PORT: str | None = None

    # The name of the application.
    APP_NAME: str | None = None

    # The version of the application.
    APP_VERSION: str | None = None

    # The category of the logging.
    DP_CATEGORY: str | None = None
    DP_LOG: str | None = None
    
    # Time format for the log.
    TIME_FORMAT: str = "%Y-%m-%d %H:%M:%S.%f %Z"


envs = Env()

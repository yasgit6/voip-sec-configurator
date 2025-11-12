from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "VoIP Security Configurator"
    version: str = "1.0.0"
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()

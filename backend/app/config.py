from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    livekit_url: str          # e.g. "wss://your-project.livekit.cloud"
    livekit_api_key: str
    livekit_api_secret: str

    gemini_api_key: str

    deepgram_api_key: str
    cartesia_api_key: str 

    # App
    cors_origins: str = "http://localhost:5173"

    model_config= SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]
    
settings = Settings()
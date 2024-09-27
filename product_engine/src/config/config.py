from pydantic_settings import BaseSettings, SettingsConfigDict

class ProductEngineSettings(BaseSettings):
    drivername : str
    username : str
    password : str
    host : str
    port : str
    database : str

    model_config = SettingsConfigDict(env_file=".env")
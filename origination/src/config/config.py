from pydantic_settings import BaseSettings, SettingsConfigDict

class OriginationSettings(BaseSettings):
    drivername : str
    username : str
    password : str
    host : str
    port : str
    database : str
    min_time_between_applications_in_sec : int

    model_config = SettingsConfigDict(env_file=".env")
from pydantic_settings import BaseSettings, SettingsConfigDict

class ProductEngineSettings(BaseSettings):
    # Database url:
    drivername : str
    username : str
    password : str
    host : str
    port : str
    database : str
    
    # Kafka config:
    kafka_topic_agreement : str
    kafka_host : str
    kafka_port : str

    model_config = SettingsConfigDict(env_file=".env")
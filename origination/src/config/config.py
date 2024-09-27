from pydantic_settings import BaseSettings, SettingsConfigDict

class OriginationSettings(BaseSettings):
    # Database url:
    drivername : str
    username : str
    password : str
    host : str
    port : str
    database : str
    
    # Constants
    min_time_between_applications_in_sec : int
    
    # Kafka config:
    kafka_topic_agreement : str
    kafka_host : str
    kafka_port : str
    group_id : str

    model_config = SettingsConfigDict(env_file=".env")
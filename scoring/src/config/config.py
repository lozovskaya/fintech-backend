from pydantic_settings import BaseSettings, SettingsConfigDict

class ScoringSettings(BaseSettings):
    # Database urls
    drivername : str
    username : str
    password : str
    host : str
    port : str
    database : str

    # Kafka config:
    kafka_topic_scoring_request : str
    kafka_topic_scoring_response : str
    kafka_host : str
    kafka_port : str
    group_id : str
    
    model_config = SettingsConfigDict(env_file=".env")
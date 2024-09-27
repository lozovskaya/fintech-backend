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
    kafka_topic_scoring_response : str
    kafka_topic_payment_received : str
    kafka_topic_overdue_payment : str
    kafka_host : str
    kafka_port : str
    group_id : str

    model_config = SettingsConfigDict(env_file=".env")
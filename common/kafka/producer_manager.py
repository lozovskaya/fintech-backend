from typing import Any, Dict
from aiokafka import AIOKafkaProducer

import json

from pydantic import BaseModel


class KafkaProducer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.producer: AIOKafkaProducer = None
    
    async def create(self):
        self.producer = AIOKafkaProducer(**self.config)

    async def start(self) -> None:
        await self.producer.start()

    async def stop(self) -> None:
        await self.producer.stop()

    async def send_message(self, topic_name: str, msg: BaseModel):
        return await self.producer.send(topic_name, json.dumps(msg.model_dump()).encode('ascii'))
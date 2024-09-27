from aiokafka import AIOKafkaConsumer
from typing import Any, Callable, Dict


class KafkaConsumer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.topic = None
        self.msg_handler: Callable = None
        self.consumer: AIOKafkaConsumer = None
        
    async def create(self, topic: str, msg_handler: Callable[[Any], Any]):
        self.topic = topic
        self.msg_handler = msg_handler
        self.consumer = AIOKafkaConsumer(topic, **self.config)
        
    async def start(self) -> None:
        await self.consumer.start()
        try:
            async for msg in self.consumer:
                await self.msg_handler(msg)
        finally:
            await self.consumer.stop()

    async def stop(self) -> None:
        await self.consumer.stop()
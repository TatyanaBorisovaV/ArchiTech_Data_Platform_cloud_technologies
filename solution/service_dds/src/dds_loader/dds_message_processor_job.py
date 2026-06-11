from datetime import datetime
from logging import Logger

from lib.kafka_connect.kafka_connectors import KafkaConsumer, KafkaProducer
from dds_loader.repository.dds_repository import DdsRepository
from dds_loader.repository.dds_repository import generate_uuid

class DdsMessageProcessor:
    def __init__(
        self,
        consumer: KafkaConsumer,
        producer: KafkaProducer,
        dds_repository: DdsRepository,
        logger: Logger
    ) -> None:

        self._consumer = consumer
        self._producer = producer
        self._dds_repository = dds_repository
        self._logger = logger

        self._batch_size = 30

    def run(self) -> None:
        self._logger.info(f"{datetime.utcnow()}: START")
        # читаем сообщение из кафка и передаём в репозиторий
        while True:
            msg = self._consumer.consume()

            if msg is None:
                continue

            self._logger.info(f"RECEIVED MESSAGE: {msg}")

            # записываем в DDS
            self._dds_repository.insert_order(msg)

            # выходное сообщение для Kafka
            items = []

            for product in msg["payload"]["products"]:
                items.append({
                    "product_id": str(generate_uuid(str(product["id"]))),
                    "product_name": product["name"],

                    "category_id": str(generate_uuid(str(product["category"]))),
                    "category_name": product["category"],

                    "quantity": product["quantity"]
                })

            output_message = {
                "user_id": str(generate_uuid(str(msg["payload"]["user"]["id"]))),
                "items": items
            }

            self._logger.info(
                f"SEND TO TOPIC {self._producer.topic}: {output_message}"
            )
            self._producer.produce(output_message)
            self._logger.info("MESSAGE SENT")
from datetime import datetime
from logging import Logger
from uuid import UUID

from lib.kafka_connect import KafkaConsumer
from cdm_loader.repository.cdm_repository import CdmRepository

class CdmMessageProcessor:
    def __init__(self,
                consumer: KafkaConsumer,
                cdm_repository: CdmRepository,
                logger: Logger,
                ) -> None:
                
                self._consumer = consumer
                self._cdm_repository = cdm_repository
                self._logger = logger

                self._batch_size = 100

    def run(self) -> None:
        self._logger.info(f"{datetime.utcnow()}: START")
        
        # читаем сообщение из кафка dds топика и передаём в репозиторий
        for _ in range(self._batch_size):

            message = self._consumer.consume()
            self._logger.info(f"CONSUMED MESSAGE: {message}")
            if not message:
                break
        
            user_id = UUID(str(message["user_id"]))

            for item in message["items"]:

                self._cdm_repository.increment_user_product_counter(
                    user_id=user_id,
                    product_id=UUID(str(item["product_id"])),
                    product_name=item["product_name"],
                    cnt=item["quantity"]
                )

                self._cdm_repository.increment_user_category_counter(
                    user_id=user_id,
                    category_id=UUID(str(item["category_id"])),
                    category_name=item["category_name"],
                    cnt=item["quantity"]
                )

        self._logger.info(f"{datetime.utcnow()}: FINISH")
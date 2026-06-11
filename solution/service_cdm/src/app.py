import logging

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

from app_config import AppConfig
from cdm_loader.cdm_message_processor_job import CdmMessageProcessor
from cdm_loader.repository.cdm_repository import CdmRepository

app = Flask(__name__)

config = AppConfig()


@app.get('/health')
def hello_world():
    return 'healthy'


if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    # Инициализируем конфиг. Для удобства, вынесли логику получения значений переменных окружения в отдельный класс.
    config = AppConfig()

    # Создаём зависимости через фабричные методы AppConfig
    pg_connect = config.pg_warehouse_db()
    cdm_repository = CdmRepository(pg_connect)
    consumer = config.kafka_consumer()

    # Создаём процессор сообщений с внедрением зависимостей
    proc = CdmMessageProcessor(
        consumer=consumer,
        cdm_repository=cdm_repository,
        logger=app.logger
    )

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=proc.run, trigger="interval", seconds=25)
    scheduler.start()

    app.run(debug=True, host='0.0.0.0', use_reloader=False)

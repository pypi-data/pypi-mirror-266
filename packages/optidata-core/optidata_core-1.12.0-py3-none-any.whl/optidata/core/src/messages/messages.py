import json
import logging

from ..config.kafka_config import KafkaConfig

log = logging.getLogger(__name__)


class Messages:
    kafka_obj = KafkaConfig()

    def obtiene_mensajes(self, topico, grupo):
        mensajes = []
        try:
            consumer = self.kafka_obj.get_message(topico, grupo)
            for message in consumer:
                mensajes.append(json.loads(message))

        except Exception as ex:
            log.exception(ex)
        return mensajes

    def envia_mensaje(self, topico, mensaje):
        try:
            self.kafka_obj.send_message(topico, mensaje)
        except Exception as ex:
            log.exception(ex)


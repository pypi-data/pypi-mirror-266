import logging

from ..messages.messages import Messages

log = logging.getLogger(__name__)


class UtilsMessages:
    @staticmethod
    def process_messages(topic, group):
        response = []
        msg = Messages()
        try:
            messages = msg.obtiene_mensajes(topico=topic, grupo=group)
            if messages:
                for message in messages:
                    response.append(message)
        except Exception as ex:
            log.exception(ex)

        return response

    @staticmethod
    def send_messages(topic, msg):
        kafka_svc = Messages()
        try:
            kafka_svc.envia_mensaje(topico=topic, mensaje=msg)
            log.info("Mensaje enviado al tópico %s : %s", topic, msg)
        except Exception as ex:
            log.exception(ex)
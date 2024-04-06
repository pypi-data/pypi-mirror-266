import json
import ssl
import sys

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

from ..config import constantes


class KafkaConfig:
    producer = None
    consumer = None

    def __get_context(self):
        # Create a new context using system defaults, disable all but TLS1.2
        self.context = ssl.create_default_context()
        self.context.options &= ssl.OP_NO_TLSv1
        self.context.options &= ssl.OP_NO_TLSv1_1

        return self.context

    def __set_producer(self, is_ssl=False):
        if is_ssl:
            self.producer = KafkaProducer(
                bootstrap_servers=[f'{constantes.KAFKA_BOOSTRAP}:{constantes.KAFKA_PORT}'],
                sasl_plain_username=constantes.KAFKA_USERNAME,
                sasl_plain_password=constantes.KAFKA_PASSWORD,
                security_protocol=constantes.KAFKA_SECURITY_PROTOCOL,
                ssl_context=self.__get_context(),
                sasl_mechanism=constantes.KAFKA_SASL_MECHANISM,
                value_serializer=lambda m: json.dumps(m).encode('utf-8'),
                api_version=(0, 10, 1),
                retries=5
            )
        else:
            self.producer = KafkaProducer(
                bootstrap_servers=[f'{constantes.KAFKA_BOOSTRAP}:{constantes.KAFKA_PORT}'],
                value_serializer=lambda m: json.dumps(m).encode('utf-8'),
                api_version=(0, 10, 1),
                retries=5
            )

    def __set_consumer(self, topic, group_id):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=[constantes.KAFKA_BOOSTRAP],
            api_version=(0, 10, 1),
            auto_offset_reset=constantes.KAFKA_OFFSET,
            max_poll_interval_ms=constantes.KAFKA_TIMEOUT,
            enable_auto_commit=False,
            group_id=group_id
        )

    def send_message(self, topic, message):
        try:
            self.__set_producer()
            future = self.producer.send(topic, message.encode(constantes.KAFKA_ENCODE))
            record_metadata = future.get(timeout=constantes.KAFKA_TIMEOUT)
            self.producer.flush()
        except KafkaError:
            print("Unexpected error:", sys.exc_info()[0])
            raise

    def get_message(self, topic, group_id):
        try:
            return self.__set_consumer(topic, group_id)
        except KafkaError:
            print("Unexpected error:", sys.exc_info()[0])
            raise

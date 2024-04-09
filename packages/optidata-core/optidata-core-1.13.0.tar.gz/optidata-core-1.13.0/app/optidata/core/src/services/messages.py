import logging

from ..config import settings
from ..utility.utils_messages import UtilsMessages

log = logging.getLogger(__name__)


def petition(json_dict):
    try:
        UtilsMessages.send_messages(settings.KAFKA_TOPIC_PETITION, json_dict)
    except Exception as ex:
        log.exception(ex)

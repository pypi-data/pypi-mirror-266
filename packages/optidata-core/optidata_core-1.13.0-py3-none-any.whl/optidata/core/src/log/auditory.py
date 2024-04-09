from ..config import settings
from ..database import MongoAPI
from ..utility import get_datetime


class AuditoryLogs:
    @staticmethod
    def registry_log(log):
        data = {
            'collection': settings.MONGO_COLLECTION_AUDITORY_LOGS,
            'Documents': {
                'origin': log['origin'],
                'event': log['event'],
                'description': log['description'],
                'user_id': log['user_id'],
                'created_at': get_datetime()
            }
        }

        mongodb = MongoAPI(data)
        mongodb.write(data)

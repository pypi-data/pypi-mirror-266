import datetime
import logging

from bson import ObjectId

from ..config import settings
from ..database.mongodb import MongoAPI
from ..utility.utils import get_message_error, get_datetime

log = logging.getLogger(__name__)


def new_role(data):
    try:
        date_doc = datetime.datetime.now()
        data = {
            'collection': settings.MONGO_COLLECTION_DATA_ROLES,
            'Document': {
                'description': data.get('description'),
                'is_admin': (data.get('description') == f'{settings.DEFAULT_ROLE_NAME_ADMIN}'),
                'active': data.get('active'),
                'created_at': date_doc
            },
            'Filter': {
                'description': data.get('description')
            },
            'DataToBeUpdated': {
                'description': data.get('description'),
                'updated_at': date_doc,
            }
        }

        mongodb = MongoAPI(data)
        response = mongodb.write(data)

    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def get_role(role_id):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_DATA_ROLES,
            'Filter': {
                '_id': ObjectId(role_id)
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.read()
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def get_all_roles():
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_DATA_ROLES,
            'Filter': {
                'active': True,
                'is_admin': False
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.all()
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def update_role(pid: str, request):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_DATA_PARTNERS,
            'Filter': {
                '_id': ObjectId(pid)
            },
            'DataToBeUpdated': {
                'description': request.get('nombre'),
                'active': request.get('activo'),
                'updated_at': get_datetime(),
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.update()
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def delete_role(pid: str):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_DATA_ROLES,
            'Filter': {
                '_id': ObjectId(pid)
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.write(data)

        if response:
            data = {
                'collection': settings.MONGO_COLLECTION_DATA_ROLES,
                'Filter': {
                    '_id': ObjectId(pid)
                },
                'DataToBeUpdated': {
                    'active': False,
                    'updated_at': get_datetime(),
                }
            }
            mongodb = MongoAPI(data)
            response = mongodb.update()
            if response:
                return {'Status': 'Eliminación exitosa'}

    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def check_role_exists(description):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_DATA_ROLES,
            'Filter': {
                'description': description
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.read()
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response

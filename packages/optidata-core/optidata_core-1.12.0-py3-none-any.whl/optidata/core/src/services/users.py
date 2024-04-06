import datetime
import logging

from bson import ObjectId

from ..config import settings
from ..database.mongodb import MongoAPI
from ..services.role import get_role
from ..utility.utils import password, get_message_error, get_datetime

log = logging.getLogger(__name__)


def new_user(data):
    try:
        date_doc = datetime.datetime.now()
        data = {
            'collection': settings.MONGO_COLLECTION_DATA_USERS,
            'Document': {
                'username': data.get('username'),
                'password': password(data.get('password')),
                'firstname': data.get('nombre'),
                'lastname': data.get('apellidos'),
                'rol_id': data.get('rol_id'),
                'active': data.get('active'),
                'created_at': date_doc
            },
            'Filter': {
                'username': data.get('username')
            },
            'DataToBeUpdated': {
                'firstname': data.get('nombre'),
                'lastname': data.get('apellidos'),
                'rol_id': data.get('rol_id'),
                'updated_at': date_doc,
            }
        }

        mongodb = MongoAPI(data)
        response = mongodb.write(data)

    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def get_user(pid: str):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_DATA_USERS,
            'Filter': {
                '_id': ObjectId(pid)
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.read()
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def get_all_users():
    users = []
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_DATA_USERS,
            'Filter': {
                'active': True
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.all()
        if response:
            for user in response:
                rol = get_role(user['rol_id'])
                if rol:
                    users.append({
                        'id': user['_id'],
                        'username': user['username'],
                        'firstname': user['firstname'],
                        'lastname': user['lastname'],
                        'rol_name': rol[0]['description'],
                        'rol_id': user['rol_id'],
                        'active': user['active'],
                    })
    except Exception as e:
        log.exception(e)
        users = get_message_error(e)
    return users


def update_user(pid: str, request):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_DATA_PARTNERS,
            'Filter': {
                '_id': ObjectId(pid)
            },
            'DataToBeUpdated': {
                'firstname': request.get('nombre'),
                'lastname': request.get('apellidos'),
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


def delete_user(pid: str):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_DATA_USERS,
            'Filter': {
                '_id': ObjectId(pid)
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.write(data)

        if response:
            data = {
                'collection': settings.MONGO_COLLECTION_DATA_USERS,
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


def get_all_users_by_rol(rol_id):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_DATA_USERS,
            'Filter': {
                'active': True,
                'rol_id': rol_id
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.all()
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def check_user_exists(description):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_DATA_USERS,
            'Filter': {
                'username': description
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.read()
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def check_current_user(pid):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_DATA_USERS,
            'Filter': {
                '_id': ObjectId(pid)
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.read()
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response

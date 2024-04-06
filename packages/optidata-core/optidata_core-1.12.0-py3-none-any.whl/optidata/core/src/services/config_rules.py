import logging
import os

from bson import ObjectId
from flask import jsonify
from werkzeug.utils import secure_filename

from ..config import constantes
from ..config import settings
from ..database.mongodb import MongoAPI
from ..utility.utils import allowed_file, get_datetime, get_uuid, get_message_error
from ..utility.utils_file import extract_headers_file

log = logging.getLogger(__name__)


def create_config_rule(json: dict):
    """
    Método que permite crear una nueva Configuración de Regla
    :param json:
    :return:
    """
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES,
            'Document': {
                f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': json.get(
                    f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}'),
                'user_id': json.get('user_id'),
                'config_state': json.get('config_state'),
                'created_at': get_datetime(),
                'active': True
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.write(data, True)
        if response:
            response = {
                f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': json.get(
                    f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}'),
                'user_id': json.get('user_id'),
                'config_state': json.get('config_state'),
                'config_rules_id': response['Document_ID']
            }
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def update_config_rule(json: dict):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES,
            'Filter': {
                '_id': ObjectId(json.get('id')),
            },
            'DataToBeUpdated': {
                'config_state': json.get('config_state'),
                'name_rule': json.get('name_rule'),
                'updated_at': get_datetime()
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.update()
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def validate_file(request):
    if 'file' not in request.files:
        resp = jsonify({'message': constantes.RESPONSE_NOT_PART_FILE_UPLOAD})
        resp.status_code = 400
        return resp

    file = request.files['file']
    '''if file.st_size == 0:
        resp = jsonify({'message': constantes.RESPONSE_EMPTY_SELECT_FILE_UPLOAD})
        resp.status_code = 400
    el'''
    if file.filename == constantes.EMPTY:
        resp = jsonify({'message': constantes.RESPONSE_NOT_SELECT_FILE_UPLOAD})
        resp.status_code = 400
    elif request.form['type'] is None:
        resp = jsonify({'message': constantes.RESPONSE_NOT_SETTING_TYPE_FILE_UPLOAD})
        resp.status_code = 400
    elif request.form['type'] == constantes.EMPTY:
        resp = jsonify({'message': constantes.RESPONSE_EMPTY_SETTING_TYPE_FILE_UPLOAD})
        resp.status_code = 400
    elif file and allowed_file(file.filename):
        file_name, file_extension = os.path.splitext(secure_filename(file.filename))

        # Save data upload
        type_data = request.form['type']
        user_id = request.form['user_id']
        partner_id = request.form[f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}']
        config_rule = request.form['config_rule']

        response = __set_upload_file(file, type_data, file_extension, user_id, partner_id, config_rule)
        if response:
            resp = jsonify(response)
            resp.status_code = 201
        else:
            resp = jsonify({'message': constantes.RESPONSE_ERROR_UPLOAD})
            resp.status_code = 500
    else:
        resp = jsonify({'message': f'Las extensiones permitidas son: {settings.FLASK_ALLOWED_EXTENSIONS}'})
        resp.status_code = 400

    return resp


def get_files(partner_id: str, config_rule_id: str):
    response = []
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES,
            'Filter': {
                f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': partner_id
            }
        }

        if config_rule_id != 'all':
            data['Filter']['_id'] = ObjectId(config_rule_id)

        mongodb = MongoAPI(data)
        config_rules = mongodb.all()
        for config_rule in config_rules:
            response = __get_response_fetch_upload(config_rule['_id'])

    except Exception as e:
        log.exception(e)
        response = get_message_error(e)

    return response


def get_file(pid: str):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_UPLOAD_FILE,
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


def get_columns_file(pid: str, type_data: str = ''):
    response = {}
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_COLUMNS,
            'Filter': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': pid
            }
        }

        if type_data != '':
            data['Filter']['type_data'] = type_data

        mongodb = MongoAPI(data)
        columns_file = mongodb.read()
        if len(columns_file) > 0:
            if type_data == '':
                data = {
                    'collection': settings.MONGO_COLLECTION_UPLOAD_FILE,
                    'Filter': {
                        '_id': ObjectId(pid)
                    }
                }
                mongodb = MongoAPI(data)
                detail_file = mongodb.read()
                if len(detail_file) > 0:
                    response = {
                        'type': detail_file[0]['type'],
                        'columns': columns_file[0]['columns']
                    }
            else:
                response = {
                    'type': type_data,
                    'columns': columns_file[0]['columns']
                }

    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def set_columns_file(pid: str, json: dict):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_COLUMNS,
            'Filter': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': pid,
                'type_data': json.get('type')
            },
            'DataToBeUpdated': {
                'columns': json.get('columns')
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.update()
        if response:
            mapping = []
            for item in json.get('columns'):
                if bool(item.get('col_used')):
                    mapping.append({
                        'col_name': item.get('col_name'),
                        'col_name_mapped': ''
                    })

            if len(mapping) > 0:
                data = {
                    'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_MAPPING_COLUMNS,
                    'Document': {
                        f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': pid,
                        'type_data': json.get('type'),
                        'mapping': mapping
                    },
                    'Filter': {
                        f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': pid,
                        'type_data': json.get('type')
                    },
                    'DataToBeUpdated': {
                        'mapping': mapping
                    }

                }
                mongodb = MongoAPI(data)
                response = mongodb.write(data)

            if response:
                response = __get_response_fetch_upload(pid)

    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def create_index_file(pid: str, json: dict):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_INDEX_COLUMNS,
            'Document': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': pid,
                'type_data': json.get('type'),
                'columns': json.get('columns')
            },
            'Filter': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': pid,
                'type_data': json.get('type')
            },
            'DataToBeUpdated': {
                'columns': json.get('columns')
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.write(data)
        if response:
            response = __get_response_fetch_upload(pid)
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def create_amount_column(pid: str, json: dict):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_AMOUNT_COLUMN,
            'Document': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': pid,
                'column': json.get('column')
            },
            'Filter': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': pid
            },
            'DataToBeUpdated': {
                'column': json.get('column')
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.write(data)
        if response:
            response = __get_response_fetch_upload(pid)
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def create_date_column(pid: str, json: dict):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_DATE_COLUMN,
            'Document': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': pid,
                'column': json.get('column')
            },
            'Filter': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': pid
            },
            'DataToBeUpdated': {
                'column': json.get('column')
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.write(data)
        if response:
            response = __get_response_fetch_upload(pid)
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def set_select_files_to_process(data: dict):
    pid = get_uuid()
    data = {
        'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_FILE,
        'Document': {
            f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': pid,
            'files': data.get('files')
        },
        'Filter': {
            f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': pid
        }
    }
    mongodb = MongoAPI(data)
    mongodb.write(data)


def get_index_file(pid: str, type_data: str):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_INDEX_COLUMNS,
            'Filter': {
                f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': pid,
                'type_data': type_data
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.read()
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def get_all_process_pending(cid: str):
    """
    Proceso que verifica si existen configuraciones pendientes
    :param cid: Identificador de la Configuración de la Regla
    :return: Lista de archivos pendientes por procesar y asociados al Socio
    """
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_UPLOAD_FILE,
            'Filter': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': cid,
                'file_processed': False
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.read()
        if response:
            response = __get_response_fetch_upload(response)
    except Exception as e:
        log.error(e)
        response = get_message_error(e)
    return response


def get_all():
    response = []
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES,
            'Filter': {
                'active': True
            }
        }
        mongodb = MongoAPI(data)
        config_rules = mongodb.all()
        for item in config_rules:
            data = {
                'collection': settings.MONGO_COLLECTION_DATA_PARTNERS,
                'Filter': {
                    '_id': ObjectId(item[f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}'])
                }
            }
            mongodb = MongoAPI(data)
            partner = mongodb.read()
            if partner:
                if 'name_rule' not in item:
                    name_rule = f"Regla para Socio {partner[0]['name']}"
                    data = {
                        'collection': settings.MONGO_COLLECTION_CONFIG_RULES,
                        'Filter': {
                            '_id': ObjectId(item['_id'])
                        },
                        'DataToBeUpdated': {
                            'name_rule': name_rule
                        }
                    }
                    mongodb = MongoAPI(data)
                    mongodb.update()
                else:
                    name_rule = item['name_rule']

                response.append({
                    f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': item['_id'],
                    f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': partner[0]['_id'],
                    'partner_name': partner[0]['name'],
                    'name_rule': name_rule,
                    'config_state': item['config_state'],
                    'created_at': item['created_at']
                })

    except Exception as e:
        log.error(e)
        response = get_message_error(e)
    return response


def set_mapping_columns(pid: str, json: dict):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_MAPPING_COLUMNS,
            'Document': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': pid,
                'type_data': json.get('type'),
                'mapping': json.get('mapping')
            },
            'Filter': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': pid,
                'type_data': json.get('type')
            },
            'DataToBeUpdated': {
                'mapping': json.get('mapping')
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.write(data)
        if response:
            response = __get_response_fetch_upload(pid)
    except Exception as e:
        log.error(e)
        response = get_message_error(e)
    return response


def get_mapping_columns(pid: str):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_MAPPING_COLUMNS,
            'Filter': {
                '_id': ObjectId(pid)
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.write(data)
    except Exception as e:
        log.error(e)
        response = get_message_error(e)
    return response


def get_all_config_rules_by_partner(cid: str, year: int = 0, month: int = 0, pid: str = ''):
    response = []
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES,
            'Filter': {
                f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': cid,
                'config_state': 'terminate',
                'active': True
            }
        }
        mongodb = MongoAPI(data)
        rules = mongodb.read()
        if rules:
            data = {
                'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_CNF,
                'Filter': {
                    f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': cid,
                    # 'state': 'config'
                }
            }

            if len(pid) > 0:
                data['Filter']['_id'] = ObjectId(pid)

            if year > 0:
                data['Filter']['year'] = int(year)
                data['Filter']['month'] = int(month)

            mongodb = MongoAPI(data)
            config_proc = mongodb.read()

            if len(config_proc) > 0:
                rule = list(
                    filter(lambda r: r['_id'] != config_proc[0][f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id'], rules)
                )
                if rule:
                    response = rule
            else:
                response = rules
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def config_remove(pid: str):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES,
            'Filter': {
                '_id': ObjectId(pid)
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.read()
        if len(response) > 0:
            data = {
                'collection': settings.MONGO_COLLECTION_CONFIG_RULES,
                'Filter': {
                    '_id': ObjectId(pid)
                },
                'DataToBeUpdated': {
                    'active': False,
                    'updated_at': get_datetime()
                }
            }
            mongodb = MongoAPI(data)
            response = mongodb.delete(data)
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


##################################
#     Section Private Methods    #
##################################
def __set_upload_file(
        file,
        type_data: str,
        ext: str,
        user_id: str,
        partner_id: str,
        config_rule: str):
    try:
        time_process = get_datetime()
        response = __create_config_rule(config_rule, partner_id, user_id, time_process)
        if response:
            config_rules_id = response['Document_ID']
            columns = extract_headers_file(file, ext)
            if columns:
                response = __create_config_rule_source_columns(config_rules_id, type_data, columns)
                if len(response) > 0:
                    response = __get_response_fetch_upload(config_rules_id)

    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def __get_amount_column(pid: str):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_AMOUNT_COLUMN,
            'Filter': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': pid
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.read()
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def __get_date_column(pid: str):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_DATE_COLUMN,
            'Filter': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': pid
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.read()
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def __get_response_fetch_upload(cri: str, year: int = 0, month: int = 0):
    data = {
        'collection': settings.MONGO_COLLECTION_CONFIG_RULES,
        'Filter': {
            '_id': ObjectId(cri)
        }
    }
    mongodb = MongoAPI(data)
    config_rules = mongodb.read()
    amount_column = []
    date_column = []
    for config_rule in config_rules:
        files = []
        partner_id = config_rule[f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}']
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_COLUMNS,
            'Filter': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': cri
            }
        }

        if int(year) > 0 and int(month) > 0:
            data['Filter']['year'] = year
            data['Filter']['month'] = month

        mongodb = MongoAPI(data)
        response = mongodb.read()
        for item in response:
            columns = __get_response_fetch_upload_detail_columns(cri, item["type_data"])
            amount_column = __get_amount_column(cri)
            date_column = __get_date_column(cri)
            if item["type_data"] == 'external':

                data = {
                    'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_MAPPING_COLUMNS,
                    'Filter': {
                        f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': cri,
                        'type_data': item["type_data"]
                    }
                }
                mongodb = MongoAPI(data)
                response = mongodb.read()
                mapping = []

                if response:
                    mapping = response[0]['mapping']
                else:
                    for cols in columns:
                        if cols['col_used']:
                            mapping.append({
                                'col_name': cols['col_name'],
                                'col_name_mapped': ''
                            })

                files.append({
                    'type': f'{item["type_data"]}',
                    'columns': columns,
                    'mapping': mapping
                })
            else:
                data = {
                    'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_INDEX_COLUMNS,
                    'Filter': {
                        f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': cri,
                        'type_data': item["type_data"]
                    }
                }
                mongodb = MongoAPI(data)
                response = mongodb.read()
                indexes = []
                if response:
                    indexes = response[0]['columns']

                files.append({
                    'type': f'{item["type_data"]}',
                    'columns': columns,
                    'indexes': indexes
                })

        name_rule = ''
        if 'name_rule' in config_rule:
            name_rule = config_rule['name_rule']

        data_amount_col = ''
        data_date_col = ''
        if len(amount_column) > 0:
            data_amount_col = amount_column[0]['column']

        if len(date_column) > 0:
            data_date_col = date_column[0]['column']

        return {
            'id': cri,
            'name_rule': name_rule,
            f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': partner_id,
            'config_rules': files,
            'amountColumn': data_amount_col,
            'amountDate': data_date_col
        }
    return {}


def __get_response_fetch_upload_detail_columns(config_rules_id: str, type_data: str):
    data = {
        'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_COLUMNS,
        'Filter': {
            f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': config_rules_id,
            'type_data': type_data
        }
    }
    mongodb = MongoAPI(data)
    upload_file_cols = mongodb.read()

    columns = []
    for cols in upload_file_cols[0]['columns']:
        columns.append({
            'col_name': cols['col_name'],
            'col_used': cols['col_used'],
            'col_norm': cols['col_norm'],
            'col_type': cols['col_type']
        })

    return columns


def __create_config_rule(config_rule: str, partner_id: str, user_id: str, time_process: str):
    # Crea Regla Socio
    data = {
        'collection': settings.MONGO_COLLECTION_CONFIG_RULES,
        'Document': {
            'user_id': user_id,
            f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': partner_id,
            'config_state': 'pending',
            'created_at': time_process
        },
        'Filter': {
            f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': partner_id,
            '_id': ObjectId(config_rule)
        },
        'DataToBeUpdated': {
            'updated_at': time_process
        }
    }
    mongodb = MongoAPI(data)
    return mongodb.write(data)


def __create_upload_file_columns(config_rules_id: str, columns):
    # Carga Columnas de Archivo Subido
    data = {
        'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_COLUMNS,
        'Document': {
            f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': config_rules_id,
            'columns': columns
        },
        'Filter': {
            f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': config_rules_id
        }
    }
    mongodb = MongoAPI(data)
    return mongodb.write(data)


def __create_config_rule_source_columns(config_rules_id: str, type_data: str, columns):
    """
    Carga Columnas de Archivo Subido
    :param config_rules_id:
    :param columns:
    :return:
    """
    data = {
        'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_COLUMNS,
        'Document': {
            f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': config_rules_id,
            'type_data': type_data,
            'columns': columns
        },
        'Filter': {
            f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': config_rules_id,
            'type_data': type_data
        },
        'DataToBeUpdated': {
            'columns': columns
        }
    }
    mongodb = MongoAPI(data)
    return mongodb.write(data)

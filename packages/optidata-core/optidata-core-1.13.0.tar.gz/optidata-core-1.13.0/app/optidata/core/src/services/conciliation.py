import logging
import os
import time

import pandas as pd
from bson import ObjectId
from flask import jsonify, make_response
from werkzeug.utils import secure_filename

from ..config import constantes
from ..config import settings
from ..database.mongodb import MongoAPI
from .config_rules import get_file, get_columns_file, get_all_config_rules_by_partner
from .partner import get_partner
from ..utility.utils import get_datetime, allowed_file, get_message_error
from ..utility.utils_file import execute_process_conciliation, convert_file_to_hfs5

log = logging.getLogger(__name__)
n = 10000


def upload_file(request):
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
        partner_id = request.form[f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}']
        config_proc = request.form['config_id']
        year = 0
        month = 0

        if 'year' in request.form:
            year = int(request.form['year'])

        if 'month' in request.form:
            month = int(request.form['month'])

        # TODO: Acá debiese colocarse la logica para subir los archivos al SFTP si está configurado así
        if year > 0 and month > 0:
            partner = get_partner(partner_id)
            path_upload = os.path.join(
                settings.FLASK_UPLOAD_FOLDER,
                partner[0]['name'],
                f'{year}',
                f'{month}'
            )

            if not os.path.exists(path_upload):
                os.makedirs(path_upload)

            file.save(os.path.join(path_upload, f'{file_name}{file_extension}'))
            file.close()
            convert_file_to_hfs5(
                os.path.join(partner[0]['name'], f'{year}', f'{month}'),
                file_name,
                file_extension
            )

        response = upload_file_by_partner(
            config_proc,
            type_data,
            file_name,
            file_extension,
            year,
            month
        )
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


def upload_file_by_partner(
        config_proc: str,
        type_data: str,
        filename: str,
        ext: str,
        year: int,
        month: int):
    response = []
    try:
        time_process = get_datetime()
        upload_file_response = __create_upload_file(time_process, filename, ext, type_data, year, month)
        if upload_file_response:
            upload_file_id = upload_file_response['Document_ID']
            data = {
                'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_FILE,
                'Document': {
                    f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': config_proc,
                    f'{settings.MONGO_COLLECTION_UPLOAD_FILE}_id': upload_file_id,
                    'status': 'not-processed',
                    'created_at': time_process
                },
                'Filter': {
                    f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': config_proc,
                    f'{settings.MONGO_COLLECTION_UPLOAD_FILE}_id': upload_file_id
                }
            }

            mongodb = MongoAPI(data)
            cnf_proc_files = mongodb.write(data)
            if cnf_proc_files:
                response = get_files_upload(config_proc)
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def get_files_upload(config_proc: str):
    data = {
        'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_FILE,
        'Filter': {
            f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': config_proc
        }
    }
    mongodb = MongoAPI(data)
    proc_files = mongodb.read()
    files = []
    for proc_file in proc_files:
        data = {
            'collection': settings.MONGO_COLLECTION_UPLOAD_FILE,
            'Filter': {
                f'_id': ObjectId(proc_file[f'{settings.MONGO_COLLECTION_UPLOAD_FILE}_id'])
            }
        }
        mongodb = MongoAPI(data)
        up_file = mongodb.read()
        if up_file:
            files.append({
                'filename': f'{up_file[0]["filename"]}{up_file[0]["extension"]}',
                'type': up_file[0]["type"]
            })
    return {
        'files': files
    }


def get_index_file(pid: str, type_data: str):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES_DEFINED_INDEX_COLUMNS,
            'Filter': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': pid,
                'type_data': type_data
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.read()
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def get_columns_amount(pid: str):
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


def get_columns_date(pid: str):
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


def process_files(json_data: dict):
    """data = {
        'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_CNF,
        'Filter': {
            '_id': ObjectId(json_data.get('doc_id'))
        }
    }
    mongodb = MongoAPI(data)
    response = mongodb.read()
    if len(response) > 0:
        queue_cxp = QueueCxP()
        queue_cxp.add_message(json_data)

    return [{
        'message': 'Proceso lanzado exitosamente'
    }]


def exec_process(json_data: dict):
    while True:"""
    start = time.time()
    date_start = get_datetime()
    process = []
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_CNF,
            'Filter': {
                '_id': ObjectId(json_data.get('doc_id'))
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.read()
        if len(response) > 0:
            config_process = response[0]

            data = {
                'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_FILE,
                'Filter': {
                    f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': config_process['_id']
                }
            }
            mongodb = MongoAPI(data)
            config_process_files = mongodb.read()

            documents = []
            columns = []
            filters = []
            amounts = []
            dates = []
            for cnf_proc_file in config_process_files:
                # Obtiene detalle de Archivo asociado a ID
                data_file = get_file(cnf_proc_file[f'{settings.MONGO_COLLECTION_UPLOAD_FILE}_id'])
                if len(data_file) > 0:
                    up_file = data_file[0]
                    documents.append(up_file)

                    # Obtiene detalle de las columnas configuradas por archivo
                    cnf_rules_columns = get_columns_file(
                        config_process[f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id'],
                        up_file['type']
                    )
                    if len(cnf_rules_columns) > 0:
                        columns.append(cnf_rules_columns['columns'])

                    # Obtiene el indice a utilizar
                    cnf_rules_indexes = get_index_file(
                        config_process[f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id'],
                        up_file['type']
                    )
                    if len(cnf_rules_indexes) > 0:
                        filters.append(cnf_rules_indexes[0]['columns'])

                    # Obtiene la columna totalizadora a utilizar si existe
                    cnf_amount_columns = get_columns_amount(
                        config_process[f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id']
                    )
                    if len(cnf_amount_columns) > 0 and cnf_amount_columns[0]['column'] not in amounts:
                        amounts.append(cnf_amount_columns[0]['column'])

                    # Obtiene la columna fecha de filtro a utilizar si existe
                    cnf_date_columns = get_columns_date(
                        config_process[f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id']
                    )
                    if len(cnf_date_columns) > 0 and cnf_date_columns[0]['column'] not in dates:
                        dates.append(cnf_date_columns[0]['column'])

            if len(documents) > 0 and len(columns) > 0 and len(filters) > 0:
                external = []
                columns_df = []
                columns_idx = []
                columns_normalized = {}
                for col in columns:
                    for c in col:
                        if c.get('col_used') and c.get('col_name') not in columns_df:
                            columns_df.append(c.get('col_name'))

                        if c.get('col_norm') and c.get('col_used') and c.get('col_name') not in columns_normalized:
                            columns_normalized[c.get('col_name')] = c.get('col_type')

                for col in filters:
                    for c in col:
                        if c.get('col_name') not in columns_idx:
                            columns_idx.append(c.get('col_name'))

                if len(columns_df) > 0:
                    filter_external_data = list(filter(lambda d: (d['type'] == 'primary'), documents))
                    filter_data = filter_external_data[0]

                    partner_name = \
                        get_partner(config_process[f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}'])[0]['name']

                    internal = {
                        'year': int(filter_data['year']),
                        'month': int(filter_data['month']),
                        'partner': partner_name,
                        'filename': filter_data['filename'],
                        'extension': filter_data['extension']
                    }

                    filter_external_data = list(filter(lambda d: (d['type'] == 'external'), documents))
                    for filter_data in filter_external_data:
                        external_items = {
                            'year': int(filter_data['year']),
                            'month': int(filter_data['month']),
                            'partner': partner_name,
                            'filename': filter_data['filename'],
                            'extension': filter_data['extension']
                        }
                        external.append(external_items)

                    # Ejecución del proceso conciliación
                    process_detail = {
                        'internal': internal,
                        'external': external,
                        'columns_normalized': columns_normalized,
                        'columns_df': columns_df,
                        'columns_index_df': columns_idx,
                        'columns_amount': amounts,
                        'columns_date': dates
                    }
                    process.append(process_detail)

                    # Inicio Proceso Conciliación
                    result = execute_process_conciliation(process, json_data.get('doc_id'))
                    if result and 'msg' not in result:
                        date_process_executed = get_datetime()
                        # Se almacena resultado de conciliados y no conciliados en MongoDB
                        dict_reconciled_primary = result.get('primary-process').get('data_reconciled')
                        dict_reconciled_secondary = result.get('secondary-process').get('data_reconciled')
                        dict_unreconciled_primary = result.get('primary-process').get('data_unreconciled')
                        dict_unreconciled_secondary = result.get('secondary-process').get('data_unreconciled')
                        dict_duplicated_primary = result.get('primary-process').get('data_duplicated')
                        dict_duplicated_secondary = result.get('secondary-process').get('data_duplicated')

                        if len(dict_reconciled_primary) > 0 or len(dict_reconciled_secondary) > 0:
                            # Se eliminan resultado de datos conciliados
                            data = {
                                'collection': settings.MONGO_COLLECTION_DATA_RECONCILED,
                                'Filter': {
                                    f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': json_data.get('doc_id')
                                }
                            }
                            mongodb = MongoAPI(data)
                            mongodb.delete_many(data)

                            # Se almacena resultado de datos conciliados
                            if len(dict_reconciled_primary) > 0:
                                data['Filter']['type_process'] = 'primary'
                                mongodb = MongoAPI(data)
                                mongodb.write_many(dict_reconciled_primary)

                            if len(dict_reconciled_secondary) > 0:
                                data['Filter']['type_process'] = 'secondary'
                                mongodb = MongoAPI(data)
                                mongodb.write_many(dict_reconciled_secondary)

                            # Se almacena total de conciliados
                            if len(dict_reconciled_primary) > 0:
                                data = {
                                    'collection': settings.MONGO_COLLECTION_DATA_TOTAL_RECONCILED,
                                    'Document': {
                                        'total_reconciled': int(result.get('primary-process').get('total_reconciled')),
                                        'type_process': 'primary',
                                        'date_process': date_process_executed,
                                        f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': json_data.get('doc_id')
                                    },
                                    'Filter': {
                                        f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': json_data.get('doc_id'),
                                        'type_process': 'primary'
                                    }
                                }
                                mongodb = MongoAPI(data)
                                mongodb.write(data)

                            if len(dict_reconciled_secondary) > 0:
                                data = {
                                    'collection': settings.MONGO_COLLECTION_DATA_TOTAL_RECONCILED,
                                    'Document': {
                                        'total_reconciled': int(
                                            result.get('secondary-process').get('total_reconciled')),
                                        'type_process': 'secondary',
                                        'date_process': date_process_executed,
                                        f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': json_data.get('doc_id')
                                    },
                                    'Filter': {
                                        f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': json_data.get('doc_id'),
                                        'type_process': 'secondary'
                                    }
                                }
                                mongodb = MongoAPI(data)
                                mongodb.write(data)

                        if len(dict_unreconciled_primary) > 0 or len(dict_unreconciled_secondary) > 0:
                            # Se eliminan resultado de datos no conciliados
                            data = {
                                'collection': settings.MONGO_COLLECTION_DATA_UNRECONCILED,
                                'Filter': {
                                    f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': json_data.get('doc_id')
                                }
                            }
                            mongodb = MongoAPI(data)
                            mongodb.delete_many(data)

                            # Se almacenan resultados de datos no conciliados
                            if len(dict_unreconciled_primary) > 0:
                                data['Filter']['type_process'] = 'primary'
                                mongodb = MongoAPI(data)
                                mongodb.write_many(dict_unreconciled_primary)

                            if len(dict_unreconciled_secondary) > 0:
                                data['Filter']['type_process'] = 'secondary'
                                mongodb = MongoAPI(data)
                                mongodb.write_many(dict_unreconciled_secondary)

                            # Se almacena total de no conciliados
                            if len(dict_unreconciled_primary) > 0:
                                data = {
                                    'collection': settings.MONGO_COLLECTION_DATA_TOTAL_UNRECONCILED,
                                    'Document': {
                                        'total_unreconciled': int(
                                            result.get('primary-process').get('total_unreconciled')
                                        ),
                                        'type_process': 'primary',
                                        'date_process': date_process_executed,
                                        f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': json_data.get('doc_id')
                                    },
                                    'Filter': {
                                        f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': json_data.get('doc_id'),
                                        'type_process': 'primary'
                                    }
                                }
                                mongodb = MongoAPI(data)
                                mongodb.write(data)

                            if len(dict_unreconciled_secondary) > 0:
                                data = {
                                    'collection': settings.MONGO_COLLECTION_DATA_TOTAL_UNRECONCILED,
                                    'Document': {
                                        'total_unreconciled': int(
                                            result.get('secondary-process').get('total_unreconciled')),
                                        'type_process': 'secondary',
                                        'date_process': date_process_executed,
                                        f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': json_data.get('doc_id')
                                    },
                                    'Filter': {
                                        f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': json_data.get('doc_id'),
                                        'type_process': 'secondary'
                                    }
                                }
                                mongodb = MongoAPI(data)
                                mongodb.write(data)

                        if len(dict_duplicated_primary) > 0 or len(dict_duplicated_secondary) > 0:
                            # Se eliminan resultado de datos duplicados
                            data = {
                                'collection': settings.MONGO_COLLECTION_DATA_DUPLICATES,
                                'Filter': {
                                    f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': json_data.get('doc_id')
                                }
                            }
                            mongodb = MongoAPI(data)
                            mongodb.delete_many(data)

                            # Se almacena resultado de datos duplicados
                            if len(dict_duplicated_primary) > 0:
                                data['Filter']['type_process'] = 'primary'
                                mongodb = MongoAPI(data)
                                mongodb.write_many(dict_duplicated_primary)

                            if len(dict_duplicated_secondary) > 0:
                                data['Filter']['type_process'] = 'secondary'
                                mongodb = MongoAPI(data)
                                mongodb.write_many(dict_duplicated_secondary)

                            # Se almacena total de duplicados

                            if len(dict_duplicated_primary) > 0:
                                data = {
                                    'collection': settings.MONGO_COLLECTION_DATA_TOTAL_DUPLICATES,
                                    'Document': {
                                        'total_duplicated': int(result.get('primary-process').get('total_duplicated')),
                                        'type_process': 'primary',
                                        'date_process': date_process_executed,
                                        f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': json_data.get('doc_id')
                                    },
                                    'Filter': {
                                        f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': json_data.get('doc_id'),
                                        'type_process': 'primary'
                                    }
                                }
                                mongodb = MongoAPI(data)
                                mongodb.write(data)

                            if len(dict_duplicated_secondary) > 0:
                                data = {
                                    'collection': settings.MONGO_COLLECTION_DATA_TOTAL_DUPLICATES,
                                    'Document': {
                                        'total_duplicated': int(result.get('primary-process').get('total_duplicated')),
                                        'type_process': 'secondary',
                                        'date_process': date_process_executed,
                                        f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': json_data.get('doc_id')
                                    },
                                    'Filter': {
                                        f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': json_data.get('doc_id'),
                                        'type_process': 'secondary'
                                    }
                                }
                                mongodb = MongoAPI(data)
                                mongodb.write(data)

                        end = time.time()
                        date_end = get_datetime()

                        # Actualizar estado del proceso en la tabla
                        data = {
                            'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_CNF,
                            'Filter': {
                                '_id': ObjectId(json_data.get('doc_id'))
                            },
                            'DataToBeUpdated': {
                                'state': constantes.CODE_STATE_CONFIG_EXECUTED,
                                'executed_count': int(config_process['executed_count']) + 1,
                                'start_process': date_start,
                                'end_process': date_end,
                                'time_process': round((end - start) / 60, 2),
                                'total_reconciled': int(result.get('primary-process').get('total_reconciled')),
                                'total_unreconciled': int(result.get('primary-process').get('total_unreconciled')),
                                'total_duplicated': int(result.get('primary-process').get('total_duplicated'))
                            }
                        }
                        mongodb = MongoAPI(data)
                        mongodb.update()
                    else:
                        return make_response(jsonify(result), 400)
            response = get_all('-')
    except KeyError as e:
        log.exception(e)
        response = get_message_error(e)
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)

    return response


def get_all(cid: str):
    response = []
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_CNF
        }
        if cid != '-':
            data['Filter'] = {
                f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': cid
            }

        mongodb = MongoAPI(data)
        reconciled_cnf = mongodb.read()
        for rec_cnf in reconciled_cnf:
            partner = get_partner(rec_cnf[f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}'])
            rule = get_data_rule(rec_cnf[f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id'])
            row = {
                'id': rec_cnf["_id"],
                f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': rec_cnf[
                    f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}'
                ],
                'rule_name': rule[0]['name_rule'] if len(rule) > 0 else 'Sin Nombre Regla',
                'partner_name': partner[0]['name'],
                'period': f'{rec_cnf["month"]}/{rec_cnf["year"]}',
                'config_state': rec_cnf['state'],
                'executed_state': __get_state_config_reconciled(rec_cnf['state']),
                'created_at': rec_cnf["created_at"],
                'executed_count': 0 if 'executed_count' not in rec_cnf else int(rec_cnf["executed_count"]),
                'year': int(rec_cnf["year"]),
                'month': int(rec_cnf["month"]),
                'config_id': rec_cnf["config_rules_id"],
                'start_process': '' if 'start_process' not in rec_cnf else rec_cnf["start_process"],
                'end_process': '' if 'end_process' not in rec_cnf else rec_cnf["end_process"],
                'time_process': '' if 'time_process' not in rec_cnf else rec_cnf["time_process"],
                'total_reconciled': 0 if 'total_reconciled' not in rec_cnf else int(rec_cnf['total_reconciled']),
                'total_unreconciled': 0 if 'total_unreconciled' not in rec_cnf else int(rec_cnf['total_unreconciled']),
                'total_duplicated': 0 if 'total_duplicated' not in rec_cnf else int(rec_cnf['total_duplicated'])
            }

            response.append(row)
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def get_data_rule(pid: str):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_CONFIG_RULES,
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


def get_all_selected(cid: str, year: int, month: int, pid: str = ''):
    response = []
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_CNF,
            'Filter': {
                f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': cid,
                'year': int(year),
                'month': int(month)
            }
        }

        if len(pid) > 0:
            data['Filter']['_id'] = ObjectId(pid)

        mongodb = MongoAPI(data)
        config_proc = mongodb.read()
        if len(config_proc) > 0 and config_proc[0][f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id'] != '':
            data = {
                'collection': settings.MONGO_COLLECTION_CONFIG_RULES,
                'Filter': {
                    f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': cid,
                    'config_state': 'terminate',
                    '_id': ObjectId(config_proc[0][f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id'])
                }
            }

            mongodb = MongoAPI(data)
            rules = mongodb.read()
            for rule in rules:
                for cnf in config_proc:
                    response.append({
                        'name_rule': rule['name_rule'],
                        'rule_id': rule['_id'],
                        'created_at': cnf['created_at']
                    })
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def del_all_selected(cid: str, year: int, month: int):
    response = []
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_CNF,
            'Filter': {
                f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': cid,
                'year': int(year),
                'month': int(month),
                'state': 'config'
            }
        }

        mongodb = MongoAPI(data)
        config_proc = mongodb.read()
        if config_proc:
            data = {
                'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_CNF,
                'Filter': {
                    f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': cid,
                    'year': int(year),
                    'month': int(month),
                    '_id': ObjectId(config_proc['_id'])
                }
            }

            mongodb = MongoAPI(data)
            response = mongodb.delete(data)

    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def set_rule_selected(cid: str, json_data: dict):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_CNF,
            'Document': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': json_data.get('config_id'),
                f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': cid,
                'user_id': json_data.get('user_id'),
                'year': int(json_data.get('year')),
                'month': int(json_data.get('month')),
                'created_at': get_datetime(),
                'state': constantes.CODE_STATE_CONFIG_PENDING
            },
            'Filter': {
                f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': cid,
                'year': int(json_data.get('year')),
                'month': int(json_data.get('month')),
                '_id': ObjectId(json_data.get('id'))
            },
            'DataToBeUpdated': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': json_data.get('config_id'),
                'updated_at': get_datetime()
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.write(data)
        if response and 'Document_ID' in response:
            response = detail_conf_reconciled(
                cid,
                int(json_data.get('year')),
                int(json_data.get('month')),
                response['Document_ID']
            )

    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def del_rule_selected(cid, json_data: dict):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_CNF,
            'Filter': {
                '_id': ObjectId(json_data.get('id')),
                f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': cid,
                'year': int(json_data.get('year')),
                'month': int(json_data.get('month'))
            },
            'DataToBeUpdated': {
                f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id': '',
                'updated_at': get_datetime()
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.update()
        if response and response['Status'] == 'Actualización exitosa':
            response = detail_conf_reconciled(
                cid,
                int(json_data.get('year')),
                int(json_data.get('month')),
                json_data.get('id')
            )

    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def new_config_reconciled(json_data: dict):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_CNF,
            'Document': {
                f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': \
                    json_data.get(f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}'),
                'year': json_data.get('year'),
                'month': json_data.get('month'),
                'status': constantes.CODE_STATE_CONFIG_PENDING,
                'created_at': get_datetime()
            },
            'Filter': {
                f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': \
                    json_data.get(f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}'),
                'year': json_data.get('year'),
                'month': json_data.get('month'),
            }
        }
        mongodb = MongoAPI(data)
        response = mongodb.write(data)
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def update_config_reconciled(json_data: dict):
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_CNF,
            'Filter': {
                '_id': ObjectId(json_data.get('id'))
            },
            'DataToBeUpdated': {
                'state': json_data.get('state'),
                'executed_count': 0,
                'updated_at': get_datetime()
            }
        }

        mongodb = MongoAPI(data)
        response = mongodb.write(data)
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def get_detail_process(cid: str, year: int, month: int, pag: int, limit: int, report: str, type_process: str):
    offset = (int(limit) * int(pag)) - (int(limit) - 1)
    response = []
    process_conciliation = {}
    try:
        data = {
            'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_CNF,
            'Filter': {
                f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': cid,
                'year': int(year),
                'month': int(month),
                'state': constantes.CODE_STATE_CONFIG_EXECUTED
            }
        }

        mongodb = MongoAPI(data)
        proc_recon = mongodb.read()
        for item in proc_recon:
            if report == constantes.OPTION_REPORTS_ALL or report == constantes.OPTION_REPORTS_RECONCILED:
                # Section Reconciled - Primary v/s External
                if type_process == constantes.OPTION_REPORTS_ALL or type_process == 'primary':
                    data = {
                        'collection': settings.MONGO_COLLECTION_DATA_RECONCILED,
                        'Filter': {
                            f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': item['_id'],
                            'type_process': 'primary'
                        },
                        'Pagination': {
                            'offset': int(offset),
                            'limit': int(limit)
                        }
                    }
                    mongodb = MongoAPI(data)
                    reconciled = mongodb.read_with_pagination(data)

                    data = {
                        'collection': settings.MONGO_COLLECTION_DATA_TOTAL_RECONCILED,
                        'Filter': {
                            f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': item['_id'],
                            'type_process': 'primary'
                        }
                    }
                    mongodb = MongoAPI(data)
                    reconciled_total = mongodb.read()

                    process_conciliation = {
                        'reconciled': {
                            'primary': {
                                'data': reconciled.get('data'),
                                'rows': reconciled.get('total'),
                                'limit': int(limit),
                                'act': int(pag),
                                'total': 0 if len(reconciled_total) == 0 else
                                int(reconciled_total[0]['total_reconciled'])
                            }
                        }
                    }

                # Section Reconciled - External v/s Primary
                if type_process == constantes.OPTION_REPORTS_ALL or type_process == 'secondary':
                    data = {
                        'collection': settings.MONGO_COLLECTION_DATA_RECONCILED,
                        'Filter': {
                            f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': item['_id'],
                            'type_process': 'secondary'
                        },
                        'Pagination': {
                            'offset': int(offset),
                            'limit': int(limit)
                        }
                    }
                    mongodb = MongoAPI(data)
                    reconciled = mongodb.read_with_pagination(data)

                    data = {
                        'collection': settings.MONGO_COLLECTION_DATA_TOTAL_RECONCILED,
                        'Filter': {
                            f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': item['_id'],
                            'type_process': 'secondary'
                        }
                    }
                    mongodb = MongoAPI(data)
                    reconciled_total = mongodb.read()

                    process_conciliation['reconciled']['secondary'] = {
                        'data': reconciled.get('data'),
                        'rows': reconciled.get('total'),
                        'limit': int(limit),
                        'act': int(pag),
                        'total': 0 if len(reconciled_total) == 0 else int(reconciled_total[0]['total_reconciled'])
                    }

            if report == constantes.OPTION_REPORTS_ALL or report == constantes.OPTION_REPORTS_UNRECONCILED:
                # Section Unreconciled - Primary v/s Secondary
                if type_process == constantes.OPTION_REPORTS_ALL or type_process == 'primary':
                    data = {
                        'collection': settings.MONGO_COLLECTION_DATA_UNRECONCILED,
                        'Filter': {
                            f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': item['_id'],
                            'type_process': 'primary'
                        },
                        'Pagination': {
                            'offset': int(offset),
                            'limit': int(limit)
                        }
                    }
                    mongodb = MongoAPI(data)
                    unreconciled = mongodb.read_with_pagination(data)

                    data = {
                        'collection': settings.MONGO_COLLECTION_DATA_TOTAL_UNRECONCILED,
                        'Filter': {
                            f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': item['_id'],
                            'type_process': 'primary'
                        },
                        'Pagination': {
                            'offset': int(offset),
                            'limit': int(limit)
                        }
                    }
                    mongodb = MongoAPI(data)
                    unreconciled_total = mongodb.read()

                    process_conciliation['unreconciled'] = {
                        'primary': {
                            'data': unreconciled.get('data'),
                            'rows': unreconciled.get('total'),
                            'limit': int(limit),
                            'act': int(pag),
                            'total': 0 if len(unreconciled_total) == 0 else
                            int(unreconciled_total[0]['total_unreconciled'])
                        }
                    }

                # Section Unreconciled - Secondary v/s Primary
                if type_process == constantes.OPTION_REPORTS_ALL or type_process == 'secondary':
                    data = {
                        'collection': settings.MONGO_COLLECTION_DATA_UNRECONCILED,
                        'Filter': {
                            f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': item['_id'],
                            'type_process': 'secondary'
                        },
                        'Pagination': {
                            'offset': int(offset),
                            'limit': int(limit)
                        }
                    }
                    mongodb = MongoAPI(data)
                    unreconciled = mongodb.read_with_pagination(data)

                    data = {
                        'collection': settings.MONGO_COLLECTION_DATA_TOTAL_UNRECONCILED,
                        'Filter': {
                            f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': item['_id'],
                            'type_process': 'secondary'
                        },
                        'Pagination': {
                            'offset': int(offset),
                            'limit': int(limit)
                        }
                    }
                    mongodb = MongoAPI(data)
                    unreconciled_total = mongodb.read()

                    process_conciliation['unreconciled']['secondary'] = {
                        'data': unreconciled.get('data'),
                        'rows': unreconciled.get('total'),
                        'limit': int(limit),
                        'act': int(pag),
                        'total': 0 if len(unreconciled_total) == 0 else int(unreconciled_total[0]['total_unreconciled'])
                    }

            if report == constantes.OPTION_REPORTS_ALL or report == constantes.OPTION_REPORTS_DUPLICATED:
                # Section Duplicated - Primary v/s Secondary
                if type_process == constantes.OPTION_REPORTS_ALL or type_process == 'primary':
                    data = {
                        'collection': settings.MONGO_COLLECTION_DATA_DUPLICATES,
                        'Filter': {
                            f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': item['_id'],
                            'type_process': 'primary'
                        },
                        'Pagination': {
                            'offset': int(offset),
                            'limit': int(limit)
                        }
                    }
                    mongodb = MongoAPI(data)
                    duplicated = mongodb.read_with_pagination(data)

                    data = {
                        'collection': settings.MONGO_COLLECTION_DATA_TOTAL_DUPLICATES,
                        'Filter': {
                            f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': item['_id'],
                            'type_process': 'primary'
                        }
                    }
                    mongodb = MongoAPI(data)
                    duplicated_total = mongodb.read()

                    process_conciliation['duplicated'] = {
                        'primary': {
                            'data': duplicated.get('data'),
                            'rows': duplicated.get('total'),
                            'limit': int(limit),
                            'act': int(pag),
                            'total': 0 if len(duplicated_total) == 0 else int(duplicated_total[0]['total_duplicated'])
                        }
                    }

                # Section Duplicated - Secondary v/s Primary
                if type_process == constantes.OPTION_REPORTS_ALL or type_process == 'secondary':
                    data = {
                        'collection': settings.MONGO_COLLECTION_DATA_DUPLICATES,
                        'Filter': {
                            f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': item['_id'],
                            'type_process': 'secondary'
                        },
                        'Pagination': {
                            'offset': int(offset),
                            'limit': int(limit)
                        }
                    }
                    mongodb = MongoAPI(data)
                    duplicated = mongodb.read_with_pagination(data)

                    data = {
                        'collection': settings.MONGO_COLLECTION_DATA_TOTAL_DUPLICATES,
                        'Filter': {
                            f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': item['_id'],
                            'type_process': 'secondary'
                        }
                    }
                    mongodb = MongoAPI(data)
                    duplicated_total = mongodb.read()

                    process_conciliation['duplicated']['secondary'] = {
                        'data': duplicated.get('data'),
                        'rows': duplicated.get('total'),
                        'limit': int(limit),
                        'act': int(pag),
                        'total': 0 if len(duplicated_total) == 0 else int(duplicated_total[0]['total_duplicated'])
                    }
            # Se genera mensaje de respuesta
            response = process_conciliation
    except Exception as e:
        log.exception(e)
        response = get_message_error(e)
    return response


def get_rule_not_selected(cid: str, json_data: dict):
    return detail_conf_reconciled(cid, int(json_data.get('year')), int(json_data.get('month')), json_data.get('id'))


def detail_conf_reconciled(cid: str, year: int, month: int, pid: str = ''):
    response = {}
    data = {
        'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_CNF,
        'Filter': {
            '_id': ObjectId(pid),
            f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': cid,
            'year': int(year),
            'month': int(month)
        }
    }
    mongodb = MongoAPI(data)
    cnf_reconciled = mongodb.read()
    if len(cnf_reconciled) > 0:
        for cnf in cnf_reconciled:
            response = {
                f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': cid,
                'year': int(year),
                'month': int(month),
                'config_id': cnf[f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id'],
                'user_id': cnf['user_id'],
                'state': cnf['state'],
                'id': cnf['_id'],
                'rules': get_all_config_rules_by_partner(cid, int(year), int(month), pid)
            }

            if cnf[f'{settings.MONGO_COLLECTION_CONFIG_RULES}_id'] != '':
                response['ruleSelected'] = get_all_selected(cid, int(year), int(month), pid)
            else:
                response['ruleSelected'] = []
    else:
        response = {}

    return response


def download_report_by_type(cid: str, year: int, month: int, report: str, type_process: str):
    data_report = []
    data = {
        'collection': settings.MONGO_COLLECTION_PROC_RECONCILED_CNF,
        'Filter': {
            f'{settings.MONGO_COLLECTION_UPLOAD_FILE_PARTNER_ID}': cid,
            'year': int(year),
            'month': int(month)
        }
    }
    mongodb = MongoAPI(data)
    cnf_processes = mongodb.read()
    for cnf_process in cnf_processes:
        if report == constantes.OPTION_REPORTS_RECONCILED:
            # Section Reconciled
            data = {
                'collection': settings.MONGO_COLLECTION_DATA_RECONCILED,
                'Filter': {
                    f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': cnf_process['_id'],
                    'type_process': type_process
                }
            }
            mongodb = MongoAPI(data)
            data_report = mongodb.read()

        if report == constantes.OPTION_REPORTS_ALL or report == constantes.OPTION_REPORTS_UNRECONCILED:
            # Section Unreconciled
            data = {
                'collection': settings.MONGO_COLLECTION_DATA_UNRECONCILED,
                'Filter': {
                    f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': cnf_process['_id'],
                    'type_process': type_process
                }
            }
            mongodb = MongoAPI(data)
            data_report = mongodb.read()

        if report == constantes.OPTION_REPORTS_ALL or report == constantes.OPTION_REPORTS_DUPLICATED:
            # Section Duplicated
            data = {
                'collection': settings.MONGO_COLLECTION_DATA_DUPLICATES,
                'Filter': {
                    f'{settings.MONGO_COLLECTION_PROC_RECONCILED_CNF}_id': cnf_process['_id'],
                    'type_process': type_process
                }
            }
            mongodb = MongoAPI(data)
            data_report = mongodb.read()

        if len(data_report) > 0:
            docs = pd.DataFrame(list(data_report))
            return docs


#####################################
#    Definición Métodos Privados
#####################################
def __create_upload_file(
        time_process: str,
        filename: str,
        ext: str,
        type_data: str,
        year: int,
        month: int):
    """
    Carga Configuración Archivos
    :param time_process:
    :param filename:
    :param ext:
    :param type_data:
    :param year:
    :param month:
    :return:
    """
    data = {
        'collection': settings.MONGO_COLLECTION_UPLOAD_FILE,
        'Document': {
            'year': int(year),
            'month': int(month),
            'filename': filename,
            'extension': ext,
            'file_processed': False,
            'type': type_data,
            'created_at': time_process
        },
        'Filter': {
            'year': int(year),
            'month': int(month),
            'filename': filename,
            'extension': ext
        },
        'DataToBeUpdated': {
            'file_processed': False,
            'date_upload': time_process,
            'updated_at': time_process
        }
    }

    mongodb = MongoAPI(data)
    return mongodb.write(data)


def __get_state_config_reconciled(state: str):
    if state == 'config':
        return constantes.STATE_CONFIG_RECONCILED
    elif state == 'pending':
        return constantes.STATE_CONFIG_PENDING
    elif state == 'executed':
        return constantes.STATE_CONFIG_EXECUTED
    else:
        return constantes.STATE_CONFIG_IN_PROCESS


def __eliminar_campo(diccionarios, campo):
    if not diccionarios:  # Verificar si la lista está vacía
        return []

    return list(map(lambda d: {key: value for key, value in d.items() if key != campo}, diccionarios))

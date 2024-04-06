import calendar
import json
import logging
import os
from datetime import datetime

from bson import ObjectId
from cryptography.fernet import Fernet
from flask import jsonify, make_response
from flask_bcrypt import generate_password_hash, check_password_hash

from ..config import settings

log = logging.getLogger(__name__)


def empty_result():
    return []


def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


def cast_id_mongo(id_mongo):
    return str(id_mongo)


def get_uuid():
    return cast_id_mongo(ObjectId())


def get_datetime():
    date_new_format = "%d-%m-%Y %H:%M:%S"
    return datetime.now().strftime(date_new_format)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.FLASK_ALLOWED_EXTENSIONS


def password(pwd: str):
    log_rounds = settings.BCRYPT_LOG_ROUNDS
    hash_bytes = generate_password_hash(pwd, log_rounds)
    return hash_bytes.decode("utf-8")


def check_password(pwd_hash, pwd):
    return check_password_hash(pwd_hash, pwd)


def get_mime_type_application(type_extension: str):
    if type_extension == 'csv':
        return "text/csv"
    elif type_extension == 'xls' or type_extension == 'xlsx':
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def get_message_error(err):
    return make_response(jsonify({
        "msg": f"Ah ocurrido un error: {err}"
    }), 400)


def get_message_success(msg):
    return make_response(jsonify({
        "msg": f"{msg}"
    }), 200)


def get_start_end_day_month(month, year):
    start_day = 1
    end_day = calendar.monthrange(year, month)[1]
    return start_day, end_day


# Messages will be serialized as JSON
def serializer(message):
    return json.dumps(message).encode('utf-8')


def extract_data_line(data: str, pos_ini=None, total=None):
    if pos_ini and total:
        return data[pos_ini:total]
    elif pos_ini:
        return data[pos_ini:]
    else:
        return data[:total]


def get_value_env(v, enc=False):
    # Generation of a key
    # key = Fernet.generate_key()
    if enc:
        cipher_suite = Fernet(bytes(os.environ['OPTIDATA_KEY'], "utf8"))

        response = cipher_suite.decrypt(v)
        return response.decode()

    return v


class DateTimeEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime):
            return str(z)
        else:
            return super().default(z)

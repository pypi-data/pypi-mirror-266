import logging
from flask import make_response
from flask_restx import Api

from ..config import settings
from ..config.error_handling import AppErrorBaseClass, ObjectNotFound

log = logging.getLogger(__name__)
authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-Access-Token',
        'description': "Type in the *'Value'* input box below: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
    }
}
api = Api(
    authorizations=authorizations,
    security='Bearer',
    title='API Motor Conciliación',
    version=f'1.0 - Release({settings.APP_VERSION})',
    description='API Backend para Motor Conciliación con JWT-Based Authentication',
    prefix=settings.RESTPLUS_API_VERSION,
    license='MIT',
    contact='Gonzalo Ariel Torres Moya',
    contact_url='mailto:gtorres@optimisa.cl',
    contact_email='gtorres@optimisa.cl',
    ordered=False,
    catch_all_404s=True,
    default_mediatype='application/json'
)


@api.errorhandler
def default_error_handler():
    message = 'An unhandled exception occurred.'
    log.exception(message)
    if not settings.FLASK_DEBUG:
        return make_response({'message': message}, 500)


@api.errorhandler(AppErrorBaseClass)
def handle_app_base_error(e):
    return make_response({'msg': str(e)}, 500)


@api.errorhandler(ObjectNotFound)
def handle_object_not_found_error(e):
    return make_response({'msg': str(e)}, 404)


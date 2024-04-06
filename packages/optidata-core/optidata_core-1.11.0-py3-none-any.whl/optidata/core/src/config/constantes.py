RESPONSE_ARGUMENT_INVALID = 'Argumento inválido.'
RESPONSE_MAPPING_KEY_ERROR = 'Error en parámetro ingresado'
RESPONSE_NOT_AUTHORIZED = 'No autorizado'
RESPONSE_SUCCESS = 'Respuesta obtenida exitosamente.'
RESPONSE_ERROR = 'Ah ocurrido un error al tratar de obtener la respuesta del servicio.'
RESPONSE_CREATE_SUCCESS = 'Creación exitosa'
RESPONSE_CREATE_ERROR = 'Ah ocurrido un error al tratar de crear el registro.'
RESPONSE_UPDATE_SUCCESS = 'Actualización exitosa'
RESPONSE_UPDATE_ERROR = 'Ah ocurrido un error al tratar de actualizar el registro.'
RESPONSE_DELETE_SUCCESS = 'Eliminación exitosa'
RESPONSE_DELETE_ERROR = 'Ah ocurrido un error al tratar de eliminar el registro.'
RESPONSE_VALID_TOKEN_IS_MISSING = 'No se tiene un token válido.'
RESPONSE_TOKEN_IS_INVALID = 'El token es inválido'
RESPONSE_DATA_EXISTS = 'Los datos ingresados ya existen'
RESPONSE_DATA_NOT_EXISTS = 'Los datos ingresados no existen'
RESPONSE_SUCCESS_UPLOAD = 'Archivo subido exitosamente.'
RESPONSE_ERROR_UPLOAD = 'Ah ocurrido un error al tratar de subir el archivo'
RESPONSE_NOT_SELECT_FILE_UPLOAD = 'No ha seleccionado un archivo para subir'
RESPONSE_EMPTY_SELECT_FILE_UPLOAD = 'El archivo seleccionado está vacío'
RESPONSE_NOT_PART_FILE_UPLOAD = 'No hay parte de archivo en la solicitud'
RESPONSE_NOT_SETTING_TYPE_FILE_UPLOAD = 'No ha indicado el parámetro type en la solicitud'
RESPONSE_EMPTY_SETTING_TYPE_FILE_UPLOAD = 'El valor del parámetro type non puede ser nulo o vacío'

# Login
LOGIN_API_DESCRIPTION = 'Acceso al Sistema'
LOGIN_API_ENDPOINT = 'login'
LOGIN_ERROR = 'No se puede verificar'
RESPONSE_LOGIN_INVALID = 'Login inválido'
RESPONSE_LOGIN_USER_PWD_INVALID = 'Usuario y Password incorrectos.'

# Register
REGISTER_API_DESCRIPTION = 'Registro de Usuario'
REGISTER_API_ENDPOINT = 'register'
REGISTER_ERROR = 'No se puede verificar'

# Rol
ROLE_API_DESCRIPTION = 'Administración de Roles'
ROLE_API_ENDPOINT = 'auth/role'
ROLE_DESCRIPTION_ID = 'Identificador del Rol'

# Usuario
USER_API_DESCRIPTION = 'Administración de Usuarios'
USER_API_ENDPOINT = 'auth/user'
USER_DESCRIPTION_ID = 'Identificador del Usuario'

# Socio
PARTNER_API_DESCRIPTION = 'Administración de Socios'
PARTNER_API_ENDPOINT = 'auth/partner'
PARTNER_DESCRIPTION_ID = 'Identificador del Socio'

# Conciliación
CONCILIATION_API_DESCRIPTION = 'Conciliación'
CONCILIATION_API_ENDPOINT = 'auth/conciliation'
CONCILIATION_DESCRIPTION_ID = 'Identificador de la Conciliación'

# Tipos de Ciclo
TYPE_CYCLES_API_DESCRIPTION = 'Administración de Tipos de Ciclo'
TYPE_CYCLES_API_ENDPOINT = 'auth/type-cycles'
TYPE_CYCLES_DESCRIPTION_ID = 'Identificador del Tipo Ciclo'

# Ciclo
CYCLES_API_DESCRIPTION = 'Ciclo'
CYCLES_API_ENDPOINT = 'auth/cycles'
CYCLES_DESCRIPTION_ID = 'Identificador del Ciclo'

# Endpoints API
PETITION_API_ENDPOINT = 'auth/petitions'
PETITION_API_DESCRIPTION = 'Peticiones Kafka'

# Reglas Conciliación
CONFIG_RULES_API_ENDPOINT = 'auth/config'
CONFIG_RULES_API_DESCRIPTION = 'Configuración de Reglas para la Conciliación'
CONFIG_RULES_DESCRIPTION_ID = 'Identificador de la Configuración'
CONFIG_RULES_YEAR = 'Año asociado al periodo a ejecutar la Conciliación'
CONFIG_RULES_MONTH = 'Mes asociado al periodo a ejecutar la Conciliación'

# Estado de la configuración de la Conciliación
STATE_CONFIG_PENDING = 'Creada'
STATE_CONFIG_RECONCILED = 'Configurada'
STATE_CONFIG_EXECUTED = 'Ejecutada'
STATE_CONFIG_IN_PROCESS = 'En Ejecución'

CODE_STATE_CONFIG_PENDING = 'pending'
CODE_STATE_CONFIG_RECONCILED = 'config'
CODE_STATE_CONFIG_EXECUTED = 'executed'
CODE_STATE_CONFIG_IN_PROCESS = 'in-process'

# Opciones de Reportes
OPTIONS_REPORT = 'Opción para emisión de Reportes (Conciliación / No Conciliación / Duplicados)'
OPTIONS_LIMIT = 'Corresponde a la cantidad de datos a entregar'
OPTIONS_OFFSET = 'Corresponde a el valor desde donde se inicia la búsqueda del item en la consulta'
OPTIONS_REPORT_OPC = ('Corresponde a que reporte se desea obtener'
                      ', los que pueden ser Conciliados, No Conciliados, Duplicados o Todos')
OPTIONS_ACT = 'Corresponde a la pagina actual'
OPTIONS_TYPE = 'Corresponde al tipo de reporte a descargar (CSV, XLSX)'
OPTIONS_TYPE_PROCESS = 'Corresponde al tipo de proceso del reporte (Primario / Externo)'
OPTION_REPORTS_ALL = 'all'
OPTION_REPORTS_RECONCILED = 'reconciled'
OPTION_REPORTS_UNRECONCILED = 'unreconciled'
OPTION_REPORTS_DUPLICATED = 'duplicated'

# Constantes Globales
EMPTY = ''
H5_FILE = '.h5'
MONGO_BATCH_SIZE = 100000

# CORS Configuration
CORS_ALLOW_ORIGIN = "*,*"
CORS_EXPOSE_HEADERS = "*,*"
CORS_ALLOW_HEADERS = "content-type,Access-Control-Allow-Origin,*"

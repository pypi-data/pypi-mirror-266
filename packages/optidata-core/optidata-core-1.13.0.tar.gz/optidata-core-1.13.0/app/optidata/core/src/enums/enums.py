from enum import Enum, unique


@unique
class DataTypeEnum(Enum):
    STRING = 'str'
    DATE = 'datetime'
    INTEGER = 'int'
    FLOAT = 'float'


@unique
class ReconciledStateEnum(Enum):
    RECONCILED_INIT = 'launched'
    RECONCILED_IN_PROCESS = 'in-process'
    RECONCILED_TERMINATE_OK = 'terminate-success'
    RECONCILED_TERMINATE_NOK = 'terminate-error'


@unique
class EventsLogsEnum(Enum):
    EVENT_ERROR = 'error'
    EVENT_INFO = 'info'

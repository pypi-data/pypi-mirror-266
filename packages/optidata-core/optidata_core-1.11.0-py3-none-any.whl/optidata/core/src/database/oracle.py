import logging
import platform

import oracledb
from sqlalchemy import create_engine, NullPool
from sqlalchemy.orm import sessionmaker

from ..config import settings

log = logging.getLogger(__name__)

d = None  # default suitable for Linux
f = None
if platform.system() == "Darwin" and platform.machine() == "x86_64":  # macOS
    d = "linux"
    f = '.'
elif platform.system() == "Windows":
    d = "win"
    f = 'd:'
oracledb.init_oracle_client(lib_dir=f'{f}/oracle_client/{d}')


class OracleAPI:
    def __init__(self):
        cp = oracledb.ConnectParams(
            host=f"{settings.ORACLE_HOST}", port=int(settings.ORACLE_PORT), sid=f"{settings.ORACLE_SERVICE_NAME}"
        )
        dsn = cp.get_connect_string()

        self.pool = oracledb.create_pool(
            user=settings.ORACLE_USERNAME,
            password=settings.ORACLE_PASSWORD,
            dsn=dsn,
            min=1,
            max=4,
            increment=1,
            disable_oob=True,
            ping_interval=2,
            getmode=oracledb.POOL_GETMODE_WAIT
        )

        self.engine = create_engine(
            "oracle+oracledb://",
            creator=self.pool.acquire,
            poolclass=NullPool
        )

        # Create a session to the database
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def read(self, sql):
        try:
            return self.session.execute(sql).fetchone()
        except Exception as ex:
            log.exception(ex)
            return None

    def all(self, sql):
        try:
            return self.session.execute(sql).fetchall()
        except Exception as ex:
            log.exception(ex)
            return None

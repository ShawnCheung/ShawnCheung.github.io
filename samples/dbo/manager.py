__all__ = [
    "DBManager",
]

import os
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from config import Configuration
from logger import logger

from dbo import ModelDBO


class DBManager(object):
    _engine: Engine = None

    model: ModelDBO = None

    def __init__(self) -> None:
        pass

    @property
    def engine(self):
        return self._engine

    def get_session(self, *args, **kwargs) -> Session:
        return Session(self._engine, *args, **kwargs)

    @classmethod
    def init(cls):
        """
        """
        # logger = SystemLogger.get_logger(cls.__class__)
        config = Configuration.get_config()

        # Get config by subscript
        db_type = config.get("database.type", default="local")
        if db_type == "local":
            cls._engine = DBManager.init_local_engine()
        elif db_type == "mysql":
            try:
                cls._engine = DBManager.init_mysql_engine()
            except Exception as e:
                logger.exception(
                    f"Failed to initialize MySQL database due to: {e}")
                logger.warning(
                    "Initializing MySQL database failed, rollback to local SQLite database.")
                cls._engine = DBManager.init_local_engine()
        elif db_type == "rds":
            # NOTE: We won't fallback to local database here, as we only use RDS in TCC.
            cls._engine = DBManager.init_byted_rds_engine()
        else:
            logger.warning(
                f"Not supported database type '{db_type}', rollback to local SQLite database.")
            cls._engine = DBManager.init_local_engine()

        cls._init_tables()

    @classmethod
    def get_instance(cls):
        """ Get a global DBManager instance.
        """
        if cls._engine is None:
            raise Exception(
                "DBManager has not be initialized, call 'DBManager.init()' first.")
        return cls()

    @classmethod
    def dispose(cls, close=True) -> None:
        """ For multiprocessing cases.
        """
        cls._engine.dispose(close)

    @classmethod
    def _init_tables(cls):
        cls.model = ModelDBO(engine=cls._engine)

    @staticmethod
    def init_local_engine():
        """ Initialize a SQLite database.
        """
        config = Configuration.get_config()
        path = config.get("database.local.path", default=os.path.join("sqlite/model.db"))  # type: str

        # If the file path is relative, we'll place it to the data directory.
        if not path.startswith("/"):
            data_dir = config.get_data_dir()
            path = os.path.join(data_dir, path)

        # Create all intermediate directories to the sqlite file
        db_dir_path = os.path.dirname(path)
        if not os.path.exists(db_dir_path):
            os.makedirs(db_dir_path, exist_ok=True)

        url = "sqlite:///{}?check_same_thread=False".format(path)
        # TODO: confirm isolation level setting
        return DBManager.init_engine(url=url, isolation_level=None)

    @staticmethod
    def init_mysql_engine():
        # TODO: implement this with MySQL database on TDVM.
        raise NotImplementedError

    @staticmethod
    def init_byted_rds_engine():
        from bytedmysql import sqlalchemy_init
        sqlalchemy_init()

        config = Configuration.get_config()
        rds_psm = config.get("database.rds.psm")
        if config.get("core.region") != "boe":
            rds_psm = rds_psm + ".service.lf"
        url = "mysql+pymysql://:@/?charset=utf8mb4&&db_psm={}".format(rds_psm)

        rds_args = config.get("database.rds.args", default={})
        if rds_args is None:
            rds_args = {}
        rds_args = dict(rds_args)
        return DBManager.init_engine(url=url, **rds_args)

    @staticmethod
    def init_engine(url: str, **kwargs) -> Engine:
        logger.info(f"* Connect to database: {url}")
        return create_engine(url=url, **kwargs)

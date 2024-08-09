from sqlalchemy.orm import Session

from core.setup import DatabaseSetup


class DBSession:
    def __init__(self) -> None:
        self._db_init = DatabaseSetup()
        self._db = self._db_init.get_session()

    def __enter__(self) -> Session:
        return self._db()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._db().close()

from .db_common import (
    DB_ENGINE, DB_NAME, DB_USER, DB_PWD, DB_HOST, DB_PORT,
)
from .db_pomes import (
    db_connect, db_exists, db_select_one, db_select_all,
    db_update, db_delete, db_insert, db_bulk_insert,
    db_call_function, db_call_procedure,
)

__all__ = [
    # db_common
    "DB_ENGINE", "DB_NAME", "DB_USER", "DB_PWD", "DB_HOST", "DB_PORT",
    # db_pomes
    "db_connect", "db_exists", "db_select_one", "db_select_all",
    "db_update", "db_delete", "db_insert", "db_bulk_insert",
    "db_call_function", "db_call_procedure",
]

from importlib.metadata import version
__version__ = version("pypomes_db")
__version_info__ = tuple(int(i) for i in __version__.split(".") if i.isdigit())

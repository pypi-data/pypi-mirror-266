from logging import Logger
from oracledb import Connection, connect

from .db_common import (
    DB_NAME, DB_HOST, DB_PORT, DB_PWD, DB_USER,
    _assert_query_quota, _db_log, _db_except_msg
)

# TODO: db_bulk_insert, db_exec_stored_procedure


def db_connect(errors: list[str], logger: Logger = None) -> Connection:
    """
    Obtain and return a connection to the database, or *None* if the connection cannot be obtained.

    :param errors: incidental error messages
    :param logger: optional logger
    :return: the connection to the database
    """
    # initialize the return variable
    result: Connection | None = None

    # obtain a connection to the database
    err_msg: str | None = None
    try:
        result = connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PWD
        )
    except Exception as e:
        err_msg = _db_except_msg(e)

    # log the results
    _db_log(errors, err_msg, logger, f"Connected to '{DB_NAME}'")

    return result


def db_select_all(errors: list[str] | None, sel_stmt: str,  where_vals: tuple,
                  require_min: int = None, require_max: int = None, logger: Logger = None) -> list[tuple]:
    """
    Search the database and return all tuples that satisfy the *sel_stmt* search command.

    The command can optionally contain search criteria, with respective values given
    in *where_vals*. The list of values for an attribute with the *IN* clause must be contained
    in a specific tuple. If not positive integers, *require_min* and *require_max* are ignored.
    If the search is empty, an empty list is returned.

    :param errors: incidental error messages
    :param sel_stmt: SELECT command for the search
    :param where_vals: the values to be associated with the search criteria
    :param require_min: optionally defines the minimum number of tuples to be returned
    :param require_max: optionally defines the maximum number of tuples to be returned
    :param logger: optional logger
    :return: list of tuples containing the search result, or [] if the search is empty
    """
    # initialize the return variable
    result: list[tuple] = []

    if isinstance(require_max, int) and require_max > 0:
        sel_stmt: str = f"{sel_stmt} FETCH NEXT {require_max} ROWS ONLY"

    err_msg: str | None = None
    try:
        # obtain the connection
        with connect(host=DB_HOST,
                     port=DB_PORT,
                     user=DB_USER,
                     password=DB_PWD) as conn:
            # make sure the connection is not in autocommit mode
            conn.autocommit = False

            # obtain a cursor and perform the operation
            with conn.cursor() as cursor:
                # execute the query
                cursor.execute(statement=sel_stmt,
                               parameters=where_vals)
                # obtain the number of tuples returned
                count: int = cursor.rowcount

                # has the query quota been satisfied ?
                if _assert_query_quota(errors, sel_stmt, where_vals, count, require_min, require_max):
                    # yes, retrieve the returned tuples
                    rows: list = cursor.fetchall()
                    result = [tuple(row) for row in rows]
            # commit the transaction
            conn.commit()
    except Exception as e:
        err_msg = _db_except_msg(e)

    # log the results
    _db_log(errors, err_msg, logger, sel_stmt, where_vals)

    return result


def db_bulk_insert(errors: list[str] | None, insert_stmt: str,
                   insert_vals: list[tuple], logger: Logger = None) -> int:
    """
    Insert the tuples, with values defined in *insert_vals*, into the database.

    :param errors: incidental error messages
    :param insert_stmt: the INSERT command
    :param insert_vals: the list of values to be inserted
    :param logger: optional logger
    :return: the number of inserted tuples, or None if an error occurred
    """
    # initialize the return variable
    result: int | None = None

    err_msg: str | None = None
    try:
        # obtain the connection
        with connect(host=DB_HOST,
                     port=DB_PORT,
                     user=DB_USER,
                     password=DB_PWD) as conn:
            # make sure the connection is not in autocommit mode
            conn.autocommit = False

            # obtain a cursor and perform the operation
            with conn.cursor() as cursor:
                try:
                    cursor.executemany(statement=insert_stmt,
                                       parameters=insert_vals)
                    result = len(insert_vals)
                except Exception:
                    conn.rollback()
                    raise
            conn.commit()
    except Exception as e:
        err_msg = _db_except_msg(e)

    # log the results
    _db_log(errors, err_msg, logger, insert_stmt, insert_vals[0])

    return result


# TODO: see https://python-oracledb.readthedocs.io/en/latest/user_guide/plsql_execution.html
def db_call_function(errors: list[str] | None, func_name: str,
                     func_vals: tuple, logger: Logger = None) -> list[tuple]:
    """
    Execute the stored function *func_name* in the database, with the parameters given in *func_vals*.

    :param errors: incidental error messages
    :param func_name: name of the stored function
    :param func_vals: parameters for the stored function
    :param logger: optional logger
    :return: the data returned by the function
    """
    # initialize the return variable
    result: list[tuple] = []

    # execute the stored procedure
    err_msg: str | None = None
    try:
        # obtain a connection
        with connect(host=DB_HOST,
                     port=DB_PORT,
                     user=DB_USER,
                     password=DB_PWD) as conn:
            # make sure the connection is not in autocommit mode
            conn.autocommit = False
            # obtain a cursor and perform the operation
            with conn.cursor() as cursor:
                cursor.callproc(name=func_name,
                                parameters=func_vals)
                # yes, retrieve the returned tuples
                result = list(cursor)
            # commit the transaction
            conn.commit()
    except Exception as e:
        err_msg = _db_except_msg(e)

    # log the results
    _db_log(errors, err_msg, logger, func_name, func_vals)

    return result


# TODO: see https://python-oracledb.readthedocs.io/en/latest/user_guide/plsql_execution.html
def db_call_procedure(errors: list[str] | None, proc_name: str,
                      proc_vals: tuple, logger: Logger = None) -> list[tuple]:
    """
    Execute the stored procedure *proc_name* in the database, with the parameters given in *proc_vals*.

    :param errors: incidental error messages
    :param proc_name: name of the stored procedure
    :param proc_vals: parameters for the stored procedure
    :param logger: optional logger
    :return: the data returned by the procedure
    """
    # initialize the return variable
    result: list[tuple] = []

    # execute the stored procedure
    err_msg: str | None = None
    try:
        # obtain a connection
        with connect(host=DB_HOST,
                     port=DB_PORT,
                     user=DB_USER,
                     password=DB_PWD) as conn:
            # make sure the connection is not in autocommit mode
            conn.autocommit = False
            # obtain a cursor and perform the operation
            with conn.cursor() as cursor:
                cursor.callproc(name=proc_name,
                                parameters=proc_vals)

                # retrieve the returned tuples
                result = list(cursor)
            # commit the transaction
            conn.commit()
    except Exception as e:
        err_msg = _db_except_msg(e)

    # log the results
    _db_log(errors, err_msg, logger, proc_name, proc_vals)

    return result


def db_modify(errors: list[str] | None, modify_stmt: str, bind_vals: tuple | list[tuple], logger: Logger) -> int:
    """
    Modify the database, inserting, updating or deleting tuples, according to the *modify_stmt* command definitions.

    The values for this modification, followed by the values for selecting tuples are in *bind_vals*.

    :param errors: incidental error messages
    :param modify_stmt: INSERT, UPDATE, or DELETE command
    :param bind_vals: values for database modification, and for tuples selection
    :param logger: optional logger
    :return: the number of inserted, modified, or deleted tuples, ou None if an error occurred
    """
    # initialize the return variable
    result: int | None = None

    err_msg: str | None = None
    try:
        # obtain a connection
        with connect(host=DB_HOST,
                     port=DB_PORT,
                     user=DB_USER,
                     password=DB_PWD) as conn:
            # make sure the connection is not in autocommit mode
            conn.autocommit = False
            # obtain the cursor and execute the operation
            with conn.cursor() as cursor:
                cursor.execute(statement=modify_stmt,
                               parameters=bind_vals)
                result = cursor.rowcount
            # commit the transaction
            conn.commit()
    except Exception as e:
        err_msg = _db_except_msg(e)

    # log the results
    _db_log(errors, err_msg, logger, modify_stmt, bind_vals)

    return result

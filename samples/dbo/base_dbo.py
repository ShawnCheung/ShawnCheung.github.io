__all__ = [
    "BaseDBO",
]

from datetime import datetime
from typing import Any, Dict, Generic, List, TypeVar, Tuple, Optional, Union

from sqlalchemy import delete as _delete, func
from sqlalchemy import select as _select
from sqlalchemy import update as _update
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select, Update, Delete
from tenacity import retry, stop_after_attempt, wait_fixed

# Type Annotation
_TT = TypeVar("_TT", bound=Any)  # Generic type for table
_RT = TypeVar("_RT", bound=Any)  # Generic type for queried rows


def retry_error_callback(retry_state):
    print("retry fails. calling retry_error_callback")


def _map_timestamp(row: List[Any]):
    for r in row:
        if isinstance(r, datetime):
            r = r.isoformat(sep=" ")
        yield r


class BaseDBO(Generic[_TT]):
    _table: _TT

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._table.__table__.create(self._engine, checkfirst=True)

    @property
    def table(self):
        return self._table

    @retry(reraise=True,
           stop=stop_after_attempt(3),
           wait=wait_fixed(0.1),
           retry_error_callback=retry_error_callback
           )
    def insert(self, **columns) -> None:
        """ Insert a new record to the table.
        :params kwargs - Key-value format parameters

        :return None
        """
        # Filter out attributes are not belonging to the table.
        for k in list(columns.keys()):
            if not hasattr(self._table, k):
                del columns[k]

        instance = self._table(**columns)

        with Session(self._engine) as session, session.begin():
            session.add(instance)

    @retry(reraise=True,
           stop=stop_after_attempt(3),
           wait=wait_fixed(0.1),
           retry_error_callback=retry_error_callback
           )
    def delete(self,
               where: Dict[str, Any] = {},
               soft_deletion: bool = True,
               ) -> bool:
        """ Delete a record from the table.
        :params where - The clauses for query
        :params soft_deletion - Flag specifying conduct a soft-deletion or hard-deletion.
        """
        if soft_deletion:
            self.update(fields={"deleted": True},
                        where=where
                        )
            return True

        statement = _delete(self._table)
        statement: Delete = self.where(statement, where, self._table)

        with Session(self._engine) as session, session.begin():
            session.execute(statement)

    @retry(reraise=True,
           stop=stop_after_attempt(3),
           wait=wait_fixed(0.1),
           retry_error_callback=retry_error_callback
           )
    def update(self,
               fields: Dict[str, Any],
               where: Dict[str, Any]
               ) -> bool:
        """ Update a record of the table.
        :params fields - Columns to be updated.
        :params where - Clauses for query.
        """
        statement = _update(self._table)
        statement: Update = self.where(statement, where, self._table)

        # Filter out attributes are not belonging to the table.
        # 同时过滤None值
        for k in list(fields.keys()):
            if not hasattr(self._table, k):
                del fields[k]
            elif fields[k] is None:
                del fields[k]
        statement = statement.values(**fields)

        with Session(self._engine) as session, session.begin():
            session.execute(statement)

    @retry(reraise=True,
           stop=stop_after_attempt(3),
           wait=wait_fixed(0.1),
           retry_error_callback=retry_error_callback
           )
    def count(self, filter_by: Dict[str, Any] = {}) -> int:
        """ Count the number of rows that meets the condition in the table.
        :params where - The clauses for query
        :return The number of rows in the table.
        """
        # statement = _select(self._table)

        # Construct the query statement
        # statement = self.where(statement, where, self._table)

        with Session(self._engine) as session, session.begin():
            return session.query(func.count()).select_from(self._table).filter_by(**filter_by).scalar()

    @retry(reraise=True,
           stop=stop_after_attempt(3),
           wait=wait_fixed(0.1),
           retry_error_callback=retry_error_callback
           )
    def select(self,
               *columns: Optional[List[str]],
               where: Dict[str, Any] = {},
               order_by: Optional[Union[str, List[str]]] = None,
               paging: Optional[Tuple[int, int]] = None,
               ) -> List[Dict[str, Any]]:
        """ Query a table and return rows meet the condition.
        :params columns - Specify wanted columns. None for all columns (eq. SELECT *)
        :params where - Specify the where clauses (Only support equality clauses)
        :params order_by - Specify the column(s) by which results will get ordered. None for no ordering.
        :params paging - Specify the paging info for picking part of rows of the table

        :return A list of queried values.
        """
        column_clauses = []
        if columns:
            for col in columns:
                if hasattr(self._table, col):
                    column_clauses.append(getattr(self._table, col))

        if column_clauses:
            statement = _select(*column_clauses)
        else:
            statement = _select(self._table)

        # Construct the query statement
        statement = self.where(statement, where, self._table)
        statement = self.page(
            statement, page=paging[0], page_size=paging[1]) if paging else statement
        statement = self.order_by(
            statement, order_by, self._table) if order_by else statement

        # Execute the SQL
        with Session(self._engine) as session, session.begin():
            rows = session.execute(statement).all()

            # Unify the return value's format to a dict
            if column_clauses:
                columns = [qc.name for qc in column_clauses]
                result = [dict(zip(columns, _map_timestamp(r))) for r in rows]
            else:
                result = [r[0].to_dict() for r in rows]

        return result

    @retry(reraise=True,
           stop=stop_after_attempt(3),
           wait=wait_fixed(0.1),
           retry_error_callback=retry_error_callback
           )
    def execute(self,
                statement: Union[Select[_RT], Update, Delete],
                ) -> Union[None, List[_RT]]:
        is_select = False

        if isinstance(statement, (Select,)):
            is_select = True

        result = None
        with Session(self._engine) as session, session.begin():
            rows = session.execute(statement)
            if is_select:
                result = rows.all()
        return result

    @staticmethod
    def where(statement: Union[Select[_RT], Update, Delete],
              clauses: Dict[str, Any],
              table,
              ) -> Union[Select[_RT], Update, Delete]:
        """ Filter out some rows based on equality clauses.
        :params statement - The select query statement.
        :params clauses - The where clauses.
        :params table - Specify the table class to be queried.

        :return A new query statement
        """
        for lhv, rhv in clauses.items():
            # lhv: left-hand value, rhv: right-hand value
            if hasattr(table, lhv):
                if type(rhv) is list and len(rhv) == 2 and rhv[0] in ["<=", ">="]:
                    if rhv[0] == "<=":
                        statement = statement.where(
                            getattr(table, lhv) <= rhv[1])
                    elif rhv[1] == ">=":
                        statement = statement.where(
                            getattr(table, lhv) >= rhv[1])
                else:
                    statement = statement.where(getattr(table, lhv) == rhv)  # noqa
        return statement

    @staticmethod
    def order_by(statement: Select,
                 clauses: Union[str, List[str]],
                 table,
                 ) -> Select:
        """ Order the queried results based on clauses.
        :params statement - The select query statement.
        :params clauses - The columns' name used for ordering.
        :params table - Specify the table class to be queried.

        :return A new query statement
        """
        if isinstance(clauses, str):
            clauses = [clauses]

        query_clauses = []
        for c in clauses:
            is_desc = False
            if c.startswith("-"):
                is_desc = True
                c = c[1:]

            if not hasattr(table, c):
                continue

            c = getattr(table, c)
            if is_desc:
                c = c.desc()

            query_clauses.append(c)

        if query_clauses:
            statement = statement.order_by(*query_clauses)

        return statement

    @staticmethod
    def page(statement: Select[_RT],
             page: int = 0,
             page_size: Optional[int] = None,
             ) -> Select[_RT]:
        """ Pick part of rows from the queried table.
        :params statement - The select query statement.
        :params page - The page number.
        :params page_size - The number of rows going to picked.

        :return A new query statement
        """
        if page_size and page > 0:
            statement = statement.offset(
                (page - 1) * page_size).limit(page_size)
        return statement

import pprint
from typing import Any

import pendulum
from masoniteorm.expressions.expressions import QueryExpression
from masoniteorm.query import QueryBuilder


def route_key(key):
    def decorator(cls):
        # Assign the getter and setter functions as a property
        setattr(cls, "__route_model_binding_key__", key)

        # Return the modified class
        return cls

    # Return the inner decorator function
    return decorator


class EnhancedModelTrait:
    @classmethod
    def without_(self, relations: str | list):
        if not isinstance(relations, (str, list)):
            print("cunny hole")
            raise Exception(
                "Argument expects a string or list."
            )
        elif isinstance(relations, str):
            relation = list(relations)
        self.__with__ = [relation for relation in self.__with__ if relation in relations]
        return self

    @classmethod
    def without_withs(self):
        self.__with__ = []
        return self

    @classmethod
    def get_db_type(cls) -> str:
        from config.database import DB
        try:
            return DB.get_connection_details()[cls.__connection__]['driver']
        except TypeError:
            return DB.get_connection_details()[cls.__connection__]

    @classmethod
    def where_date_primitive(cls, data_type: str, column: str, *args: Any):
        initialized_self = cls()
        try:
            operator, value = args
        except ValueError:
            value = args[0]
            operator = "="

        db_driver = cls.get_db_type()
        match db_driver:
            case "mssql":
                value_wrapper = f"'{value}'"
                column_wrapper = f"CAST({column} as {data_type})"
            case "postgres":
                value_wrapper = f"'{value}'"
                column_wrapper = f"CAST('{column}' as {data_type})"
            case _:
                value_wrapper = f"'{value}'"
                column_wrapper = f"{data_type}({column})"

        if operator:
            initialized_self.where_raw(f"{column_wrapper} {operator} {value_wrapper}")
        else:
            initialized_self.where_raw(f"{column_wrapper} {operator} {value_wrapper}")
        return initialized_self

    @classmethod
    def where_date(cls, column: str, *args: Any):
        return cls.where_date_primitive("DATE".lower(), column, *args)

    @classmethod
    def where_time(cls, column: str, *args: Any):
        return cls.where_date_primitive("TIME".lower(), column, *args)


    def with_where_has(cls, relation: str, callback):
        return cls.with_(relation).where_has(relation, callback)


    def where_any(cls, list_of_columns: list[str], operator: str = "=", criterion: Any | None = None):
        if not isinstance(list_of_columns, (list,)):
            return TypeError("Columns should be of type [list]")
        if operator in ["LIKE", "like"]:
            criterion = f"%{criterion}%"
        for column in list_of_columns:
            if "." not in column:
                cls._wheres += (
                    (QueryExpression(column, operator, criterion, keyword="or")),
                )
            else:
                relation, column = column.split(".")
                cls.with_where_has(
                    relation,
                    lambda q: q.where(column, operator, criterion)
                )
        return cls



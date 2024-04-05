from typing import Union

TableName = str
SchemaName = str
DatabaseName = str

ExternalTableKey = Union[
    TableName, tuple[SchemaName, TableName], tuple[DatabaseName, SchemaName, TableName]
]

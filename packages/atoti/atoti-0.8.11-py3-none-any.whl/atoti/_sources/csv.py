from __future__ import annotations

from collections.abc import Mapping, Sequence, Set as AbstractSet
from dataclasses import asdict
from pathlib import Path
from typing import Optional, Protocol, Union

from atoti_core import (
    PYDANTIC_CONFIG,
    Constant,
    DataType,
    TableIdentifier,
    keyword_only_dataclass,
)
from pydantic.dataclasses import dataclass
from typing_extensions import override

from ..client_side_encryption_config import ClientSideEncryptionConfig
from .data_source import DataSource, LoadDataIntoTable
from .to_absolute_path import to_absolute_path


@keyword_only_dataclass
@dataclass(config=PYDANTIC_CONFIG, frozen=True)
class CsvPrivateParameters:
    parser_thread_count: Optional[int] = None
    buffer_size_kb: Optional[int] = None


def create_csv_params(
    path: Union[Path, str],
    /,
    *,
    columns: Union[Mapping[str, str], Sequence[str]],
    separator: Optional[str],
    encoding: str,
    process_quotes: Optional[bool],
    array_separator: Optional[str],
    pattern: Optional[str],
    date_patterns: Mapping[str, str],
    client_side_encryption: Optional[ClientSideEncryptionConfig],
    parser_thread_count: Optional[int],
    buffer_size_kb: Optional[int],
) -> dict[str, object]:
    return {
        "absolutePath": to_absolute_path(path),
        "columns": {} if isinstance(columns, Sequence) else columns,
        "headers": columns if isinstance(columns, Sequence) else [],
        "separator": separator,
        "encoding": encoding,
        "processQuotes": process_quotes,
        "arraySeparator": array_separator,
        "globPattern": pattern,
        "datePatterns": date_patterns,
        "clientSideEncryptionConfig": asdict(client_side_encryption)
        if client_side_encryption is not None
        else None,
        "parserThreads": parser_thread_count,
        "bufferSize": buffer_size_kb,
    }


@keyword_only_dataclass
@dataclass(frozen=True)
class CsvFileFormat:
    process_quotes: bool
    separator: str
    types: Mapping[str, DataType]


class _DiscoverCsvFileFormat(Protocol):
    def __call__(
        self,
        source_params: Mapping[str, object],
        /,
        *,
        keys: AbstractSet[str],
        default_values: Mapping[str, Optional[Constant]],
    ) -> CsvFileFormat: ...


class CsvDataSource(DataSource):
    def __init__(
        self,
        *,
        discover_csv_file_format: _DiscoverCsvFileFormat,
        load_data_into_table: LoadDataIntoTable,
    ) -> None:
        super().__init__(load_data_into_table=load_data_into_table)

        self._discover_csv_file_format = discover_csv_file_format

    @property
    @override
    def key(self) -> str:
        return "CSV"

    def discover_file_format(
        self,
        path: Union[Path, str],
        /,
        *,
        keys: AbstractSet[str],
        separator: Optional[str],
        encoding: str,
        process_quotes: Optional[bool],
        array_separator: Optional[str],
        pattern: Optional[str],
        date_patterns: Mapping[str, str],
        default_values: Mapping[str, Optional[Constant]],
        client_side_encryption: Optional[ClientSideEncryptionConfig],
        columns: Union[Mapping[str, str], Sequence[str]],
        parser_thread_count: Optional[int],
        buffer_size_kb: Optional[int],
    ) -> CsvFileFormat:
        """Infer Table types from a CSV file or directory."""
        source_params = create_csv_params(
            path,
            columns=columns,
            separator=separator,
            encoding=encoding,
            process_quotes=process_quotes,
            array_separator=array_separator,
            pattern=pattern,
            date_patterns=date_patterns,
            client_side_encryption=client_side_encryption,
            parser_thread_count=parser_thread_count,
            buffer_size_kb=buffer_size_kb,
        )
        return self._discover_csv_file_format(
            source_params,
            keys=keys,
            default_values=default_values,
        )

    def load_csv_into_table(
        self,
        identifier: TableIdentifier,
        path: Union[Path, str],
        /,
        *,
        columns: Union[Mapping[str, str], Sequence[str]],
        scenario_name: str,
        separator: Optional[str],
        encoding: str,
        process_quotes: Optional[bool],
        array_separator: Optional[str],
        pattern: Optional[str],
        date_patterns: Mapping[str, str],
        client_side_encryption: Optional[ClientSideEncryptionConfig],
        parser_thread_count: Optional[int],
        buffer_size_kb: Optional[int],
    ) -> None:
        source_params = create_csv_params(
            path,
            columns=columns,
            separator=separator,
            encoding=encoding,
            process_quotes=process_quotes,
            array_separator=array_separator,
            pattern=pattern,
            date_patterns=date_patterns,
            client_side_encryption=client_side_encryption,
            parser_thread_count=parser_thread_count,
            buffer_size_kb=buffer_size_kb,
        )
        self.load_data_into_table(
            identifier,
            source_params,
            scenario_name=scenario_name,
        )

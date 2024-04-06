#  Copyright (c) 2024. ISTMO Center S.A.  All Rights Reserved
#  IBIS is a registered trademark
#
import datetime
import os
from pathlib import Path
from typing import Optional, Dict, Union, Any, List

import dask.dataframe as dd
from pydantic import BaseModel, model_validator, DirectoryPath, FilePath

from ..file_utils import FilePathGenerator
from ..log_utils import Logger
from .config import dataframe_params, dataframe_options
from .sql_model_builder import SqlModelBuilder

logger = Logger(log_dir='./logs/', logger_name=__name__, log_file=f'{__name__}.log')

LOOKUP_SEP = "__"


class ConnectionConfig(BaseModel):
    live: bool = False
    connection_name: str = None
    table: str = None
    model: Any = None

    @model_validator(mode='after')
    def check_model(self):
        if self.connection_name is None:
            raise ValueError('Connection name must be specified')

        if self.live is False:
            if self.model is None:
                raise ValueError('Model must be specified')
            self.table = self.model._meta.db_table
        else:
            # if live is True, then connection_name and table must be specified
            if self.table is None:
                raise ValueError('Table name must be specified')
            self.model = SqlModelBuilder(connection_name=self.connection_name, table=self.table).build_model()

        return self


class QueryConfig(BaseModel):
    use_exclude: bool = False
    n_records: int = 0
    dt_field: Optional[str] = None
    use_dask: bool = False
    as_dask: bool = False

    @model_validator(mode='after')
    def check_n_records(self):
        if self.n_records < 0:
            raise ValueError('Number of records must be non-negative')


class ParamsConfig(BaseModel):
    field_map: Optional[Dict] = None
    legacy_filters: bool = False
    fixed_filters: Dict[str, Union[str, bool, int, float]] = {}
    filters: Dict[str, Union[str, Dict, bool, int, float]] = {}
    df_params: Dict[str, Union[tuple, str, bool, None]] = {}
    df_options: Dict[str, Union[bool, str, None]] = {}
    params: Dict[str, Union[str, bool, int, float, List[Union[str, int, bool, float]]]] = {}

    @model_validator(mode='after')
    def check_params(self):
        if self.params is not None:
            self.parse_params(self.params)
        return self

    def parse_params(self, params, use_parquet=False):
        df_params, df_options, filters = {}, {}, {}
        for k, v in params.items():
            if k in dataframe_params:
                df_params.update({k: v})
            elif k in dataframe_options:
                df_options.update({k: v})
            else:
                filters.update({k: v})
        if not self.fixed_filters:
            self.fixed_filters = filters
        self.filters = {**self.fixed_filters, **filters}
        self.df_params = {**self.df_params, **df_params}
        self.df_options = {**self.df_options, **df_options}
        if self.legacy_filters and not use_parquet:
            self.convert_legacy_filters()

    def convert_legacy_filters(self):
        if not self.legacy_filters or not self.field_map or not self.filters:
            return

        # create a reverse map of the field_map
        reverse_map = {v: k for k, v in self.field_map.items()}

        new_filters = {}
        for filter_field, value in self.filters.items():
            # split the filter_field if LOOKUP_SEP exists
            parts = filter_field.split(LOOKUP_SEP, 1)

            # replace each part with its legacy equivalent if it exists
            new_parts = [reverse_map.get(part, part) for part in parts]

            # join the parts back together and add to the new filters
            new_filter_field = LOOKUP_SEP.join(new_parts)
            new_filters[new_filter_field] = value

        self.filters = new_filters
        return self


class ParquetOptions(BaseModel):
    df_as_dask: bool = False
    use_parquet: bool = False
    save_parquet: bool = False
    load_parquet: bool = False
    parquet_filename: Optional[str] = None
    parquet_storage_path: Optional[DirectoryPath] = None
    parquet_full_path: Optional[FilePath] = None
    parquet_folder_list: Optional[List[str]] = None
    parquet_size_bytes: int = 0
    parquet_max_age_minutes: int = 0
    parquet_is_recent: bool = False
    parquet_start_date: str = None
    parquet_end_date: str = None

    @model_validator(mode='after')
    def check_parquet_params(self):
        if self.use_parquet is False:
            return self
        self.save_parquet = False
        self.load_parquet = False
        if self.parquet_storage_path is None:
            raise ValueError('Parquet storage path must be specified')
        if not os.path.exists(self.parquet_storage_path):
            raise ValueError('Parquet storage path does not exist')
        if self.parquet_filename is not None:
            self.parquet_full_path = self.ensure_file_extension(
                filepath=self.parquet_storage_path / self.parquet_filename, extension='parquet')
            self.parquet_is_recent = self.is_file_recent()
            self.load_parquet = self.parquet_is_recent and self.parquet_full_path.exists()
            self.save_parquet = not self.parquet_is_recent

        if self.parquet_start_date is not None:
            if self.parquet_end_date is None:
                raise ValueError('Parquet end date must be specified if start date is provided')

            start_date = datetime.datetime.strptime(self.parquet_start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(self.parquet_end_date, '%Y-%m-%d')
            if end_date < start_date:
                raise ValueError('Parquet end date must be greater than start date')

            # saving to parquet is disabled when start and end dates are provided, since we will be
            # just loading the parquet files
            self.save_parquet = False
            self.parquet_folder_list = FilePathGenerator(str(self.parquet_storage_path)).generate_file_paths(start_date,
                                                                                                             end_date)
            self.parquet_size_bytes = self.get_parquet_size_bytes()
            self.load_parquet = all(
                [os.path.exists(folder) for folder in self.parquet_folder_list]) and self.parquet_size_bytes > 0
        elif self.parquet_end_date is not None:
            raise ValueError('Parquet start date must be specified if end date is provided')

        return self

    def is_file_recent(self):
        if not os.path.exists(self.parquet_full_path):
            return False
        if self.parquet_max_age_minutes == 0:
            return True
        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(self.parquet_full_path))
        if datetime.datetime.now() - file_time > datetime.timedelta(minutes=self.parquet_max_age_minutes):
            # logger.info(f"File {self.parquet_full_path} is older than {self.parquet_max_age_minutes} minutes")
            return False
        return True

    def get_parquet_size_bytes(self):
        total_size = 0
        for folder in self.parquet_folder_list:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith('.parquet'):
                        total_size += os.path.getsize(os.path.join(root, file))
        return total_size

    @staticmethod
    def ensure_file_extension(filepath: Path, extension: str) -> Path:
        if not filepath.suffix == f".{extension}":
            return filepath.with_suffix(f".{extension}")
        return filepath

    @staticmethod
    def apply_filters_dask(df, filters):
        dt_operators = ['date', 'time']
        date_operators = ['year', 'month', 'day', 'hour', 'minute', 'second', 'week_day']
        comparison_operators = [
            'gte',
            'lte',
            'gt',
            'lt',
            'exact',
            'in',
            'range',
            'contains',
            'icontains',
            'startswith',
            'endswith',
            'isnull'
        ]

        operation_map = {
            'exact': lambda col, val: col == val,
            'gt': lambda col, val: col > val,
            'gte': lambda col, val: col >= val,
            'lt': lambda col, val: col < val,
            'lte': lambda col, val: col <= val,
            'in': lambda col, val: col.isin(val),
            'range': lambda col, val: (col >= val[0]) & (col <= val[1]),
            'contains': lambda col, val: col.str.contains(val, regex=True),
            'icontains': lambda col, val: col.str.contains(val, case=False),
            'startswith': lambda col, val: col.str.startswith(val),
            'endswith': lambda col, val: col.str.endswith(val),
            'isnull': lambda col, val: col.isnull() if val else col.notnull(),
        }

        def get_temp_col(dask_df, field_name, casting):
            if casting in dt_operators + date_operators:
                # Ensure datetime conversion for date/time operations
                temp_col = dd.to_datetime(dask_df[field_name]) if casting in dt_operators else dask_df[field_name]
                if casting in date_operators + dt_operators:
                    temp_col = getattr(temp_col.dt, casting)
            else:
                temp_col = df[field_name]
            return temp_col

        for key, value in filters.items():
            parts = key.split('__')
            field_name = parts[0]
            casting = None
            operation = 'exact'

            if len(parts) == 3:
                # Adjust logic based on the parts
                _, casting, operation = parts
            elif len(parts) == 2:
                # Could be either a casting or an operation
                if parts[1] in comparison_operators:
                    operation = parts[1]
                elif parts[1] in dt_operators + date_operators:
                    casting = parts[1]
            # field_name, casting, operation = (parts + [None, 'exact'])[:3]  # Defaults added to match expected length
            temp_col = get_temp_col(df, field_name, casting)

            if operation in operation_map:
                condition = operation_map[operation](temp_col, value)
                df = df[condition]
            else:
                raise ValueError(f"Unsupported operation: {operation}")

        return df

        # dt_operators = ['date', 'time']
        # date_operators = ['year', 'month', 'day', 'hour', 'minute', 'second']
        # comparison_operators = [
        #     'gte',
        #     'lte',
        #     'gt',
        #     'lt',
        #     'exact',
        #     'in',
        #     'range',
        #     'contains',
        #     'icontains',
        #     'startswith',
        #     'endswith',
        #     'isnull'
        # ]
        # for key, value in filters.items():
        #     parts = key.split('__')
        #
        #     # Initialize defaults
        #     field_name = parts[0]
        #     casting = None
        #     operation = 'exact'  # Default operation if not explicitly provided
        #
        #     if len(parts) == 3:
        #         # Adjust logic based on the parts
        #         _, casting, operation = parts
        #     elif len(parts) == 2:
        #         # Could be either a casting or an operation
        #         if parts[1] in comparison_operators:
        #             operation = parts[1]
        #         elif parts[1] in dt_operators + date_operators:
        #             casting = parts[1]
        #
        #     # Prepare the column for operation
        #     if casting in dt_operators + date_operators:
        #         # Temporarily convert to datetime for operation, if not already
        #         temp_col = dd.to_datetime(df[field_name]) if casting in dt_operators else df[field_name]
        #     else:
        #         temp_col = df[field_name]
        #
        #     if casting in date_operators + dt_operators:
        #         temp_col = getattr(temp_col.dt, casting)
        #
        #     if operation == 'exact':
        #         condition = temp_col == value
        #     elif operation == 'gt':
        #         condition = temp_col > value
        #     elif operation == 'gte':
        #         condition = temp_col >= value
        #     elif operation == 'lt':
        #         condition = temp_col < value
        #     elif operation == 'lte':
        #         condition = temp_col <= value
        #     elif operation == 'in':
        #         condition = temp_col.isin(value)
        #     elif operation == 'range':
        #         condition = (temp_col >= value[0]) & (temp_col <= value[1])
        #     elif operation == 'contains':
        #         condition = temp_col.str.contains(value, regex=True)
        #     elif operation == 'icontains':
        #         condition = temp_col.str.contains(value, case=False)
        #     elif operation == 'startswith':
        #         condition = temp_col.str.startswith(value)
        #     elif operation == 'endswith':
        #         condition = temp_col.str.endswith(value)
        #     elif operation == 'isnull':
        #         condition = temp_col.isnull() if value else temp_col.notnull()
        #     df = df[condition]
        #
        # return df

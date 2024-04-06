#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#
import datetime
from typing import Dict, Union
import json
import pandas as pd
from django.db import models

# This is the configuration file for the df_helper module.

# conversion_map is a dictionary that maps the field types to their corresponding data type conversion functions.
# Each entry in the dictionary is a pair of a field type (as a string) and a callable function that performs the
# conversion. This mapping is used to convert the values in a pandas DataFrame to the appropriate data types based on
# the Django field type.

conversion_map: Dict[str, callable] = {
    'CharField': lambda x: x.astype(str),
    'TextField': lambda x: x.astype(str),
    'IntegerField': lambda x: pd.to_numeric(x, errors='coerce'),
    'AutoField': lambda x: pd.to_numeric(x, errors='coerce'),
    'BigIntegerField': lambda x: pd.to_numeric(x, errors='coerce'),
    'SmallIntegerField': lambda x: pd.to_numeric(x, errors='coerce'),
    'PositiveIntegerField': lambda x: pd.to_numeric(x, errors='coerce'),
    'PositiveSmallIntegerField': lambda x: pd.to_numeric(x, errors='coerce'),
    'FloatField': lambda x: pd.to_numeric(x, errors='coerce'),
    'DecimalField': lambda x: pd.to_numeric(x, errors='coerce'),
    'BooleanField': lambda x: x.astype(bool),
    'NullBooleanField': lambda x: x.astype(bool),
    'DateTimeField': lambda x: pd.to_datetime(x, errors='coerce'),
    # 'DateField': lambda x: pd.to_datetime(x, errors='coerce'),
    'DateField': lambda x: pd.to_datetime(x, errors='coerce').dt.date,
    # 'DateField': lambda x: datetime.datetime.combine(x, datetime.datetime.min.time()),
    'TimeField': lambda x: pd.to_datetime(x, errors='coerce').dt.time,
    'DurationField': lambda x: pd.to_timedelta(x, errors='coerce'),
    # for JSONField, assuming JSON objects are represented as string in df
    'JSONField': lambda x: x.apply(json.loads),
    'ArrayField': lambda x: x.apply(eval),
    'UUIDField': lambda x: x.astype(str),
}

# default_kwargs is a dictionary that provides default values for various optional parameters.
# These default values are used when the corresponding parameters are not provided by the user.

default_kwargs: Dict[str, Union[str, bool, models.Model,int, Dict, None]] = {
    'connection_name': None,
    'table': None,
    'model': None,
    'field_map': {},
    'params': None,
    'legacy_filters': False,
    'live': False,
    'use_exclude': False,
    'debug': False,
    'n_records': 0,
    'dt_field': None,
    'use_dask': False,
    'verbose_debug': False,
}
# dataframe_params is a dictionary that provides configuration options for creating a pandas DataFrame.
# These options include parameters for specifying the columns, index column, and other options for DataFrame creation.

dataframe_params: Dict[str, Union[tuple, str, bool, int, None]] = {
    "fieldnames": (),
    "index_col": None,
    "coerce_float": False,
    "verbose": True,
    "datetime_index": False,
    "column_names": None
}
# dataframe_options is a dictionary that provides additional options for modifying a pandas DataFrame.
# These options include parameters for handling duplicate values, sorting, grouping, and other DataFrame operations.

dataframe_options: Dict[str, Union[bool, str, int, None]] = {
    "debug": False,  # Whether to print debug information
    "duplicate_expr": None,  # Expression for identifying duplicate values
    "duplicate_keep": 'last',  # How to handle duplicate values ('first', 'last', or False)
    "sort_field": None,  # Field to use for sorting the DataFrame
    "group_by_expr": None,  # Expression for grouping the DataFrame
    "group_expr": None  # Expression for aggregating functions to the grouped DataFrame
}

parquet_default_params: Dict[str, Union[bool, str, int, None]] = {
    "use_parquet": False,  # Whether to use parquet files for storing data
    "parquet_storage_path": None,  # Path to the folder where parquet files are stored
    "parquet_filename": None,  # Name of the parquet file
    "parquet_max_age_minutes": None,  # Maximum age of the parquet file in minutes
}



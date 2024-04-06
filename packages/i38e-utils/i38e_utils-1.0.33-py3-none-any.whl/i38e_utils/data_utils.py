#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#

import datetime
import os
import time
from typing import Any

import pandas as pd

from .df_utils import add_df_totals


def convert_value_pairs(row):
    if row['value_type'] == "datetime":
        converted_value = datetime.datetime.strptime(row['value'], '%Y-%m-%d %H:%M:%S')
    elif row['value_type'] == 'str':
        converted_value = row['value']
    else:
        converted_value = eval(f"{row['value_type']}({row['value']})")
    return converted_value


def get_timeseries_params(df_params) -> Any:
    index_col = None
    ts_params = df_params
    if ts_params.get("datetime_index", False):
        index_col = ts_params.get('index_col', None)
        pop_cols = ['datetime_index', 'index_col']
        for p in pop_cols:
            ts_params.pop(p, None)
    return index_col, ts_params


def format_fields(df, format_options):
    for fld_name, fld_type in format_options.items():
        if fld_name in df.columns:
            df[fld_name] = df[fld_name].values.astype(fld_type)
    return df


def fillna_fields(df, fill_options):
    for fld_name, fill_value in fill_options.items():
        if fld_name in df.columns:
            df[fld_name].fillna(fill_value, inplace=True)
    return df


def cast_cols_as_categories(df, threshold=100):
    for col in df.columns:
        if df[col].dtype in ['object', 'string'] and len(df[col].unique()) < threshold:
            df[col] = df[col].astype(pd.CategoricalDtype())
    return df


def load_as_timeseries(df, **options):
    index_col = options.get("index_col", None)
    if index_col is not None and df.index.name != index_col:
        if index_col in df.columns:
            df.reset_index(inplace=True)
            df.set_index(index_col, inplace=True)
    rule = options.pop("rule", "D")
    index = options.pop("index", df.index)
    cols = options.pop("cols", None)
    vals = options.pop("vals", None)
    totals = options.pop("totals", False)
    agg_func = options.pop("agg_func", 'count')
    df = df.pivot_table(index=index, columns=cols, values=vals, aggfunc=agg_func).fillna(0)
    df = df.resample(rule=rule).sum()
    df.sort_index(inplace=True)
    if totals:
        df = add_df_totals(df)
    return df


def fix_fields(df, fields_to_fix, field_type):
    field_attributes = {
        'str': {'default_value': '', 'dtype': str},
        'int': {'default_value': 0, 'dtype': int},
        'date': {'default_value': pd.NaT, 'dtype': 'datetime64[ns]'},
        'datetime': {'default_value': pd.NaT, 'dtype': 'datetime64[ns]'}
    }

    if field_type not in field_attributes:
        raise ValueError("Invalid field type: {}".format(field_type))

    attr = field_attributes[field_type]
    fields = [field for field in fields_to_fix if field in df.columns]
    df[fields] = df[fields].fillna(attr['default_value']).astype(attr['dtype'])


def merge_lookup_data(classname, df, **kwargs):
    """
    kwargs={
        'source_col':'marital_status_id',
        'lookup_description_col':'description',
        'lookup_col':'id',
        'source_description_alias':'marital_status_description',
        'fillna_source_description_alias': True
    }
    :param classname:
    :param df:
    :param kwargs:
    :return:
    """
    if df.empty:
        return df
    source_col = kwargs.pop('source_col', None)
    lookup_col = kwargs.pop('lookup_col', None)
    lookup_description_col = kwargs.pop('lookup_description_col', None)
    source_description_alias = kwargs.pop('source_description_alias', None)
    fillna_source_description_alias = kwargs.pop('fillna_source_description_alias', False)
    fieldnames = kwargs.get('fieldnames', None)
    column_names = kwargs.get('column_names', None)

    if source_col is None or lookup_description_col is None or source_description_alias is None or lookup_col is None:
        raise ValueError(
            'source_col, lookup_col, lookup_description_col and source_description_alias must be specified')
    if source_col not in df.columns:
        # raise ValueError(f'{source_col} not in dataframe columns')
        return df
    ids = list(df[source_col].dropna().unique())
    if not ids:
        return df
    if fieldnames is None:
        kwargs['fieldnames'] = (lookup_col, lookup_description_col)
    if column_names is None:
        kwargs['column_names'] = ['temp_join_col', source_description_alias]
    kwargs[f'{lookup_col}__in'] = ids
    result = classname(live=True).load(**kwargs)
    if 'temp_join_col' in kwargs.get("column_names"):
        temp_join_col = 'temp_join_col'
    else:
        temp_join_col = lookup_col

    df = df.merge(result, how='left', left_on=source_col, right_on=temp_join_col)
    if fillna_source_description_alias:
        if source_description_alias in df.columns:
            df[source_description_alias].fillna('', inplace=True)
    if 'temp_join_col' in df.columns:
        df.drop(columns='temp_join_col', inplace=True)
    return df


class DataWrapper:
    def __init__(self, dataclass, date_field, data_path, parquet_filename, start_date, end_date,
                 verbose=False, load_params=None, reverse_order=False, overwrite=False, max_age_minutes=1440):
        self.dataclass = dataclass
        self.date_field = date_field
        self.data_path = self.ensure_forward_slash(data_path)
        self.parquet_filename = parquet_filename
        self.verbose = verbose
        self.load_params = load_params or {}
        self.reverse_order = reverse_order
        self.overwrite = overwrite
        self.max_age_minutes = max_age_minutes

        self.start_date = self.convert_to_date(start_date)
        self.end_date = self.convert_to_date(end_date)

    @staticmethod
    def convert_to_date(date):
        return datetime.datetime.strptime(date, '%Y-%m-%d').date() if isinstance(date, str) else date

    @staticmethod
    def ensure_forward_slash(path):
        return path if path.endswith('/') else path + '/'

    @staticmethod
    def ensure_directory_exists(path):
        os.makedirs(path, exist_ok=True)

    def generate_date_range(self):
        step = -1 if self.reverse_order else 1
        start, end = (self.end_date, self.start_date) if self.reverse_order else (self.start_date, self.end_date)
        current_date = start
        while current_date != end + datetime.timedelta(days=step):
            yield current_date
            current_date += datetime.timedelta(days=step)

    def process(self):
        for current_date in self.generate_date_range():
            self.process_date(current_date)

    def is_file_older_than(self, file_path, current_date):
        """Checks if the file at file_path is older than max_age_minutes or if overwrite is True."""
        today = datetime.date.today()

        if self.overwrite or self.max_age_minutes == 0 or current_date == today:
            return True
        if not os.path.exists(file_path):
            return True  # If the file does not exist, treat as "old" to allow generation.
        file_age_seconds = time.time() - os.path.getmtime(file_path)
        if self.verbose:
            print(f"File {file_path} is {round((file_age_seconds / 60), 0)} minutes old")

        return file_age_seconds / 60 > self.max_age_minutes

    def process_date(self, date):
        folder = f'{self.data_path}{date.year}/{date.month:02d}/{date.day:02d}/'
        self.ensure_directory_exists(folder)
        full_parquet_filename = os.path.join(folder, self.parquet_filename)

        if self.verbose:
            print(f"Processing {full_parquet_filename}...")

        if not self.is_file_older_than(full_parquet_filename, date):
            if self.verbose:
                print("File exists and conditions for regeneration are not met. Skipping.")
            return

        # Assuming dataclass has a method to load data for a specific date and save to parquet
        data_object = self.dataclass(live=True)
        date_filter_params = {
            f'{self.date_field}__year': date.year,
            f'{self.date_field}__month': date.month,
            f'{self.date_field}__day': date.day
        }
        df = data_object.load(**self.load_params, **date_filter_params)

        if df.empty:
            if self.verbose:
                print("No data found for the specified date.")
            return

        data_object.save_to_parquet(df, parquet_full_path=full_parquet_filename)
        if self.verbose:
            print(f"Data saved to {full_parquet_filename}")

# Usage:
# wrapper = DataWrapper(dataclass=YourDataClass, date_field="created_at", data_path="/path/to/data", parquet_filename="data.parquet", start_date="2022-01-01", end_date="2022-12-31")
# wrapper.process()

#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#

import configparser
import datetime
import glob
import os
import time
import zipfile

import openpyxl
import pandas as pd


class IniFile(configparser.ConfigParser):
    def __init__(self, config_file, defaults=None, overwrite_defaults=False):
        super().__init__()
        self.config_file = config_file
        self.defaults = defaults
        self.overwrite_defaults = overwrite_defaults
        self.go()

    def go(self):
        if not os.path.exists(self.config_file):
            self.save_config()
            self.overwrite_defaults = True

        if self.defaults is not None and self.overwrite_defaults:
            for section, content in self.defaults.items():
                self.add_section(section)
                for key in content.keys():
                    self.set(section, key, str(content[key]))
            self.save_config()
        self.read(self.config_file)
        return self

    def get_config(self, section: str, option: str) -> str:
        return self.get(section, option)

    def write_config(self, section: str, option: str, value: str) -> None:
        self.set(section, option, str(value))
        self.save_config()

    def save_config(self) -> None:
        with open(self.config_file, 'w') as configfile:
            self.write(configfile)


#
# def ensure_file_extension(filename, extension):
#     basename, ext = os.path.splitext(filename)
#     if ext != extension:
#         new_filename = f"{basename}.{extension}"
#         # shutil.move(filename, new_filename)
#         return new_filename
#     return filename


# Alternative Version
# class IniFile:
#     def __init__(self, config_file, defaults=None, overwrite_defaults=False):
#         self.config_file = config_file
#         self.defaults = defaults
#         self.overwrite_defaults = overwrite_defaults
#         self.config = configparser.ConfigParser()
#         self.create_file()
#         self.add_defaults()
#         self.read_file()
#
#     def create_file(self):
#         if not os.path.exists(self.config_file):
#             with open(self.config_file, 'w') as f:
#                 pass
#
#     def add_defaults(self):
#         if self.defaults is not None and self.overwrite_defaults:
#             for section, content in self.defaults.items():
#                 self.config.add_section(section)
#                 for key in content.keys():
#                     self.config.set(section, key, str(content[key]))
#             self.save_config()
#
#     def read_file(self):
#         self.config.read(self.config_file)
#
#     def get_config(self, section: str, option: str) -> str:
#         return self.config.get(section, option)
#
#     def write_config(self, section: str, option: str, value: str) -> None:
#         self.config.set(section, option, str(value))
#
#     def save_config(self) -> None:
#         with open(self.config_file, 'w') as configfile:
#             self.config.write(configfile)

def check_make_dir(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)
    return os.path.join(dirpath, '')


def ensure_directory_exists(dir_path):
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def ensure_forward_slash(dir_path):
    if not dir_path.endswith('/'):
        return f"{dir_path}/"
    return dir_path


def compress_files_to_zip(file_list, zip_file_name):
    with zipfile.ZipFile(zip_file_name, 'w') as zip_file:
        for file in file_list:
            zip_file.write(file)
    return zip_file_name


def adjust_worksheet_columns(worksheet, df):
    for col_idx, col in enumerate(df.columns):
        series = df[col]
        if isinstance(series, pd.Series):
            # Find the maximum length of the column name and the values in the column
            max_len = max(
                series.astype(str).map(len).max(),
                len(str(series.name))
            ) + 1  # Adding a little extra space
            # Set the width of the column in the worksheet
            worksheet.column_dimensions[openpyxl.utils.get_column_letter(col_idx + 1)].width = max_len
            # worksheet.set_column(col_idx, col_idx, max_len)


def read_most_recent_parquet(dir_path, starts_with=None) -> pd.DataFrame:
    """Read the most recent Parquet file in a specified directory."""

    # List all Parquet files in the directory that start with the specified prefix
    if starts_with is None:
        files = [f for f in os.listdir(dir_path) if f.endswith('.parquet')]
    else:
        files = [f for f in os.listdir(dir_path) if f.endswith('.parquet') and f.startswith(starts_with)]

    # Ensure there is at least one file
    if not files:
        raise ValueError("No Parquet files found in directory matching the criteria")

    # Find the most recent file
    most_recent_file = max(files, key=lambda x: os.path.getmtime(os.path.join(dir_path, x)))

    # Define the file path
    file_path = os.path.join(dir_path, most_recent_file)

    # Load the DataFrame from the Parquet file
    df = pd.read_parquet(file_path)

    return df


def ensure_file_extension(filename, extension):
    if not filename.lower().endswith(f'.{extension}'):
        return f"{filename}.{extension}"
    else:
        return filename


def check_file_exists(filename):
    return os.path.exists(filename)


def handle_save_options(**kwargs):
    save = kwargs.pop('save', False)
    filename = kwargs.pop('filename', None)
    extension = kwargs.pop('extension', None)
    stub = kwargs.pop('stub', None)

    if filename is not None:
        filename = ensure_file_extension(filename, extension)
        save = True

    if save and filename is None:
        filename = f"{stub}_{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.{extension}"

    return save, filename


def check_file_is_recent(filename, age=0, unit='minutes'):
    if not check_file_exists(filename):
        return True
    if age == 0:
        return True
    if unit == 'years':
        age = age * 31536000
    elif unit == 'months':
        age = age * 2628000
    elif unit == 'days':
        age = age * 86400
    elif unit == 'hours':
        age = age * 3600
    elif unit == 'minutes':
        age = age * 60
    else:
        raise ValueError("Invalid unit specified")

    if os.path.getmtime(filename) > time.time() - age:
        return True
    else:
        return False


def prune_aged_files(dir_path, age_days):
    """Prune files that are older than a certain number of days."""

    # Get the current time
    now = time.time()

    # Walk through the directory
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)

            # If the file is older than the specified number of days, delete it
            if os.path.getmtime(file_path) < now - age_days * 86400:
                os.remove(file_path)
                print(f"Deleted {file_path}")


def load_newest_file(dir_path, extension='xlsx'):
    files = os.listdir(dir_path)
    files = [os.path.join(dir_path, f) for f in files if f.endswith(f'.{extension}')]
    files.sort(key=lambda x: os.path.getmtime(x))
    recent_file = files[-1]
    return recent_file


def fix_sheet_name(sheet_name):
    invalid_chars = [":", "\\", "/", "?", "*", "[", "]"]
    for char in invalid_chars:
        sheet_name = sheet_name.replace(char, '-')
    sheet_name = sheet_name[:30]
    return sheet_name


class FilePathGenerator:
    # Example Usage:
    # generator = FilePathGenerator(base_path='/your/base/path')
    # file_paths = generator.generate_file_paths('2022-01-01', '2022-03-31')
    # print(file_paths)
    def __init__(self, base_path=''):
        self.base_path = base_path.rstrip('/')

    @staticmethod
    def _get_day_file_path(dir_path, day):
        return f"{dir_path}/{str(day).zfill(2)}/*.parquet"

    @staticmethod
    def _get_month_file_path(dir_path):
        return f"{dir_path}/*/*.parquet"

    def generate_file_paths(self, start_date, end_date):
        start_date = self._convert_to_datetime(start_date)
        end_date = self._convert_to_datetime(end_date)

        file_paths = []
        curr_date = start_date

        while curr_date <= end_date:
            year, month = curr_date.year, curr_date.month
            dir_path = f"{self.base_path}/{year}/{str(month).zfill(2)}"

            if os.path.exists(dir_path):
                file_paths.extend(self._get_files_for_month(curr_date, start_date, end_date, dir_path))

            curr_date = self._increment_month(curr_date)

        return file_paths

    @staticmethod
    def _convert_to_datetime(date):
        if isinstance(date, str):
            return datetime.datetime.strptime(date, '%Y-%m-%d')
        return date

    def _get_files_for_month(self, curr_date, start_date, end_date, dir_path):
        files = []
        if curr_date.year == start_date.year and curr_date.month == start_date.month:
            if curr_date.year == end_date.year and curr_date.month == end_date.month:
                files.extend(self._get_files_for_range(dir_path, start_date.day, end_date.day))
            else:
                start_day = start_date.day if start_date.day > 1 else 1
                files.extend(self._get_files_for_range(dir_path, start_day, 31))  # Max days in a month
        elif curr_date.year == end_date.year and curr_date.month == end_date.month:
            files.extend(self._get_files_for_range(dir_path, 1, end_date.day))
        else:
            month_file_path = self._get_month_file_path(dir_path)
            if glob.glob(month_file_path):
                files.append(month_file_path)
        return files

    def _get_files_for_range(self, dir_path, start_day, end_day):
        files = []
        for day in range(start_day, end_day + 1):
            day_file_path = self._get_day_file_path(dir_path, day)
            if glob.glob(day_file_path):
                files.append(day_file_path)
        return files

    @staticmethod
    def _increment_month(curr_date):
        if curr_date.month == 12:
            return datetime.datetime(curr_date.year + 1, 1, 1)
        else:
            return datetime.datetime(curr_date.year, curr_date.month + 1, 1)



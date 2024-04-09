#  core_data.py
#  Project: sensorialytics
#  Copyright (c) 2022 Sensoria Health Inc.
#  All rights reserved

import logging
from typing import Tuple, AnyStr, Set, List, Dict

import numpy as np
import pandas as pd

from sensorialytics.helpers.tools import as_bool
from sensorialytics.mathematics.tools import cast_to_float
from sensorialytics.signals.filters import Filter
from .helper import (read_header, FiltersType, KEY_SAMPLING_FREQUENCY_MEASURED,
                     KEY_SAMPLING_FREQUENCY, COL_CORE_TICK, KEY_DEVICE_NAME,
                     KEY_IS_LEADING_CORE, METADATA_SEPARATOR,
                     COEFFICIENTS_SEPARATOR, KEY_TIMESTAMP,
                     KEY__CORE_TIMESTAMP, KEY_LEADING_CORE_TIMESTAMP,
                     COL_TIME_EFFECTIVE, COL_TIME, COL_TICK)

__all__ = ['CoreData']

HeaderType = List[List[AnyStr]]


class CoreData:
    def __init__(self,
                 raw_data_path: str = None,
                 processed_data_path: str = None,
                 session_id: str = None):
        """
        :param raw_data_path: str = path of the raw data csv
        :param processed_data_path: str = path of the raw data csv
        """

        self._raw = pd.DataFrame()
        self._processed = pd.DataFrame()
        self._tags = set()
        self._metadata = {}
        self._coefficients = {}
        self._session_id = session_id

        if raw_data_path is not None:
            self._raw = self.__read_data_frame(raw_data_path)

            if COL_TICK in self._raw.columns:
                self.__process_tick()

        if processed_data_path is not None:
            self._processed = self.__read_data_frame(processed_data_path)
            self._processed.set_index(
                COL_CORE_TICK,
                drop=True,
                inplace=True
            )

        min_len = min(len(self._raw), len(self._processed))

        if min_len > 0:
            self._raw = self._raw.iloc[0:min_len, :]
            self._processed = self._processed.iloc[0:min_len, :]

    @property
    def sampling_frequency(self) -> float:
        """
        :return: float = sampling frequency (declared) of the core data
        """

        return float(self._metadata.get(KEY_SAMPLING_FREQUENCY, -1.0))

    @property
    def sampling_frequency_measured(self) -> float:
        """
        :return: float = sampling frequency (measured) of the core data
        """

        return float(self._metadata.get(KEY_SAMPLING_FREQUENCY_MEASURED, -1.0))

    @property
    def core_name(self) -> str:
        """
        :return: str = name of the core
        """

        return self._metadata.get(KEY_DEVICE_NAME, '')

    @property
    def core_code(self) -> str:
        """
        :return: str = code of the core
        """

        return self._metadata.get(KEY_DEVICE_NAME, '').split('-')[-1]

    def is_leading_core(self) -> bool:
        """
        :return: bool = a boolean determining if this core is the leading one
        """

        return as_bool(self._metadata.get(KEY_IS_LEADING_CORE, False))

    @property
    def tags(self) -> Set:
        return self._tags

    @property
    def metadata(self) -> Dict[str, str]:
        """
        :return: dict = the metadata contained in the header of the csv files
        """

        return self._metadata

    @property
    def coefficients(self) -> Dict[str, str]:
        """
        :return: dict = if present the dictionary of the remapping coefficients
                        for the analog inputs
        """

        return self._coefficients

    @property
    def raw(self) -> pd.DataFrame:
        """
        :return: pandas.DataFrame = the raw data for the core
        """

        return self._raw

    @property
    def processed(self) -> pd.DataFrame:
        """
        :return: pandas.DataFrame = the processed data for the core
        """

        return self._processed

    def update_metadata(self, metadata: dict):
        """
        Updates the metadata for the CoreData
        :param metadata: metadata to insert
        """
        self._metadata.update(metadata)

    def add_tag(self, tag: str):
        self._tags.add(tag)

    def remove_tag(self, tag: str):
        self._tags.remove(tag)

    def clear_tags(self):
        self._tags.clear()

    def filter(self, filters: FiltersType, from_raw: bool = True):
        """
        Filters the raw data passing them through filters
        :param filters:
            can be:
                - dict with {column_name: Filter}
                    e.g. {'Ax': ButterworthFilter}
                - dict with {column_name: [Filter, Filter, ..]}
                    e.g. {'Ax': [
                                    ButterworthFilter(...),
                                    RecursiveAverageFilter(...)
                                ]}
                    where the filters are applied in sequence
        :param from_raw: set to True to use raw data as source for filtering,
            False for processed
        """

        self.__ensure_processed()

        source = self.__get_source(from_raw)

        for column, flt in filters.items():
            if isinstance(flt, list):
                for flt_elem in flt:
                    self.__filter(flt_elem, column=column, source=source)
            else:
                self.__filter(flt, column=column, source=source)

    def offset(self, offsets: Dict[str, float], from_raw: bool = True) -> None:
        """
        Offsets the data using the values in offsets
        :param offsets: dict = dict composed as: {column_name : offset}
        :param from_raw: set to True to use raw data as source for offsetting,
            False for processed
        """

        self.__ensure_processed()

        source = self.__get_source(from_raw)

        for column, offset in offsets.items():
            self._processed[column] = source[column].values - offset

    def scale(self, scaling_factors: Dict[str, float],
              from_raw: bool = True) -> None:
        """
        Scales the data using the values in scaling_factor
        :param scaling_factors: dict = dict composed as:
            {column_name : scale_factors}
        :param from_raw: set to True to use raw data as source for scaling,
            False for processed
        """

        self.__ensure_processed()

        source = self.__get_source(from_raw)

        for column, scaling in scaling_factors.items():
            self._processed[column] = source[column].values / scaling

    def subsample(self, target_sampling_frequency=None,
                  decimation_factor: int = None):
        if target_sampling_frequency is None and decimation_factor is None:
            raise ValueError(
                "Must specify one of \'target_sampling_frequency\' "
                "or \'decimation_factor\'")

        if target_sampling_frequency is not None:
            if decimation_factor is None:
                decimation_factor = int(
                    self.sampling_frequency / target_sampling_frequency)
            else:
                raise ValueError(
                    "Must specify just one of \'target_sampling_frequency\' "
                    "or \'decimation_factor\'")

        raw_range = range(0, len(self._raw), decimation_factor)
        processed_range = range(0, len(self._processed), decimation_factor)

        self._raw = self._raw.iloc[raw_range, :]
        self._processed = self._processed.iloc[processed_range, :]

        self._metadata[KEY_SAMPLING_FREQUENCY] = \
            self.sampling_frequency / decimation_factor

        self._metadata[KEY_SAMPLING_FREQUENCY_MEASURED] = \
            self.sampling_frequency_measured / decimation_factor

    def __read_data_frame(self, core_data_path) -> pd.DataFrame:
        header, data_frame = self.__read_csv(core_data_path)

        self.__parse_header(header)
        self.__parse_data(data_frame)
        self.__parse_timestamp(data_frame)
        self.__parse_time(data_frame)

        return data_frame

    @staticmethod
    def __read_csv(core_data_path: str) -> Tuple[HeaderType, pd.DataFrame]:
        header, n_header_rows = read_header(core_data_path)

        raw_data = pd.read_csv(
            filepath_or_buffer=core_data_path,
            skiprows=n_header_rows
        )

        raw_data.columns = [
            c.strip().replace(' ', '_')
            for c in raw_data.columns
        ]

        return header, raw_data

    @staticmethod
    def __to_camel_case(text: str):
        if len(text) > 1:
            return text[0].lower() + text[1:]
        else:
            return text

    def __parse_header(self, header: HeaderType):
        self.__parse_metadata(header)
        self.__parse_coefficients(header)

    def __parse_metadata(self, header: HeaderType):
        metadata = [h[0].split(METADATA_SEPARATOR) for h in header if
                    len(h) == 1]
        metadata = [m for m in metadata if len(m) == 2]

        metadata = {
            self.__to_camel_case(m[0].strip()): m[1].strip()
            for m in metadata
        }

        self.update_metadata(metadata)

    def __parse_coefficients(self, header: HeaderType):
        coefficients = [h for h in header if len(h) > 1]

        for line in coefficients:
            row_coefficients = {}
            sensor = line[0]

            for coefficient in line[1:]:
                k, v = coefficient.split(COEFFICIENTS_SEPARATOR)
                row_coefficients.update({k: cast_to_float(v)})

            self._coefficients.update({sensor: row_coefficients})

    def __parse_data(self, data_frame: pd.DataFrame):
        data_frame = data_frame.reset_index(drop=True)

        self.__parse_float_columns(data_frame)

    @staticmethod
    def __parse_float_columns(data_frame: pd.DataFrame):
        for c in data_frame.columns:
            try:
                data_frame[c] = data_frame[c].astype(float)
            except ValueError:
                pass

    def __parse_timestamp(self, data_frame: pd.DataFrame):
        n = max(1, min(100, len(data_frame) - 10))

        timestamp_col = self.__get_first_available_timestamp_column(data_frame)
        timestamp = pd.to_datetime(data_frame[timestamp_col])
        t = (timestamp.values - timestamp.values[0]).astype(float) / 1.0E9

        dt = (t[n:] - t[:-n]) / n
        sampling_frequency = 1.0 / dt.mean()

        self.__check_sampling_frequency(sampling_frequency)
        self.__check_gaps(t)

        data_frame[COL_TIME_EFFECTIVE] = t
        data_frame[KEY_TIMESTAMP] = timestamp.dt.time

        self._metadata.update({
            KEY_SAMPLING_FREQUENCY_MEASURED: sampling_frequency,
        })

    @staticmethod
    def __get_first_available_timestamp_column(data_frame) -> str:
        if any(np.array(data_frame.columns) == KEY_TIMESTAMP):
            return KEY_TIMESTAMP
        elif any(np.array(data_frame.columns) == KEY__CORE_TIMESTAMP):
            return KEY__CORE_TIMESTAMP
        elif any(np.array(data_frame.columns) == KEY_LEADING_CORE_TIMESTAMP):
            return KEY_LEADING_CORE_TIMESTAMP
        else:
            raise RuntimeError('No timestamp column found')

    def __check_sampling_frequency(self, sampling_frequency):
        if abs(sampling_frequency / self.sampling_frequency - 1.0) > 0.05:
            logging.warning(
                f'\tsession {self._session_id} | '
                f'core {self.core_code} | '
                f'Sampling frequency discrepancy: '
                f'measured = {sampling_frequency}; '
                f'declared = {self.sampling_frequency}')

    def __check_gaps(self, t):
        dt = t[1:] - t[:-1]
        gaps = dt[(dt / self.sampling_frequency) > 3]

        if len(gaps) > 0:
            logging.warning(
                f'\tsession {self._session_id} | '
                f'Gaps found '
                f'{gaps}')

    def __parse_time(self, data_frame: pd.DataFrame):
        data_frame.drop(columns=['T'], inplace=True, errors="ignore")

        data_frame[COL_TIME] = np.array([
            n / self.sampling_frequency
            for n in range(len(data_frame))
        ])

    def __process_tick(self):
        tick = self._raw[COL_TICK]
        diff = tick.diff()
        missing = diff[(diff > 1) & (diff != 2 ** 16 - 1)]

        if len(missing):
            logging.warning(
                f'\tsession {self._session_id} | '
                f'core {self.core_code} | '
                f'Missing ticks: '
                f'n holes = {len(missing)}; '
                f'mean = {np.round(missing.mean(), 2)}; '
                f'var = {np.round(missing.var(), 2)}; '
                f'max = {missing.max()}')

        self._raw.set_index(
            COL_TICK,
            drop=True,
            inplace=True
        )

    def __ensure_processed(self):
        if self._processed is None:
            self._processed = self._raw.copy()

        if len(self._processed) == 0:
            self._processed = self._raw.copy()

    def __get_source(self, raw) -> pd.DataFrame:
        if raw:
            return self._raw
        else:
            return self._processed

    def __filter(self, flt: Filter, column: str, source: pd.DataFrame):
        flt.set_sampling_frequency(self.sampling_frequency)
        self._processed[column] = flt.filter(source[column])

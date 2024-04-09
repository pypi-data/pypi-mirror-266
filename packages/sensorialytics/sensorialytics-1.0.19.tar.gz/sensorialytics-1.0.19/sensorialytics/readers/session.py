#  session.py
#  Project: sensorialytics
#  Copyright (c) 2022 Sensoria Health Inc.
#  All rights reserved

import logging
import os
from typing import Dict, Tuple, Set

import pandas as pd
import requests

from sensorialytics.helpers.sensoria_io_client import SensoriaIoClient
from sensorialytics.helpers.tools import as_bool
from . import helper as h
from .core_data import CoreData
from .events import Events
from .helper import FiltersType

__all__ = ['Session']

SESSION_URL = 'https://api.sensoriafitness.com/api/1.0/session'


class Session(Dict[str, CoreData]):
    _CORE_DATA_CLASS = CoreData

    def __init__(self, session_dir: str, read_title: bool = False):
        """
        :param session_dir: directory of the session containing all the files
        :param read_title: bool = read the title of the session from the cloud
        """
        super().__init__()

        self._session_dir = session_dir
        self._session_id = h.get_session_id(session_dir=session_dir)
        self._title = ''
        self._user_id = -1
        self._core_index = 0
        self._tags = set()
        self._metadata = {}

        self._events = Events()
        self._aggregate = CoreData()

        self.__read_session_data(session_dir)

        if read_title:
            self.__read_title()

    def __str__(self):
        return f'{self.session_id} - {self.title}'

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def tags(self) -> Set:
        return self._tags

    @property
    def metadata(self):
        return self._metadata

    @property
    def title(self) -> str:
        """
        :return: title of the session
        """
        return self._title

    @property
    def aggregate(self) -> CoreData:
        """
        :return: aggregate data for the session
        """
        return self._aggregate

    @property
    def events(self) -> Events:
        """
        :return: events occurred during the session
        """
        return self._events

    @property
    def settings(self) -> dict:
        """
        :return: settings used during the session
        """
        return self._events.settings

    @property
    def leading_core(self) -> str:
        """
        :return: str leading core for the session
        """
        for core_data in self.values():
            if as_bool(core_data.metadata.get(h.KEY_IS_LEADING_CORE, False)):
                return core_data.core_name[-4:]

        return ""

    @property
    def session_dir(self):
        """
        :return: session directory
        """
        return self._session_dir

    def __getitem__(self, item: str) -> CoreData:
        """
        :param item: str name of the core used or tag. Default tags are
                assigned as C0, C1, ...
        :return: CoreData
        """
        if self.keys().__contains__(item):
            return super(Session, self).__getitem__(item)

        for core_data in self.values():
            if item in core_data.tags:
                return core_data

        raise Exception(f'No CoreData with tag or id \'{item}\'')

    def add_tag(self, tag: str):
        """
        :param tag: str tag to add to the  to the session.
        The session can be retrieved from a Sessions object by :
        sessions[tag]
        :return:
        """

        self._tags.add(tag)

    def remove_tag(self, tag: str):
        """
        :param tag:
        :return:
        """
        self._tags.remove(tag)

    def clear_tags(self):
        self._tags.clear()

    def filter(self, filters: FiltersType, from_raw: bool = True) -> None:
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
        :param from_raw: set to True to use raw as source for offsetting,
                        False for processed
        """

        for core_data in self.values():
            core_data.filter(filters=filters, from_raw=from_raw)

    def offset(self, offsets: Dict[str, Dict[str, float]],
               from_raw: bool = True) -> None:
        """
        Offsets the data using the values in offsets
        :param offsets: dict composed as:
            {
                core_id : {
                    column_name : offset
                }
            }
        :param from_raw: set to True to use raw as source for offsetting,
                        False for processed
        """

        for core_data in self.values():
            core_offsets = offsets.get(core_data.core_code)

            if core_offsets is not None:
                core_data.offset(offsets=core_offsets, from_raw=from_raw)

    def scale(self, scaling_factors: Dict[str, Dict[str, float]],
              from_raw: bool = True) -> None:
        """
                Scales the data using the values in scaling_factors
                :param scaling_factors: dict composed as:
                    {
                        core_name : {
                            column_name : scaling_factor
                        }
                    }
        :param from_raw: set to True to use raw as source for scaling, False
                        for processed
        """

        for core_data in self.values():
            core_scaling_factors = scaling_factors.get(core_data.core_code)

            if core_scaling_factors is not None:
                core_data.scale(
                    scaling_factors=core_scaling_factors,
                    from_raw=from_raw
                )

    def subsample(self, target_sampling_frequency=None,
                  decimation_factor: int = None):
        for core_data in self.values():
            core_data.subsample(
                target_sampling_frequency=target_sampling_frequency,
                decimation_factor=decimation_factor
            )

    @title.setter
    def title(self, title: str) -> None:
        """
        Sets the title of the session
        :param title: title of the session
        """

        self._title = title.lower()

    def set_user_id(self, user_id: int) -> None:
        """
        Sets the title of the session
        :param user_id: title of the session
        """

        self._user_id = user_id

    def update_metadata(self, metadata: dict):
        self._metadata.update(metadata)

    def clear_metadata(self):
        self._metadata = {}

    def __read_session_data(self, session_dir: str):
        logging.info(f'[{self._session_id}]')

        if h.is_app_session_dir(session_dir):
            self.__read_app_session_data(session_dir=session_dir)
        else:
            self.__read_portal_session_data(session_dir=session_dir)

    def __read_portal_session_data(self, session_dir: str):
        generic = not h.is_portal_session_dir(session_dir)

        organized_file_paths = self.__get_organized_portal_file_paths(
            session_dir, generic)

        self.__read_portal_core_data(organized_file_paths=organized_file_paths)
        self.__read_portal_events(organized_file_paths=organized_file_paths)
        self.__read_portal_aggregate(organized_file_paths=organized_file_paths)

    def __get_organized_portal_file_paths(self, directory,
                                          generic: bool = False) -> dict:
        """
        :param directory: directory containing the files
        :return: a dictionary of the form:
        {
            Aggregate : <filename>,
            Events : <filename>,
            CoreData : {
                <core_name>: {
                    Processed : <filename>,
                    Raw : <filename>
                }
            }
        }
        """

        file_paths = [
            os.path.join(directory, core_data_filename)
            for core_data_filename in os.listdir(directory)
            if h.is_session_file(core_data_filename, generic)
        ]

        organized_file_paths = {}
        organized_file_paths.update({h.LOG_TYPE_CORE_DATA: {}})

        for file_path in sorted(file_paths):
            log_type, core_name = self.__get_log_type(file_path)

            if core_name is None:
                organized_file_paths.update({log_type: file_path})
            else:
                core_file_paths = organized_file_paths.get(
                    h.LOG_TYPE_CORE_DATA)

                if core_name not in core_file_paths.keys():
                    core_file_paths.update({core_name: {}})

                core_file_paths[core_name].update({log_type: file_path})

        return organized_file_paths

    def __read_portal_core_data(self, organized_file_paths: dict):
        core_data_paths = organized_file_paths.get(h.LOG_TYPE_CORE_DATA, None)

        if core_data_paths is not None:
            for core_name, paths in core_data_paths.items():
                core_data = self._CORE_DATA_CLASS(
                    raw_data_path=paths.get(h.LOG_TYPE_RAW),
                    processed_data_path=paths.get(h.LOG_TYPE_PROCESSED),
                    session_id=self.session_id
                )

                core_data.add_tag(f'C{self._core_index}')
                self._core_index += 1

                self.update({core_name[-4:]: core_data})

    def __read_portal_events(self, organized_file_paths: dict):
        events_path = organized_file_paths.get(h.LOG_TYPE_EVENTS)

        if events_path is not None:
            self._events = Events(events_path=events_path)

            leading_core_data = self.get(self.leading_core, None)

            if leading_core_data is not None:
                time = leading_core_data.processed[h.COL_TIME]
                condition = ~time.index.duplicated(keep='first')
                self._events[h.COL_TIME] = time[condition]
                self._events[h.COL_TIME].fillna(0.0, inplace=True)

    def __read_portal_aggregate(self, organized_file_paths: dict):
        aggregate_path = organized_file_paths.get(h.LOG_TYPE_AGGREGATED)

        if aggregate_path is None:  # KEEP FOR LEGACY
            aggregate_path = organized_file_paths.get(h.LOG_TYPE_AGGREGATE)

        if aggregate_path is not None:
            self._aggregate = self._CORE_DATA_CLASS(
                raw_data_path=aggregate_path,
                session_id=self.session_id
            )

    def __read_title(self):
        SensoriaIoClient.authenticate()

        session_response = requests.get(
            url=f'{SESSION_URL}/{self._session_id}',
            auth=SensoriaIoClient.get_token())

        if session_response.reason == 'OK':
            api_result = session_response.json()['APIResult']
            metadata = api_result['MetaData']
            user_id = int(api_result['UserId'])

            self.title = metadata.get('Title', "# No tile found #")
            self.set_user_id(user_id=user_id)
        else:
            logging.warning(f'\tCan\'t retrieve title for session '
                            f'{self._session_id}. '
                            f'Reason: {session_response.reason}')

    @staticmethod
    def __get_log_type(path) -> Tuple[str, str]:
        log_type = h.LOG_TYPE_RAW
        core_name = None

        with open(path, 'r') as f:
            lines = f.readlines()[0:50]

        for line in lines:
            if h.KEY_CSV_LOG_TYPE + ':' in line:
                log_type = line.split(h.METADATA_SEPARATOR)[-1].strip()
            if h.KEY_CSV_DEVICE_NAME in line:
                core_name = line.split(h.METADATA_SEPARATOR)[-1].strip()

        return log_type, core_name

    def __read_app_session_data(self, session_dir: str):
        self.__read_app_raw(session_dir)
        self.__read_app_processed(session_dir)
        self.__read_app_events(session_dir)

    def __read_app_raw(self, session_dir):
        pass

    def __read_app_processed(self, session_dir):
        pass

    def __read_app_events(self, session_dir):
        directory = os.path.join(session_dir, h.EVENT_DIR_APP)

        events = pd.concat([
            Events(events_path=os.path.join(directory, filename))
            for filename in os.listdir(directory)
            if filename[-4:] == ".csv"
        ])

        self._events = Events(events=events)

    @staticmethod
    def __take(x, i: int):
        try:
            return x[i].strip()
        except IndexError:
            return None

    def __parse_event_info(self, x):
        if x is None:
            return None

        all_info = self.__take(x.split(':'), 1)

        if all_info is None:
            return None

        parsed_event_info = {}

        for info in all_info.split('|'):
            info_kv = info.strip().split('=')
            k = self.__parse_value(info_kv[0].strip())
            v = self.__parse_value(info_kv[1].strip())

            parsed_event_info.update({k: v})

        return parsed_event_info

    @staticmethod
    def __parse_value(x):
        if x is None:
            return None

        if x in ['true', 'false', 'True', 'False']:
            return as_bool(x)

        try:
            return float(x)
        except ValueError:
            return x

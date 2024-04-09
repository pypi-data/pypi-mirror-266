#  events.py
#  Project: sensorialytics
#  Copyright (c) 2024 Sensoria Health Inc.
#  All rights reserved

from __future__ import annotations

import json
import pandas as pd
from typing import Union, List

from . import helper as h

__all__ = ['Events']


class Events(pd.DataFrame):
    def __init__(self,
                 events_path: str = None,
                 events: Union[Events, pd.DataFrame] = None):
        """
        :param events_path:
        :param events:
        """

        if events is not None:
            super(Events, self).__init__(events)
            return

        if events_path is None:
            super(Events, self).__init__(pd.DataFrame())
            return

        _, n_headers = h.read_header(events_path)

        super(Events, self).__init__(
            pd.read_csv(events_path, skiprows=n_headers))

        self[h.COL_LEADING_CORE_TICK] = self[h.COL_LEADING_CORE_TICK].astype(
            int)
        self.set_index(h.COL_LEADING_CORE_TICK, drop=True, inplace=True)

        if h.COL_EVENT_PARAMS in self.columns:
            self.__parse_events_parameters()
        else:
            self.__parse_events_column_old()

    @property
    def metadata(self) -> dict:
        """
        :return: metadata used during the session
        """

        return self.get_event(h.KEY_ON_METADATA_SAVED).iloc[0, :].to_dict()

    @property
    def settings(self) -> dict:
        """
        :return: settings used during the session
        """

        return self.metadata[h.KEY_APP_SETTINGS]

    def get_event(self, event_name: str):
        """
        :param event_name: str = name of the event to get
        :return: pandas.DataFrame = DataFrame containing the all the
                                    occurrences of the selected event
        """

        condition = self[h.COL_EVENT_NAME] == event_name
        event = self[condition][h.COL_EVENT_PARAMS]

        index = event.index
        event = pd.DataFrame([p for p in event])
        event.index = index

        if len(event) == 0:
            return event

        event[h.COL_TIME] = self[h.COL_TIME].drop_duplicates()

        return event

    def filter_by_name(self, event_names: Union[str, List[str]],
                       broad_match: bool = False) -> pd.DataFrame:
        """
        :param event_names: string or list of strings containing the names of
                            the events to keep
        :param broad_match: if False matches exactly the names provided in
                            event_names, otherwise searches for names
                            containing the names provided
        :return:
        """

        event_names = self.__ensure_collection(event_names)

        keep = self[h.COL_EVENT_NAME].apply(lambda _: False)

        for event_name in event_names:
            if broad_match:
                keep = keep | self[h.COL_EVENT_NAME].str.contains(event_name)
            else:
                keep = keep | (self[h.COL_EVENT_NAME] == event_name)

        return Events(events=self[keep])

    def filter_by_tag(self, event_tags: Union[str, List[str]],
                      broad_match: bool = False) -> pd.DataFrame:
        """
        :param event_tags: string or list of strings containing the tags of
                            the events to keep
        :param broad_match: if False matches exactly the tags provided in
                            event_tags, otherwise searches for tags
                            containing the tags provided
        :return:
        """

        event_tags = self.__ensure_collection(event_tags)

        keep = self[h.COL_EVENT_NAME].apply(lambda _: False)

        for event_tag in event_tags:
            if broad_match:
                keep = keep | self[h.COL_EVENT_TAG].str.contains(event_tag)
            else:
                keep = keep | (self[h.COL_EVENT_TAG] == event_tag)

        return Events(events=self[keep])

    def filter_by_parameter(self, keys: Union[str, List[str]],
                            values: Union[str, List[str]],
                            broad_match: bool = False) -> pd.DataFrame:
        """
        :param keys:
        :param values:
        :param broad_match:
        :return:
        """

        keys = self.__ensure_collection(keys)
        values = self.__ensure_collection(values)
        keep = self[h.COL_EVENT_NAME].apply(lambda _: False)

        if len(keys) != len(values):
            raise RuntimeError('keys and values must have the same length')

        params = self[h.COL_EVENT_PARAMS]

        for k, v in zip(keys, values):
            if broad_match:
                keep = keep | params.apply(lambda x: v in str(x.get(k, '')))
            else:
                keep = keep | params.apply(lambda x: x.get(k) == v)

        return Events(events=self[keep])

    def __parse_events_parameters(self):
        def to_dict(x) -> dict:
            if x is None or pd.isna(x):
                return {}

            return json.loads(x)

        self[h.COL_EVENT_PARAMS] = self[h.COL_EVENT_PARAMS].apply(to_dict)

    def __parse_events_column_old(self):
        events = self[h.COL_EVENT].apply(
            lambda row: self.__take(row.split(':'), 0))

        events_info = self[h.COL_EVENT].apply(
            lambda row: self.__parse_event_info(row))

        self[h.COL_EVENT] = events
        self[h.COL_EVENT_INFO] = events_info

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
    def __take(x, i: int):
        try:
            return x[i].strip()
        except IndexError:
            return None

    @staticmethod
    def __parse_value(x):
        if x is None:
            return None

        if x in ['true', 'false', 'True', 'False']:
            return bool(x)

        try:
            return float(x)
        except ValueError:
            return x

    @staticmethod
    def __ensure_collection(event_tags):
        if isinstance(event_tags, str):
            event_tags = [event_tags]

        return event_tags

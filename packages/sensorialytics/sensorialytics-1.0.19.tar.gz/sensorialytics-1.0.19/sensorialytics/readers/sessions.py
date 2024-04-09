#  sessions.py
#  Project: sensorialytics
#  Copyright (c) 2022 Sensoria Health Inc.
#  All rights reserved

from __future__ import annotations

import logging
import os
import pickle
from os.path import join
from typing import Dict, Set

from .helper import (is_session_dir, FiltersType,
                     get_session_id)
from .session import Session

__all__ = ['Sessions']

SESSIONS_FILENAME = 'sessions.pickle'


class Sessions(Dict[int, Session]):
    _SESSION_CLASS = Session

    def __init__(self, sessions_dir=None, read_titles: bool = False,
                 save: bool = True, load: bool = False, update: bool = True):
        """
        :param sessions_dir: directory containing the sessions to handle
        :param read_titles: if true interrogates the cloud to get the tiles
        :param save: saves in session_dir a .pickle file containing self
        :param load: if present loads the .pickle file instead of reading the
                sessions. If a new session is inserted in session_dir it will
                be read
        """
        super().__init__()

        self.__sessions_dir = sessions_dir

        found_ids = set()

        if load:
            found_ids = self.__load_sessions()

        if update:
            self.__read_sessions(found_ids, read_titles, save)
        else:
            self.save()

    def __iter__(self):
        for session_id, session in self.items():
            yield session_id, session

    def __str__(self):
        return str(self.ids)

    @property
    def ids(self):
        """
        :return: list of session ids
        """
        return list(self.keys())

    @property
    def titles(self):
        """
        list of titles of the sessions
        :return:
        """
        return [session.title for session in self.values()]

    @property
    def description(self):
        """
        :return: dict with session id and title for each session
        """
        return {session.session_id: session.title for session in self.values()}

    @property
    def sessions_dir(self):
        """
        :return: session directory
        """
        return self.__sessions_dir

    def save(self, tag: str = None):
        """
        Saves the sessions in sessions_dir provided in the constructor
        :param tag: str optional =  tag for the specific saved instance
        """

        if tag is not None:
            filename = f'{SESSIONS_FILENAME}-{tag}'
        else:
            filename = SESSIONS_FILENAME

        with open(join(self.__sessions_dir, filename), 'wb') as f:
            pickle.dump(self, f)

    def merge(self, sessions):
        for session in sessions.values():
            self.insert_session(session)

    def insert_session(self, session: Session):
        if session.session_id not in self.keys():
            if isinstance(session, self._SESSION_CLASS):
                self.update({session.session_id: session})
            else:
                raise ValueError(
                    f"Can't add a session of type {type(session)} "
                    f"to a session set of type {type(self._SESSION_CLASS)}")

    def insert_sessions(self, sessions: Sessions):
        for session in sessions.values():
            self.insert_session(session)

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

        for session in self.values():
            session.filter(filters=filters, from_raw=from_raw)

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
        :param from_raw: set to True to use raw data as source for offsetting,
                        False for processed
        """

        for session in self.values():
            session.offset(offsets=offsets, from_raw=from_raw)

    def scale(self, scaling_factors: Dict[str, Dict[str, float]],
              from_raw: bool = True) -> None:
        """
        Scales the data using the values in scaling_factors
        :param scaling_factors: dict composed as:
            {
                core_id : {
                    column_name : scaling_factor
                }
            }
        :param from_raw: set to True to use raw data as source for filtering,
                        False for processed
        """

        for session in self.values():
            session.scale(scaling_factors=scaling_factors, from_raw=from_raw)

    def subsample(self, target_sampling_frequency=None,
                  decimation_factor: int = None, save=False):
        """
        Subsamples the CoreData of all the sessions to a customizable frequency

        :param target_sampling_frequency: the chosen sampling frequency
        :param decimation_factor: the decimation factor for the subsampling
        :param save: if true saves the sessions in the .pickle file
        :return:
        """

        for session in self.values():
            session.subsample(
                target_sampling_frequency=target_sampling_frequency,
                decimation_factor=decimation_factor
            )

        if save:
            self.save()

    def __read_sessions(self, found_ids: set,
                        read_titles: bool, save: bool):
        for session_name in os.listdir(self.__sessions_dir):
            if is_session_dir(session_name):
                session_dir = join(self.__sessions_dir, session_name)
                session_id = get_session_id(session_dir)

                if session_id not in found_ids and os.path.isdir(session_dir):
                    self.__read_session(session_dir, read_titles)

        if save:
            self.save()

        logging.info('Done!')

    def __read_session(self, session_dir, read_titles):
        session = self._SESSION_CLASS(session_dir=session_dir,
                                      read_title=read_titles)

        self.insert_session(session)

    def __load_sessions(self) -> Set[int]:
        self.clear()

        path = join(self.__sessions_dir, SESSIONS_FILENAME)

        if not os.path.exists(path):
            return set()

        found_ids = set()

        with open(join(self.__sessions_dir, SESSIONS_FILENAME), 'rb') as f:
            sessions = pickle.load(f)

        for session_id, session in sessions.items():
            self.update({session.session_id: session})
            found_ids.add(session_id)

        return found_ids


class TokenRetrievingFailed(Exception):
    def __init__(self, message: str):
        super().__init__(message)

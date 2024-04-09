#  fitfile.py
#  Project: sensorialytics
#  Copyright (c) 2021 Sensoria Health Inc.
#  All rights reserved

import fitdecode
import pandas as pd

__all__ = ['FitFile']

OTHER_FIT_FORMATS = (fitdecode.FitHeader, fitdecode.FitDefinitionMessage,
                     fitdecode.FitDataMessage, fitdecode.FitCRC)


class FitFile:
    def __init__(self, file_path: str):
        self._df = pd.DataFrame([])
        self._power = pd.Series([])
        self._recap = None

        self.__read(file_path=file_path)

    @property
    def df(self) -> pd.DataFrame:
        """
        :return: pandas.DataFrame = the whole DataFrame of the FIT file
        """

        return self._df

    @property
    def recap(self) -> dict:
        """
        :return: dict = a recap of the FIT file
        """

        return self._recap

    @property
    def power(self) -> pd.Series:
        """
        :return: pandas.Series = the power calculated during the session
        """
        return self._power

    def save_to_csv(self, csv_path: str) -> None:
        """
        :param csv_path: str = path for the output file
        """

        self._df.to_csv(path_or_buf=csv_path)

    def __read(self, file_path: str):
        frames = self.__read_fit(file_path=file_path)

        self.__get_df(frames=frames)
        self.__get_power()
        self.__get_recap()

    def __get_df(self, frames: list):
        self._df = pd.DataFrame({
            tick: {v.name: v.value for v in f.fields}
            for tick, f in enumerate(frames)
        }).T

    @staticmethod
    def __read_fit(file_path: str) -> list:
        frames = []
        with fitdecode.FitReader(file_path) as fit:
            for frame in fit:
                if isinstance(frame, fitdecode.FitDataMessage):
                    frames.append(frame)
                elif isinstance(frame, OTHER_FIT_FORMATS):
                    pass

            return frames

    def __get_power(self):
        valid_pow = ~self._df.power.isna()
        power = self._df.loc[valid_pow, ['timestamp', 'power']].copy()
        power.set_index('timestamp', inplace=True)

        self._power = power['power']

    def __get_recap(self):
        self._recap = dict(
            settings={},
            various={},
            data_columns=[],
            unknowns={},
            useless=[]
        )

        for c in self._df.columns:
            unique = [x for x in self._df[c].unique() if not pd.isna(x)]
            n_unique = len(unique)

            if c[0:8] == 'unknown_':
                self._recap['unknowns'].update({c: unique})
            else:
                if n_unique > 0:
                    if n_unique == 1:
                        self._recap['settings'].update({c: unique[0]})
                    elif n_unique < 10:
                        self._recap['various'].update({c: unique})
                    else:
                        self._recap['data_columns'].append(c)
                else:
                    self._recap['useless'].append(c)

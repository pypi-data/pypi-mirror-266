#  timer.py
#  Project: sensorialytics
#  Copyright (c) 2021 Sensoria Health Inc.
#  All rights reserved

import datetime


class ExecutionTimer:
    __start = datetime.datetime.now()

    @staticmethod
    def reset():
        ExecutionTimer.__start = datetime.datetime.now()

    @staticmethod
    def get_elapsed_time() -> datetime.timedelta:
        return datetime.datetime.now() - ExecutionTimer.__start

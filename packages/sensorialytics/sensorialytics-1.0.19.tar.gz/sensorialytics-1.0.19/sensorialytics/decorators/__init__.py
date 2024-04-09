#  __init__.py
#  Project: sensorialytics
#  Copyright (c) 2021 Sensoria Health Inc.
#  All rights reserved

import datetime
import functools
import logging

__all__ = ['execution_time']


def execution_time(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        start = datetime.datetime.now()
        logging.info(f'Execution started on: {start}')
        res = func(*args, **kwargs)
        end = datetime.datetime.now()
        logging.info(f'Execution ended on: {end}')
        logging.info(f'Execution time: {end - start}')

        return res

    return wrapped

#  exceptions.py
#  Project: sensorialytics
#  Copyright (c) 2021 Sensoria Health Inc.
#  All rights reserved


__all__ = ['FitError', 'MaximumDepthError', 'InvalidSessionError']


class FitError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class MaximumDepthError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class InvalidSessionError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

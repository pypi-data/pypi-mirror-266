#  helper.py
#  Project: sensorialytics
#  Copyright (c) 2024 Sensoria Health Inc.
#  All rights reserved

import re
from pathlib import Path
from typing import Dict, List, Union

from sensorialytics.signals import Filter

SESSION_DIR_REGEX_PORTAL = r'\bsession-[0-9]{6}-raw$'
SESSION_DIR_REGEX_BROAD = r'\bsession-[0-9]{6}-raw'
SESSION_DIR_REGEX_APP = r'[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}' \
                        r'-[0-9a-z]{4}-[0-9a-z]{12}$'
SESSION_DIR_REGEXES = [
    SESSION_DIR_REGEX_PORTAL,
    SESSION_DIR_REGEX_BROAD,
    SESSION_DIR_REGEX_APP
]

SESSION_FILE_REGEXES = [
    r'\b[0-9]{6}-[0-9]x[0-9]{4}\.csv$',
    r'\b[0-9]{6}-[0-9]{5}-[0-9]x[0-9]{4}\.csv$',
    r'\b[0-9]{8}-[0-9]{6}-[a-z0-9]{8}-[a-z0-9]{4}-'
    r'[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}.*\.csv$'
]
SESSION_ID_REGEX = r'[0-9]{6}'
SESSION_ID_REGEX_APP = r'[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}' \
                       r'-[0-9a-z]{4}-[0-9a-z]{12}$'

KEY_CSV_LOG_TYPE = "LogType"
KEY_CSV_DEVICE_NAME = "DeviceName"
METADATA_SEPARATOR = ":"
COEFFICIENTS_SEPARATOR = ":"

LOG_TYPE_PROCESSED = "Processed"
LOG_TYPE_RAW = "Raw"
LOG_TYPE_AGGREGATE = "Aggregate"  # KEEP FOR LEGACY
LOG_TYPE_AGGREGATED = "Aggregated"
LOG_TYPE_EVENTS = "Events"
LOG_TYPE_CORE_DATA = "CoreData"

KEY_SAMPLING_FREQUENCY = "samplingFrequency"
KEY_SAMPLING_FREQUENCY_MEASURED = "samplingFrequencyMeasured"
KEY_DEVICE_NAME = "deviceName"
KEY_IS_LEADING_CORE = "isLeadingCore"
KEY_TIMESTAMP = "Timestamp"
KEY__CORE_TIMESTAMP = "CoreTimestamp"
KEY_LEADING_CORE_TIMESTAMP = "LeadingCoreTimestamp"
KEY_ON_METADATA_SAVED = "onMetadataSaved"
KEY_APP_SETTINGS = "appSettings"

COL_LEADING_CORE_TICK = "LeadingCoreTick"
COL_TICK = "Tick"
COL_CORE_TICK = "CoreTick"
COL_EVENT = "Event"
COL_EVENT_TAG = "EventTag"
COL_EVENT_NAME = "EventName"
COL_EVENT_PARAMS = "EventParameters"
COL_EVENT_INFO = "EventInfo"
COL_TIME = 't'
COL_TIME_EFFECTIVE = 'tEffective'

EVENT_DIR_APP = "eventData"
PROCESSED_DIR_APP = "processedData"
RAW_DIR_APP = "rawData"

FiltersType = Union[Dict[str, Filter], Dict[str, List[Filter]]]


def is_session_dir(path: str):
    for regexp in SESSION_DIR_REGEXES:
        if re.search(regexp, path) is not None:
            return True

    return False


def is_app_session_dir(path: str):
    if re.search(SESSION_DIR_REGEX_APP, path) is not None:
        return True

    return False


def is_portal_session_dir(path: str):
    if re.search(SESSION_DIR_REGEX_BROAD, path) is not None:
        return True

    return False


def is_session_file(filename: str, generic: bool) -> bool:
    if generic:
        return ".csv" in filename

    return any([re.search(r, filename) for r in SESSION_FILE_REGEXES])


def get_session_id(session_dir: str) -> str:
    for regex in SESSION_DIR_REGEXES:
        session_match = re.search(regex, session_dir)

        if session_match is not None:
            if regex == SESSION_ID_REGEX_APP:
                return session_match.group(0)
            else:
                return re.search(SESSION_ID_REGEX,
                                 session_match.group(0)).group(0)

    path = Path(session_dir)

    return path.parts[-1]


def read_header(core_data_path):
    with open(core_data_path, 'r') as f:
        lines = f.readlines()

    header = [
        (i, line) for i, line in enumerate(lines)
        if len(line.split(',')) == 1 and line != 'sep=,\n'
    ]

    n_header_rows = header[-1][0] + 1

    header = [
        line[1].replace(',\n', '').replace('\n', '').split(',')
        for line in header
    ]

    return header, n_header_rows

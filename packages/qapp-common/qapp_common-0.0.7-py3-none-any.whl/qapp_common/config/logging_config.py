"""
    QApp Platform Project logging_config.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
import sys

from loguru import logger

logger.add(sink=sys.stderr, format="{level} : {time} : {message}: {process}", level='DEBUG')

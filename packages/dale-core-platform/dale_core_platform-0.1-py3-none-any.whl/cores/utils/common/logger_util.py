import logging
import os
from colorlog import ColoredFormatter

from cores.const.common import TimeConst, EnvConst


_log = os.getenv(EnvConst.Environment.LOG_LEVEL) if os.getenv(
    EnvConst.Environment.LOG_LEVEL) else EnvConst.Logger.INFO
__LOG_LEVEL = logging.getLevelName(_log)
__LOG_FORMAT = "\t%(asctime)-6s %(log_color)s%(levelname)7s [%(filename)s:%(lineno)d] | %(log_color)s%(message)s"
logging.root.setLevel(__LOG_LEVEL)
logger = logging.getLogger('pythonConfig')  # pylint: disable=invalid-name
logger.propagate = False
if not logger.handlers:
    stream = logging.StreamHandler()  # pylint: disable=invalid-name
    stream.setLevel(__LOG_LEVEL)
    stream.setFormatter(ColoredFormatter(
        __LOG_FORMAT, TimeConst.Format.FORMAT_24_HOUR))  # "%Y-%m-%d %H:%M:%S"
    logger.setLevel(__LOG_LEVEL)
    logger.addHandler(stream)

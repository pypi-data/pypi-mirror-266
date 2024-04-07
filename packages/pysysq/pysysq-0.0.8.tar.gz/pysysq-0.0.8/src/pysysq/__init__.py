import logging.config
from os import path

from os.path import dirname, abspath
from .sq_base import *


logging.config.fileConfig(path.join((dirname(abspath(__file__))), 'logging.conf'))

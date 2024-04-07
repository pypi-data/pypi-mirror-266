import logging

from ..sq_time_base import SQTimeBase


class SQLogger:
    def __init__(self, logger_name: str, owner: str):
        self.logger = logging.getLogger(logger_name)
        self.name = owner

    def set_level(self, level):
        self.logger.setLevel(level)

    def debug(self, message):
        self.logger.debug(f'{self.name}::{SQTimeBase.get_current_sim_time()}:: {message}')

    def info(self, message):
        self.logger.info(f'{self.name}::{SQTimeBase.get_current_sim_time()}:: {message}')

    def warning(self, message):
        self.logger.warning(f'{self.name}::{SQTimeBase.get_current_sim_time()}:: {message}')

    def error(self, message):
        self.logger.error(f'{self.name}::{SQTimeBase.get_current_sim_time()}:: {message}')

    def critical(self, message):
        self.logger.critical(f'{self.name}::{SQTimeBase.get_current_sim_time()}:: {message}')

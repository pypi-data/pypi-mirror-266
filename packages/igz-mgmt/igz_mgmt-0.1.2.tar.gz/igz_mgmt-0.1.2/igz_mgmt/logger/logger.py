# Copyright 2023 Iguazio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging
import sys


class HumanReadableFormatter(logging.Formatter):
    def __init__(self):
        super(HumanReadableFormatter, self).__init__()

    def format(
        self, record
    ):  # take last 30 chars of logger name, if shorter, take all, if longer, take last 30
        logger_name = record.name[-30:]
        return "{0} {1:30} [{2}] {3}".format(
            self.formatTime(record, self.datefmt),
            logger_name,
            record.levelname.lower(),
            record.getMessage(),
        )


class Logger(object):
    def __init__(self, level="DEBUG", logger_name=None, logger=None):
        self._logger = logger or logging.getLogger(
            "root" if not logger_name else logger_name
        )
        self.set_level(level)
        self._handlers = {}

    def set_handler(self, handler_name, file, formatter):
        # check if there's a handler by this name
        if handler_name in self._handlers:
            self._logger.removeHandler(self._handlers[handler_name])

        # create a stream handler from the file
        stream_handler = logging.StreamHandler(file)

        # set the formatter
        stream_handler.setFormatter(formatter)

        # add the handler to the logger
        self._logger.addHandler(stream_handler)

        # save as the named output
        self._handlers[handler_name] = stream_handler

    def set_level(self, level):
        self._logger.setLevel(level)

    def get_level(self):
        return self._logger.getEffectiveLevel()

    def get_child(self, name):
        new_logger = Logger(
            logger_name=f"{self._logger.name}.{name}",
            level=logging.getLevelName(self._logger.level),
        )
        new_logger._handlers = self._handlers
        return new_logger

    def debug(self, message, *args):
        self._logger.debug(message, *args)

    def info(self, message, *args):
        self._logger.info(message, *args)

    def warn(self, message, *args):
        self._logger.warning(message, *args)

    def error(self, message, *args):
        self._logger.error(message, *args)

    def debug_with(self, message, *args, **kw_args):
        self._logger.debug(self._add_kw_args_to_message(message, kw_args), *args)

    def info_with(self, message, *args, **kw_args):
        self._logger.info(self._add_kw_args_to_message(message, kw_args), *args)

    def warn_with(self, message, *args, **kw_args):
        self._logger.warning(self._add_kw_args_to_message(message, kw_args), *args)

    def error_with(self, message, *args, **kw_args):
        self._logger.error(self._add_kw_args_to_message(message, kw_args), *args)

    @staticmethod
    def _add_kw_args_to_message(message, kw_args):
        return "{0}: {1}".format(message, kw_args) if kw_args else message


_logger = None


def get_or_create_logger(level="DEBUG", name="root", logger=None):
    global _logger
    if not _logger:
        _logger = Logger(level=level, logger_name=name, logger=logger)
        if not logger:
            _logger.set_handler("stdout", sys.stdout, HumanReadableFormatter())
    if _logger._logger.name != name:
        return _logger.get_child(name)
    return _logger

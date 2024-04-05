# Product:   Macal
# Author:    Marco Caspers
# Date:      16-10-2023
#
#    This library is licensed under the MIT license.
#
#    (c) 2023 Westcon-Comstor
#    (c) 2023 WestconGroup, Inc.
#    (c) 2023 WestconGroup International Limited
#    (c) 2023 WestconGroup EMEA Operations Limited
#    (c) 2023 WestconGroup European Operations Limited
#    (c) 2023 Sama Development Team
#
# Syslog/logging external functions

import logging
import logging.config
import sys
from typing import Any


class SysLog:
    def __init__(self):
        self.__address__ = "localhost"
        self.__port__ = 514

        # REF, modified from:
        #   https://stackoverflow.com/a/19367225

        self.__config__ = {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "verbose": {"format": "%(levelname)s %(module)s P%(process)d T%(thread)d %(message)s"},
                "simple": {"format": "%(levelname)s %(message)s"},
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "stream": sys.stdout,
                    "formatter": "simple",
                },
                "syslog0": {
                    "class": "logging.handlers.SysLogHandler",
                    "address": "/dev/log",
                    "facility": "local0",
                    "formatter": "simple",
                },
                "syslogR": {
                    "class": "logging.handlers.SysLogHandler",
                    "address": (self.__address__, self.__port__),
                    "formatter": "simple",
                },
            },
            "loggers": {
                "macal-syslog": {
                    "handlers": ["syslog0", "stdout"],
                    "level": logging.DEBUG,
                    "propagate": True,
                },
                "macal-syslog-remote": {
                    "handlers": ["syslogR"],
                    "level": logging.DEBUG,
                    "propagate": False,
                },
            },
        }
        logging.config.dictConfig(self.__config__)
        self.handle = None
        self.debug = None
        self.info = None
        self.warn = None
        self.error = None
        self.critical = None
        self.syslog_enabled = False
        self.remote_enabled = False

    def SysLogInit(self, remote: bool):
        if (remote is True and self.remote_enabled) or (remote is False and self.syslog_enabled):
            raise Exception("Syslog is already initialized!")
        if remote is True:
            self.remote_enabled = True
            self.handle = logging.getLogger("macal-syslog-remote")
            self.debug = self.handle.debug
            self.info = self.handle.info
            self.warn = self.handle.warn
            self.error = self.handle.error
            self.critical = self.handle.critical
        else:
            self.syslog_enabled = True
            self.handle = logging.getLogger("macal-syslog")
            self.debug = self.handle.debug
            self.info = self.handle.info
            self.warn = self.handle.warn
            self.error = self.handle.error
            self.critical = self.handle.critical

    def SysLogSetAddress(self, address, port):
        if self.remote_enabled is True or self.syslog_enabled is True:
            raise Exception("Cannot change syslog configuration after initialization.")
        self.__address__ = address
        self.__port__ = port
        logging.config.dictConfig(self.__config__)


SysLogLocal = SysLog()


def Syslog(level: str, message: str) -> None:
    """Implementation of Syslog function"""
    if level == "debug" and SysLogLocal.debug is not None:
        SysLogLocal.debug(message)
    elif (level == "info" or level == "information") and SysLogLocal.info is not None:
        SysLogLocal.info(message)
    elif (level == "warn" or level == "warning") and SysLogLocal.warn is not None:
        SysLogLocal.warn(message)
    elif level == "error" and SysLogLocal.error is not None:
        SysLogLocal.error(message)
    elif level == "critical" and SysLogLocal.critical is not None:
        SysLogLocal.critical(message)
    else:
        raise Exception(f"Invalid syslog level given: {level}")


def SyslogInit(remote: bool) -> None:
    """Implementation of SysLog init function"""
    SysLogLocal.SysLogInit(remote)


def SyslogSetAddress(address: Any, port: Any) -> None:
    """Implementation of SysLog SetAddress function"""
    SysLogLocal.SysLogSetAddress(address, port)

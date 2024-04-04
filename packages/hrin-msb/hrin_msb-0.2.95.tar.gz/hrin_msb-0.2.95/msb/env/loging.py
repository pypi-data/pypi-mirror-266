import logging
import json
from logging.handlers import RotatingFileHandler
import os

"""
	LOGGING CONSTANTS
"""

FILE_MAX_BYTES = 10 * 1024 * 1024
FILE_BACKUP_COUNT = 5
LOG_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
ERROR_LOG_FILE_NAME, INFO_LOG_FILE_NAME = "exceptions.log", "info.log"
LOG_SEPERATOR = f"{'-' * 100}\n"
MSB_DEFAULT_LOG_HANDLER_CLASS = 'msb.env.loging.DefaultLogHandler'
MSB_ERROR_LOG_HANDLER_CLASS = 'msb.env.loging.ErrorLogHandler'
MSB_JSON_LOG_HANDLER_CLASS = 'msb.env.loging.JsonLogHandler'
MSB_CONSOLE_LOG_HANDLER_CLASS = 'logging.StreamHandler'
MSB_EMAIL_LOG_HANDLER_CLASS = 'django.utils.log.AdminEmailHandler'

LOG_LEVEL_CHOICES = (
	(logging.INFO, 'INFO'),
	(logging.DEBUG, 'DEBUG'),
	(logging.WARNING, 'WARNING'),
	(logging.ERROR, 'ERROR'),
	(logging.CRITICAL, 'CRITICAL'),
)

"""
LOGGING FORMATTERS
"""
INFO_LOG_FORMAT = '({asctime})[{levelname}]: {message}'
ERROR_LOG_FORMAT = "[LEVEL]: {levelname}\n[TIME]: {asctime}\n[MESSAGE]:{message}\n[STACK]: {exc_info}\n"
DEFAULT_FORMATTERS = {
	'console': {'style': '{', 'datefmt': LOG_DATETIME_FORMAT, 'format': ERROR_LOG_FORMAT}
}

"""
LOGGING FILTERS
"""
DEFAULT_FILTERS = {
	'require_debug_true': {"()": "django.utils.log.RequireDebugTrue", }
}


class DefaultLogFormatter(logging.Formatter):

	def __init__(self, *args, **kwargs):
		self._log_separator = LOG_SEPERATOR
		super().__init__(
			fmt=kwargs.get('fmt', INFO_LOG_FORMAT),
			datefmt=kwargs.get('datefmt', LOG_DATETIME_FORMAT),
			style=kwargs.get('style', '{'),
			validate=kwargs.get('validate', True),
			defaults=kwargs.get('defaults', None),
		)


class JsonLogFormatter(DefaultLogFormatter):

	def format(self, record):
		log_data = {
			'timestamp': self.formatTime(record, self.datefmt),
			'level': record.levelname,
			'message': record.getMessage(),
			'logger_name': record.name,
			'filename': record.filename,
			'lineno': record.lineno,
			'func_name': record.funcName,
			'module': record.module,
			'pathname': record.pathname,
			'process': record.process,
			'thread': record.thread,
			'thread_name': record.threadName,
			'exc_info': self.formatException(record.exc_info) if record.exc_info else None,
		}
		return json.dumps(log_data)


class ErrorLogFormatter(DefaultLogFormatter):

	def __init__(self):
		super().__init__(fmt=ERROR_LOG_FORMAT)

	def format(self, record):
		_log = self._fmt.format(
			asctime=self.formatTime(record, self.datefmt),
			levelname=record.levelname,
			message=record.getMessage(),
			exc_info=self.formatException(record.exc_info) if record.exc_info else None,
		)
		return f"{self._log_separator}{_log}{self._log_separator}"


class DefaultLogHandler(RotatingFileHandler):
	def __init__(self, *args, **kwargs):
		kwargs.update({'maxBytes': FILE_MAX_BYTES, 'backupCount': FILE_BACKUP_COUNT})
		super().__init__(*args, **kwargs)
		self.formatter = DefaultLogFormatter()


class ErrorLogHandler(DefaultLogHandler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.formatter = ErrorLogFormatter()


class ErrorLogHandler(DefaultLogHandler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.formatter = ErrorLogFormatter()


class JsonLogHandler(DefaultLogHandler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.formatter = JsonLogFormatter()


"""
LOGGING LOGGERS
"""
DEFAULT_LOGGERS = {
	"root": {
		"handlers": ["error", 'email',"console"],
		"level": "WARNING",
		"propagate": True,

	},
	"django": {
		"handlers": ["console","error"],
		"level": "DEBUG",
		"propagate": False,
	},
}
"""
DEFAULT LOGGING CONFIGURATION
"""


class MsbLoggingConfiguration(object):
	_instance = None
	_filters: dict = {}
	_formatters: dict = {}
	_loggers: dict = {}

	@property
	def filters(self) -> dict:
		return self._filters

	@property
	def formatters(self) -> dict:
		return self._formatters

	@property
	def handlers(self):
		info_file = os.path.join(self._logsdir, INFO_LOG_FILE_NAME)
		error_file = os.path.join(self._logsdir, ERROR_LOG_FILE_NAME)
		return {
			"console": {'class': MSB_CONSOLE_LOG_HANDLER_CLASS, 'level': 'INFO', 'filters': ['require_debug_true'], },
			"error": {'class': MSB_JSON_LOG_HANDLER_CLASS, 'filename': error_file, 'level': 'WARNING', },
			"email": {'class': MSB_EMAIL_LOG_HANDLER_CLASS, 'level': 'CRITICAL', 'include_html': True, },
		}

	@property
	def loggers(self) -> dict:
		return self._loggers

	@property
	def config(self) -> dict:
		return {
			"version": 1,
			"disable_existing_loggers": False,
			"handlers": self.handlers,
			"filters": self.filters,
			"formatters": self.formatters,
			"loggers": self.loggers,
		}

	@property
	def info_logger(self) -> logging.Logger:
		return logging.getLogger('info')

	@property
	def django_logger(self) -> logging.Logger:
		return logging.getLogger('django')

	@property
	def root_logger(self) -> logging.Logger:
		return logging.getLogger('root')

	def set_logs_dir(self, logsdir: str):
		self._logsdir = logsdir
		return self

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super().__new__(cls, *args, **kwargs)
		return cls._instance

	def __init__(self, logsdir: str = '', **kwargs):
		self._logsdir = logsdir
		self._kwargs = kwargs
		self._filters = DEFAULT_FILTERS
		self._formatters = DEFAULT_FORMATTERS
		self._loggers = DEFAULT_LOGGERS

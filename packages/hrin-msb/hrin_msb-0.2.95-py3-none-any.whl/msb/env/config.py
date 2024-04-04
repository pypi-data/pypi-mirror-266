import os

from .constants import (NameConst)


# Env variable class
class EnvVar(object):
	_key = None

	_value = None

	def __init__(self, key: str = '', value: str = ''):
		self._key = key
		self._value = value

	def __str__(self):
		return f"{self._key} : {self._value}"

	def as_str(self, default: str = '') -> str:
		return default if self._value is None else self._value

	def as_int(self, default: int = 0) -> int:
		return default if self._value is None else int(self._value)

	def as_float(self, default: float = 0.0) -> float:
		return default if self._value is None else float(self._value)

	def as_bool(self, default: bool = False) -> bool:
		if self._value is not None:
			return (int(self._value) > 0) if self._value.isnumeric() \
				else self._value.lower() in ['yes', 'true', '1']
		else:
			return default

	def as_list(self, sep='|', default: list = None) -> list:
		default = default if default is not None else []
		return default if self._value is None else self._value.split(sep=sep)

	def as_tuple(self, sep='|', default: tuple = None) -> tuple:
		default = default if default is not None else tuple()
		return tuple(self.as_list(sep=sep, default=list(default)))

	def as_dict(self, sep='|', kv_sep: str = '=', default: dict = None) -> dict:
		default = default if default is not None else dict()
		lst = self.as_list(sep=sep)
		if len(lst) > 0:
			return {
				str(item).strip().split(kv_sep)[0]:
					str(item).strip().split(kv_sep)[1]
				for item in lst}

	def as_path(self, default='', joinpath: str = None):
		if joinpath is not None:
			return os.path.join(joinpath, self.as_str(default=default))
		return self.as_str(default=default)


class MsbConfig(object):
	_instance = None

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super().__new__(cls, *args, **kwargs)
		return cls._instance

	def load(self, env_path: str = '', main_file: str = '', local_file: str = ''):
		from .core import load_config
		load_config(env_path, main_file, local_file)

	def is_loaded(self) -> bool:
		return os.environ.get(NameConst.ENV_LOAD_STATUS_KEY_NAME) is not None

	def get(self, key: str = '', default=None) -> EnvVar:
		return EnvVar(key=key, value=os.environ.get(key, default=default))

	def get_settings(self, name: str, default=None):
		from django.conf import settings
		return getattr(settings, name, default)

	def debug(self):
		return self.get(NameConst.DEBUG_VARIABLE_NAME).as_bool(default=False)

	def env_name(self) -> str | None:
		return self.get(NameConst.ENVIRONMENT_VARIABLE_NAME).as_str(default=None)

	def is_local_env(self):
		return self.env_name() == NameConst.LOCAL_ENV_NAME

	def is_dev_or_test_env(self) -> bool:
		return str(self.env_name()).lower() in NameConst.DEV_OR_TEST_ENV_NAMES_LIST

	def is_dev_or_test_or_stage_env(self) -> bool:
		return str(self.env_name()).lower() == NameConst.STAGE_ENV_NAME or self.is_dev_or_test_env()

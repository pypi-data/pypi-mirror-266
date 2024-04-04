import logging
from argparse import ArgumentParser

from msb.env import Config, NameConst, PathConst
from .constants import (REGEX_TO_SELECT_ENV_VARIABLE, REGEX_TO_REPLACE_ENV_VARIABLE)
from .django import (DjangoFixtureInstaller)
from .funcs import (
	require_django, run_management_command, drop_database_tables
)


def build_prod_env_file_from(dev_env_file_path: str = None, prod_env_file_path: str = None):
	import os, re

	dev_env_file_path = dev_env_file_path or PathConst.DEV_ENV_FILE_PATH
	prod_env_file_path = prod_env_file_path or PathConst.PROD_ENV_FILE_PATH

	if os.path.isfile(dev_env_file_path) and os.path.isfile(prod_env_file_path):
		with open(dev_env_file_path, "r+") as dev_env_file:
			dev_env_file_content = dev_env_file.read()

		prod_env_file_content = re.sub(
			REGEX_TO_SELECT_ENV_VARIABLE, REGEX_TO_REPLACE_ENV_VARIABLE, dev_env_file_content
		)

		with open(prod_env_file_path, "w+") as prod_env_file:
			prod_env_file.write(prod_env_file_content)


def _drop_database_task(**kwargs):
	"""[ -d=<str:'db_name'> ] : Drops all tables from the databse"""
	if kwargs.get("env", None) not in NameConst.DEV_ENV_NAMES_LIST:
		return logging.warning(msg=f"Dropping Tables only allowed in {NameConst.DEV_ENV_NAMES_LIST} Enviroment")
	if not (db := kwargs.get("-d", None)):
		return logging.warning(msg="Please specify a database name")

	drop_database_tables(db_name=db)


def _load_database_fixtures_task(env=None, _force: bool = False, **kwargs):
	""": Loads Database Fixtures for the current env."""
	addtional_fixture_dirs = [NameConst.TEST_FIXTURE_DIR_NAME] if Config.is_dev_or_test_env() else []

	for _dir in [NameConst.DEFAULT_FIXTURE_DIR_NAME, *addtional_fixture_dirs]:
		_installer = DjangoFixtureInstaller(from_dir=_dir.lower()).install()


def _fresh_db_setup_task(**kwargs):
	"""[ -b=<:bool=False> build Migration ] [ -l=<:bool=True>, Load Fixtures ] [ -d=<str:'default'> ]
	: Drops all tables,	Migrate created	migrations & loads db fixtures."""
	if kwargs.get("env", None) not in NameConst.DEV_ENV_NAMES_LIST:
		raise ValueError(f"This Task can Only Be Run For {NameConst.DEV_ENV_NAMES_LIST} Environment")
	_drop_database_task(**{"-d": kwargs.get('-d', NameConst.DEFAULT_DATABASE_NAME), **kwargs})
	_migrate_task(**dict(**kwargs))


def _make_migrations_task(**kwargs):
	""": Creates db migrations for all apps."""
	for app in kwargs.get('apps', []):
		run_management_command("makemigrations", app)


def _migrate_task(**kwargs):
	"""[ -l=<:bool=True>, Load Fixtures ] [ -b=<bool> build Migration ] : Migrate all apps."""
	if kwargs.get("-b", False):
		_make_migrations_task(**kwargs)

	run_management_command("migrate", "--no-input")

	if kwargs.get("-l", False):
		_load_database_fixtures_task(**kwargs)


@require_django
class MsbSetupTask:
	__task_details: dict = {
		"load_fixtures": _load_database_fixtures_task,
		"makemigrations": _make_migrations_task,
		"migrate": _migrate_task,
		"clean_db": _drop_database_task,
		"reset_db": _fresh_db_setup_task
	}
	_kwargs: dict = {}

	@property
	def task_names(self):
		return list(self.__task_details.keys())

	@property
	def usage_text(self):
		_task_list = [f"[ -t {k} ] {v.__doc__}\n" for k, v in self.__task_details.items()]
		return f"python setup.py -t task_name arg1=value1  arg2=value2 if any.\n{''.join(_task_list)}\n\n\n"

	@property
	def env(self):
		return self._kwargs.get('env', None)

	def __get_user_inputs(self):
		parser = ArgumentParser(prog='Msb Application Setup Task', usage=self.usage_text)
		parser.add_argument('-t', choices=self.task_names, help='Task Name', required=True)
		return parser.parse_known_args()

	def __init__(self, for_apps: list, for_dbs: list, **kwargs):
		self._kwargs = {"env": Config.env_name(), "apps": for_apps, "dbs": for_dbs, **kwargs}

	def run(self):
		try:
			input_args, task_args = self.__get_user_inputs()
			input_task_name = input_args.t

			if not callable(task_name := self.__task_details.get(input_task_name, None)):
				raise ValueError(f"Invalid Task Name {task_name}")

			self._kwargs.update({i.split("=")[0]: i.split("=")[1] for i in task_args if "=" in i})

			return task_name(**self._kwargs)
		except KeyboardInterrupt:
			logging.warning("Keyboard interrupt occurred.")
		except Exception as e:
			logging.exception(e)

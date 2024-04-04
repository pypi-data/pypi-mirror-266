import logging
import os

from msb.env import (NameConst, PathConst)
from django.db.migrations.recorder import MigrationRecorder

from .funcs import (log_to_console)


class DjangoBase:
	def _execute_cmd(self, *args, format=True, log=True):
		from django.core.management import call_command
		if log:
			log_to_console(msg=f"executing {' '.join(args if len(args) > 0 else 'all')} ", format=format)
		call_command(*args)

	def _db_query(self, db_connection, *queries):
		if db_connection and len(queries) > 0:
			with db_connection.cursor() as cursor:
				_result = []
				for query in queries:
					print(f"Executing Query = {query}\n")
					query_result = cursor.execute(query)
					if query.lstrip(' ').lower().startswith(('select', 'show')):
						_result.append(cursor.fetchall())
					else:
						_result.append(query_result)
				return _result[0] if len(_result) == 1 else _result


class DjangoFixtureInstaller(DjangoBase):

	def __init__(self, from_dir: str, app: str = '', is_yaml: bool = True):
		self.recorder = MigrationRecorder(None)
		self.fixture_dir = from_dir
		self.app_name = app
		self.file_ext = NameConst.YAML_FILE_EXTENTION_NAME if is_yaml else "json"

	@property
	def migration_objects(self):
		return self.recorder.Migration.objects

	@property
	def fixture_app(self):
		return f"{self.app_name + '_' if self.app_name  else ''}{self.fixture_dir}_fixtures".strip(' ')

	@property
	def fixture_directory_path(self):
		return PathConst.FIXTURES_DIR_PATH.joinpath(self.fixture_dir)

	@property
	def fixture_files_to_load(self) -> list:
		if os.path.isdir(self.fixture_directory_path):
			return sorted([file for file in os.listdir(self.fixture_directory_path) if file.endswith(f'.{self.file_ext}')])
		return []

	def _save_fixture_record(self, fixture):
		# Create a new migration record with the fixture name
		migration_record = self.recorder.Migration(app=self.fixture_app, name=fixture)

		# Save the migration record to the django_migrations table
		migration_record.save()

	def _get_installed_fixtures(self):
		# Retrieve all the installed fixtures from the django_migrations table
		installed_fixtures = self.migration_objects.filter(app=self.fixture_app).values_list('name', flat=True)

		return list(installed_fixtures)

	def _delete_fixture_record(self, *fixtures):
		# Delete the record for a particular fixture from the django_migrations table
		self.recorder.Migration.objects.filter(app=self.fixture_app, name__in=fixtures).delete()

	def _load_fixture(self, fixture):
		try:
			self._execute_cmd("loaddata", fixture, format=False, log=False)
			self._save_fixture_record(fixture=fixture)
			return "Success"
		except Exception as e:
			return f"Failed->{e}"

	def install(self, reinstall: bool = False):
		_log_message, _final_result = "Loading {} fixtures from '{}' Dir in following sequence:", []
		if (_fixture_count := len(_fixtures_list := self.fixture_files_to_load)) > 0:
			if reinstall:
				self._delete_fixture_record(*_fixtures_list)

			log_to_console(_log_message.format(_fixture_count, self.fixture_dir), format=True)
			_installed_fixtures = self._get_installed_fixtures()

			for _fixture in _fixtures_list:
				_status = self._load_fixture(_fixture) if _fixture not in _installed_fixtures \
					else "Skipped (Fixture is Already Installed)."
				print(_fixture, ":", _status)

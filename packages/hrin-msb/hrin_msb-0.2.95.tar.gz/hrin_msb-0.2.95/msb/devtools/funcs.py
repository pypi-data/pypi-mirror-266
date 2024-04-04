from msb.env import NameConst, PathConst

from .dataclasses import DbVendorConfig


def log_to_console(msg, format=False, sep="\n"):
	if format:
		_sep = '#' * ((len(msg) if 30 <= len(msg) <= 100 else 100) + 10)
		msg = f"\n{_sep}\n##  {msg.capitalize()}\n{_sep}\n"
	return print(msg)


def run_management_command(*args, format=True, log=True):
	from django.core.management import call_command
	if len(args) > 0:
		if log:
			log_to_console(msg=f"running command: {' '.join(args if len(args) > 0 else 'all')} ", format=format)
		call_command(*args)


def execute_db_query(db_connection, *queries):
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


def drop_database_tables(db_name):
	from django.db import connections
	con = connections[db_name]
	db_config = get_django_db_vendor_config(db_connection=con)
	if db_config:
		log_to_console(f"Dropping Tables From Database[{db_name}]", format=True)
		table_list = execute_db_query(con, db_config.query_to_list_tables)
		queries_to_drop_tables = db_config.queries_to_drop_multiple_tables(table_list, )
		execute_db_query(con, *[*queries_to_drop_tables])


def get_django_db_vendor_config(db_connection) -> DbVendorConfig:
	from .constants import DJANGO_MIGRATION_DB_VENDOR_CONFIG
	if db_connection and hasattr(db_connection, 'vendor'):
		return DJANGO_MIGRATION_DB_VENDOR_CONFIG.get(getattr(db_connection, 'vendor'))
	return None


def init_django_app(settings_dir: str = NameConst.APP_DIR_NAME, *sys_pathlist, **kwargs):
	import django, sys, os
	sys.path.extend([*PathConst.SYS_PATH_LIST, *sys_pathlist])
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{settings_dir}.settings")
	os.environ.setdefault("PYTHONUNBUFFERED", "1")

	django.setup()


def require_django(_func):
	def inner_func(*args, **kwargs):
		init_django_app()
		return _func(*args, **kwargs)

	return inner_func

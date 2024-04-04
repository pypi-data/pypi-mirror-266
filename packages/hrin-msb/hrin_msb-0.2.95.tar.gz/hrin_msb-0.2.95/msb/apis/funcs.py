from django.urls import path, include
from msb.validation import validate_against, ValidationSchema, ValidationExceptions
from django.utils import timezone
from msb.env import Config

from .constants import CRUD_URL_PK_NAME, CrudMethods, REQUEST_METHODS as HttpVerbs
from .exceptions import ApiViewsetExceptions


def search_action_routes(cls, search: bool):
	actions = {HttpVerbs.POST: (CrudMethods.search if search == True else CrudMethods.not_found)}
	return path("/search", cls.as_view(actions=actions))


def single_action_routes(cls, retrieve: bool = True, update: bool = True, delete: bool = True):
	actions = {
		HttpVerbs.GET: (CrudMethods.retrieve if retrieve == True else CrudMethods.not_found),
		HttpVerbs.PUT: (CrudMethods.update if update == True else CrudMethods.not_found),
		HttpVerbs.DELETE: (CrudMethods.delete if delete == True else CrudMethods.not_found),
	}
	return path(f"/<str:{(cls.pk_name or CRUD_URL_PK_NAME)}>", cls.as_view(actions=actions))


def bulk_action_routes(cls, create: bool = True, list: bool = True, bulk_update: bool = True, bulk_delete: bool = True):
	actions = {
		HttpVerbs.GET: (CrudMethods.list if list == True else CrudMethods.not_found),
		HttpVerbs.POST: (CrudMethods.create if create == True else CrudMethods.not_found),
		HttpVerbs.PUT: (CrudMethods.bulk_update if bulk_update == True else CrudMethods.not_found),
		HttpVerbs.DELETE: (CrudMethods.bulk_delete if bulk_delete == True else CrudMethods.not_found),
	}
	return path("", cls.as_view(actions=actions))


class ApiCrudRoutes:
	_api_input_is_validated: bool = False
	_api_permission_is_validated: bool = False

	@classmethod
	def crud_routes(cls, create: bool = True, retrieve: bool = True, update: bool = True, delete: bool = True,
	                list: bool = True, bulk_update: bool = True, bulk_delete: bool = True, search: bool = True):
		return include([
			search_action_routes(cls, search),
			bulk_action_routes(cls, create, list, bulk_update, bulk_delete),
			single_action_routes(cls, retrieve, update, delete),
		])

	@classmethod
	def _validate_api_input(cls, action: str, inp=None, unknown=True, bulk=False, rule=None):
		if not cls._api_input_is_validated:

			if cls.validation_schema_class is None:
				raise ApiViewsetExceptions.SchemaValidationClassNotDefined
			_validation_rule = rule if isinstance(rule, ValidationSchema) else \
				cls.validation_schema_class.get(action, default=ValidationSchema())
			validation_errors = validate_against(schema=_validation_rule, inp=inp, unknown=unknown, bulk=bulk)

			if validation_errors is not None:
				raise ValidationExceptions.InvalidPayloadException(errors=validation_errors)

	def _validate_api_payload(self, schema: ValidationSchema, unknown=False, bulk: bool = False):
		_payload = getattr(self, 'payload', ([] if bulk else {}))
		if (validation_errors := validate_against(schema=schema, inp=_payload, unknown=unknown, bulk=bulk)) is not None:
			raise ValidationExceptions.InvalidPayloadException(errors=validation_errors)


def evaluate_execution_time(_func):
	def wrapper(self, request, *args, **kwargs):
		if not Config.is_dev_or_test_or_stage_env():
			return _func(self, request, *args, **kwargs)

		# Capture the start time of the request
		start_time = timezone.now()

		# execute the api function
		response = _func(self, request, *args, **kwargs)

		# Calculate the elapsed time
		end_time = timezone.now()

		# calculate execution time
		execution_time = end_time - start_time

		# convert time to seconds

		execution_time = '{:.2f} milliseconds'.format(execution_time.total_seconds() * 1000)

		# Append the elapsed time to the response
		getattr(response, 'data', {}).update({'execution_time': execution_time})

		return response

	return wrapper

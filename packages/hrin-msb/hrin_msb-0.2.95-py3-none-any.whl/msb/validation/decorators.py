from functools import wraps

from .utils import (validate_inp_payload, validate_inp_parameters, Request, ValidationSchema)


def validation_schema_wrapper(klass):
	def get(key: str, default=None) -> ValidationSchema | None:
		if hasattr(klass, key) and isinstance((schema := getattr(klass, key)), ValidationSchema):
			return schema
		return default

	setattr(klass, "get", get)
	return klass


def api_inputs(payload_schema: ValidationSchema = None, param_schema: ValidationSchema = None, **opt):
	allow_unknown = opt.get("unknown") == True
	bulk_inp = opt.get("bulk_inp") == True

	def outer_func(_func):
		@wraps(_func)
		def inner_func(cls, request: Request, *args, **kwargs):
			"""
			validate parameter data like from URL/Query string if parameter validation rules are defined
			"""
			if isinstance(param_schema, ValidationSchema):
				validate_inp_parameters(param_schema, kwargs, allow_unknown=True)

			"""
			validate payload data if payload rules are defined
			"""
			if isinstance(payload_schema, ValidationSchema):
				validate_inp_payload(payload_schema, request, allow_unknown, bulk_inp)

			cls._api_input_is_validated = True
			return _func(cls, *args, **dict(request=request, **kwargs))

		return inner_func

	return outer_func


def verify_search_employee_list(key: str = 'employee_number', parent_key: str = 'filters'):
	def decorator_function(func):
		@wraps(func)
		def wrapper_function(cls, request, *args, **kwargs):
			"""
			This function takes the key for employee number in search.
			It validates all the employee numbers in the payload if employee number is provided else will
			return the employee numbers of all the employee data the user has access to.
			"""
			# Get the employee number from the payload and make sure it is list
			employees = cls.payload[parent_key].get(key) or []
			employees_list = employees if type(employees) is list else [employees]
			# Validate and update the employee list
			cls.payload[parent_key].update({key: cls.user.get_validated_employee_list(*employees_list)})
			return func(cls, request, *args, **kwargs)

		return wrapper_function

	return decorator_function

import logging

from requests.models import Response
from msb.env import (Config)
from user_agents.parsers import UserAgent

from .dataclasses import ApiRequestData, ApiResponseWrapper
from .exceptions import ApiRequestExceptions


def make_api_request(request_data: ApiRequestData) -> ApiResponseWrapper:
	from requests import (api, ConnectionError)
	api_response = Response()
	try:
		request_parameters = request_data.get_request_parameters()
		api_response = api.request(**request_parameters)
	except ConnectionError as ce:
		if Config.is_local_env():
			logging.exception(ce)
		raise ApiRequestExceptions.ResourceNotFound
	except Exception as e:
		if Config.is_local_env():
			logging.exception(e)
		raise ApiRequestExceptions.InternalServerError

	return ApiResponseWrapper(api_response)


def get_user_agent_from_request(request) -> UserAgent:
	import user_agents
	user_agent_string = request.META.get('HTTP_USER_AGENT', '')
	return user_agents.parse(user_agent_string)

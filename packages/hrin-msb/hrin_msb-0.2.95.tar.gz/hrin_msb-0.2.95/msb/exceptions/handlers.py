import logging

from ._exception import AppException


class MsbExceptionHandler:

	@staticmethod
	def handle_exception(e):
		logging.exception(e)

	@staticmethod
	def handle_error(e):
		logging.error(f"Error : {e}")

	@staticmethod
	def raise_exceptions(e: AppException|Exception, alternate_exc: AppException|Exception = None, silent=False):
		if not silent:
			raise (e if isinstance(e, AppException) else alternate_exc)

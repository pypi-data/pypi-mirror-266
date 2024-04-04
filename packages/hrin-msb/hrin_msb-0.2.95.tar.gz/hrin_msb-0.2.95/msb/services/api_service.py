from typing import List, Dict

from django.core.exceptions import FieldDoesNotExist
from django.db import (IntegrityError, )
from django.db.models.query import QuerySet

from msb.dataclasses import SearchParameter
from msb.db import constants as _const
from msb.db.models import MsbModel
from .exceptions import ApiServiceExceptions
from .msb_service import MsbService


class ApiService(MsbService):
	db_model: MsbModel = MsbModel
	exception_class_name: ApiServiceExceptions | None = None

	@property
	def exception_class(self) -> ApiServiceExceptions:
		if not isinstance(self.exception_class_name, ApiServiceExceptions):
			return ApiServiceExceptions
		return self.exception_class_name

	def get_meta_field_data(self, field_name: str, field_value) -> Dict:
		if hasattr(self.db_model, field_name) and str(field_value).isnumeric():
			return {field_name: field_value}
		return {}

	def __parsed_pk_value(self, pk: str | int):
		if isinstance(pk, int) or str(pk).isnumeric():
			return int(pk)

		if (pk := self.cipher.decipher(pk)) in [None, '']:
			raise ApiServiceExceptions.InvalidPk(resource=self.service_name_value)
		return pk

	def __init__(self):
		if self.db_model is None or self.db_model._meta.model_name == MsbModel._meta.model_name:
			raise ApiServiceExceptions.InvalidDatabaseModel(resource=self.service_name_value)

	def search(self, params: SearchParameter) -> Dict:
		result = dict(count=0, records=[])
		try:
			model_query = params.get_query(self.db_model)
			result['count'] = model_query.count()
			model_query = model_query.all()[params.offset:params.offset + params.limit]
			result['records'] = [i.dict() for i in model_query]
		except FieldDoesNotExist as fde:
			raise ApiServiceExceptions.InvalidSearchField(resource=self.service_name_value)
		except Exception as e:
			self.raise_exceptions(e, ApiServiceExceptions.SearchOperationFailed(resource=self.service_name_value, errors=e))
		return result

	def create(self, *model_data_list, user_id=None) -> bool | MsbModel | List[MsbModel]:
		try:
			if len(model_data_list) == 0:
				raise ApiServiceExceptions.InvalidDataForCreateOperation(resource=self.service_name_value)

			created_by = self.get_meta_field_data(_const.COLUMN_NAME_CREATED_BY, user_id)

			if len(model_data_list) == 1:
				model_data = model_data_list[0]
				_model = self.db_model(**{**model_data, **created_by})
				_model.save()
				return _model
			else:
				_model_list = [self.db_model({**model_data, **created_by}) for model_data in model_data_list]
				self.db_model.objects.bulk_create(_model_list)
				return _model_list
		except IntegrityError as ie:
			raise ApiServiceExceptions.DuplicateEntry(resource=self.service_name_value)
		except Exception as e:
			self.raise_exceptions(e, ApiServiceExceptions.CreateOperationFailed(resource=self.service_name_value))

	def retrieve(self, pk=None, silent=False):
		try:
			pk = self.__parsed_pk_value(pk)
			return self.db_model.objects.retrieve(pk=pk)
		except self.db_model.DoesNotExist:
			raise ApiServiceExceptions.ResourseDoesNotExists(resource=self.service_name_value)
		except Exception as e:
			self.raise_exceptions(e, ApiServiceExceptions.RetrieveOperationFailed(resource=self.service_name_value), silent)
		return None

	def list(self, limit: int = _const.DEFAULT_QUERY_LIMIT, offset: int = _const.DEFAULT_QUERY_OFFSET) -> QuerySet | None:
		try:
			offset = int(offset) if str(offset).isnumeric() else _const.DEFAULT_QUERY_OFFSET
			limit = int(limit) if str(limit).isnumeric() else _const.DEFAULT_QUERY_LIMIT

			fields = [
				i for i in self.db_model._list_field_names
				if (x := getattr(self.db_model, i, None)) and not isinstance(x, property)
			]
			data_set = self.db_model.objects.only(*fields).all()
			return data_set[offset:(limit + offset)] if len(fields) > 0 else None
		except Exception as e:
			self.raise_exceptions(e, ApiServiceExceptions.ListOperationFailed(resource=self.service_name_value))

	def update(self, pk=None, user_id=None, **model_data) -> bool:
		try:
			pk = self.__parsed_pk_value(pk)

			if not (model_object := self.db_model.objects.filter(pk=pk)).exists():
				raise ApiServiceExceptions.ResourseDoesNotExists(resource=self.service_name_value)

			model_data.update(self.get_meta_field_data(_const.COLUMN_NAME_UPDATED_BY, user_id))

			if not (status := model_object.update(**model_data)):
				raise ApiServiceExceptions.UpdateOperationFailed(resource=self.service_name_value)
			return bool(status)
		except IntegrityError as ie:
			raise ApiServiceExceptions.DuplicateEntry(resource=self.service_name_value)
		except Exception as e:
			self.raise_exceptions(e, ApiServiceExceptions.UpdateOperationFailed(resource=self.service_name_value))

	def delete(self, pk=None, user_id=None) -> bool:
		try:
			pk = self.__parsed_pk_value(pk)
			model_object = self.retrieve(pk=pk)
			delete_kwargs = self.get_meta_field_data(_const.COLUMN_NAME_DELETED_BY, user_id)
			if not (status := model_object.delete(**delete_kwargs)):
				raise ApiServiceExceptions.DeleteOperationFailed(resource=self.service_name_value)
			return bool(status)
		except Exception as e:
			self.raise_exceptions(e, ApiServiceExceptions.DeleteOperationFailed(resource=self.service_name_value))

from dataclasses import dataclass
from typing import (AnyStr, Tuple, List, Dict)

from msb.cipher import Cipher
from msb.db.constants import (DEFAULT_QUERY_OFFSET, DEFAULT_QUERY_LIMIT)


@dataclass
class SearchParameter:
	# this is what goes to the search
	_model_filters: Dict
	_fields: List
	_order_by: AnyStr
	_limit: int
	_offset: int
	_order_field: str
	# this is what we recieve from payload
	_raw_filters: Dict

	# this is what we is declared beforehand
	_model_filter_map: Dict
	_auto_decrypt_filters: List

	def get_query(self, for_model=None):
		try:
			self._init_model_filters(model=for_model)
			_filter_list, _filter_dict = self.compound_filters, self.filters
			_query_fields, _query_properties = self._extract_query_fields_and_properties(for_model)

			query_set = for_model.objects.from_all

			if len(_filter_list) > 0:
				query_set = query_set.filter(*_filter_list, **_filter_dict)
			else:
				query_set = query_set.filter(**_filter_dict)

			if len(_query_fields) > 0:
				query_set = query_set.only(*_query_fields)

			if len(_query_properties) > 0:
				for_model.add_query_properties(*_query_properties)

			if self.order_field:
				query_set = query_set.order_by(self.order_field)
			return query_set
		except Exception as e:
			raise e

	def _init_model_filters(self, model=None):
		for key, value in self._raw_filters.items():
			if value is None: continue
			value = self.__parse_value(key=key, value=value, model=model)

			if key in self.model_filter_map.keys():
				self.add_filters(self.model_filter_map[key], value)
			elif hasattr(model, key):
				self.add_filters(key, value)

	def _extract_query_fields_and_properties(self, model=None):
		_model_fields, _model_properties = [], []
		if self.fields:
			for f in self.fields:
				if isinstance(getattr(model, f, None), property):
					_model_properties.append(f)
				else:
					_model_fields.append(f)

		return _model_fields, _model_properties

	def __parse_value(self, key, value, model):
		return Cipher.decipher(value) if key in self.auto_decrypt_fields_list(model) else value

	def __init__(self, **kwargs):
		self._model_filters = dict()
		self._fields = kwargs.get('fields', [])
		self._order_by = kwargs.get('order_by', 'ASC')
		self._limit = kwargs.get('limit', DEFAULT_QUERY_LIMIT)
		self._offset = kwargs.get('offset', DEFAULT_QUERY_OFFSET)
		self._order_field = kwargs.get('order_field', None)
		self._raw_filters = kwargs.get('filters', {})

	def add_filters(self, key: str, value):
		if key and value not in ['', None, []]:
			self._model_filters[key] = value

	def auto_decrypt_fields_list(self, model):
		_secure_field_list = self.auto_decrypt_filters
		_secure_field_list.append(model._meta.pk.attname)
		_private_fields = getattr(model, "_private_fields", [])
		if isinstance(_private_fields, list):
			_secure_field_list.extend(_private_fields)
		return _secure_field_list

	@property
	def compound_filters(self) -> List | Tuple:
		return []

	@property
	def model_filter_map(self) -> dict:
		return getattr(self, "_model_filter_map", dict())

	@property
	def auto_decrypt_filters(self) -> list:
		return getattr(self, "_auto_decrypt_filters", list())

	@property
	def filters(self) -> dict:
		return self._model_filters

	@property
	def fields(self) -> list:
		return self._fields if isinstance(self._fields, list) and len(self._fields) > 0 else None

	@property
	def order_by(self) -> str:
		return self._order_by

	@property
	def limit(self) -> int:
		try:
			return int(self._limit) if int(self._limit) > 0 else DEFAULT_QUERY_LIMIT
		except Exception:
			return 0

	@property
	def offset(self) -> int:
		try:
			return int(self._offset) if int(self._offset) >= 0 else DEFAULT_QUERY_OFFSET
		except Exception:
			return 0

	@property
	def order_field(self) -> str:
		if self._order_field is not None:
			return f"-{self._order_field}" if str(self.order_by).upper() != 'ASC' else self._order_field
		return None


@dataclass
class SearchParameterRequest:
	fields: List
	filters: Dict
	limit: int
	offset: int
	order_field: str | None
	order_by: str | None

	def __init__(self, **kwargs):
		self.fields = kwargs.get('fields') or []
		self.filters = kwargs.get('filters') or dict()
		self.limit = kwargs.get('limit') or DEFAULT_QUERY_LIMIT
		self.offset = kwargs.get('offset') or DEFAULT_QUERY_OFFSET
		self.order_field = kwargs.get('order_field')
		self.order_by = kwargs.get('order_by')

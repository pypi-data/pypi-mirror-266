from functools import cache

from django.conf import settings
from django.core.serializers import serialize
from django.db import models as Models
from django.utils.functional import cached_property

from msb.cipher import Cipher
from .constants import (COLUMN_NAME_DELETED, COLUMN_NAME_DELETED_BY)
from .msb_model_manager import MsbModelManager


class MsbModel(Models.Model):
	_private_fields: list = []
	_protected_fields: list = []
	_list_field_names: list = []
	_identifier_field: str = ""

	_encrypt_private_fields: bool = settings.MSB_DB_ENCRYPT_PRIVATE_FIELDS
	_encrypt_protected_fields: bool = settings.MSB_DB_ENCRYPT_PROTECTED_FIELDS
	_pk_is_private_fields: bool = settings.MSB_DB_PK_IS_PRIVATE_FIELD
	_hidden_fields: list = []
	_query_properties: list = []

	class Meta:
		abstract = True

	@property
	def pk_name(self):
		return self._meta.pk.attname

	@property
	def pk_value(self):
		return getattr(self, self.pk_name) if self.pk_name is not None else ""

	@property
	def identifier(self):
		return f"{getattr(self, self.identifier_field_name)}" if hasattr(self, self.identifier_field_name) else ""

	@property
	def rows(self):
		return self.objects

	@classmethod
	def add_query_properties(cls, *properties):
		cls._query_properties.extend(properties)

	objects = MsbModelManager()

	@property
	def serialized(self):
		return serialize('python', [self])

	def delete(self, deleted_by=None, using=None, keep_parents=False):
		if hasattr(self, COLUMN_NAME_DELETED):
			setattr(self, COLUMN_NAME_DELETED, True)

		if hasattr(self, COLUMN_NAME_DELETED_BY):
			setattr(self, COLUMN_NAME_DELETED_BY, deleted_by)
		self.save()
		return True

	def recover(self):
		if hasattr(self, COLUMN_NAME_DELETED):
			setattr(self, COLUMN_NAME_DELETED, False)
		self.save()
		return True

	@property
	def encrypted_fields(self) -> list:
		_secure_fields = self._private_fields if isinstance(self._private_fields, list) else []
		if self._pk_is_private_fields:
			_secure_fields.append(self._meta.pk.attname)
		return _secure_fields

	@property
	def encoded_fields(self) -> list:
		return self._protected_fields if isinstance(self._protected_fields, list) else []

	@property
	def identifier_field_name(self):
		if isinstance(self._identifier_field, str) and len(self._identifier_field) > 0:
			return self._identifier_field
		return ''

	@property
	def related_fields(self):
		fields = []
		for field in self._meta.fields:
			if field.get_internal_type() in ['ForeignKey', 'ManyToManyField']:
				fields.append(field.name)
		return fields

	@property
	def list_fields(self) -> dict:
		return self._get_field_values(
			*[self.pk_name, *self._list_field_names] if isinstance(self._list_field_names, list) else []
		)

	def __formatted_field_value(self, field_name: str, field_value: str, force_encrypt: bool = False):
		if field_name in self.encrypted_fields and (force_encrypt or self._encrypt_private_fields):
			return Cipher.encrypt(field_value)
		elif field_name in self.encoded_fields and (force_encrypt or self._encrypt_protected_fields):
			return Cipher.encode_base64(field_value)
		else:
			return field_value

	def _field_value(self, field_name: str, default=None):
		try:
			if "." in field_name:
				field_name, relation_name, *_ = field_name.split(".")
				local_field_value = getattr(self, field_name, default)
				field_value = local_field_value._get_field_value(relation_name, default=None)
			else:
				field_value = getattr(self, field_name, default)
				if isinstance(field_value, MsbModel):
					field_value = field_value._field_value(field_value.pk_name)

		except Exception as e:
			field_value = default
		return field_value

	@cache
	def __should_fetch_field(self, field_name: str, include_properties: bool) -> bool:
		_should_fetch = not any([
			field_name.startswith('_'),
			field_name in self._hidden_fields,
			(isinstance(field_name, property) and not include_properties),
		])
		return _should_fetch

	def _get_field_values(
			self, *field_names, default=None, force_encrypt: bool = False, include_properties: bool = False):
		try:
			return {
				field_name.replace('.', '_'): self.__formatted_field_value(
					field_name, self._field_value(field_name, default), force_encrypt
				) for field_name in field_names
				if self.__should_fetch_field(field_name, include_properties)
			}
		except Exception as e:
			return dict()

	def dict(self, encrypted: bool = False, include_properties: bool = False) -> dict:
		_model_fields = [*self.__dict__.keys(), *getattr(self, '_query_properties', [])]
		return self._get_field_values(*_model_fields, force_encrypt=encrypted, include_properties=include_properties)

	def __str__(self):
		return f"<{self.__class__.__name__} [{self.pk_value}]: {self.identifier}>"

	def __unicode__(self):
		return self.__str__()

	def __repr__(self):
		return self.__str__()

	@classmethod
	def has_model_field(cls, field_name: str) -> bool:
		return all([
			hasattr(cls, field_name),
			type(getattr(cls, field_name, None)) not in [property, cached_property],
			not field_name.startswith('_'),
		])

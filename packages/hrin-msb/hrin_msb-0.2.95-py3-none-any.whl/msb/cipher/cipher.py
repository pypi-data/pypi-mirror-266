import base64

import jwt

from .asymmetric_cipher import AsymmetricCipher
from .exceptions import CipherExceptions
from .symmetric_cipher import SymmetricCipher


class Cipher:

	@staticmethod
	def get_instance(asymetric=False):
		if asymetric:
			cipher = AsymmetricCipher()
		else:
			cipher = SymmetricCipher()
		return cipher

	@staticmethod
	def encrypt(data=None, asymetric=False):
		try:
			if data is None:
				raise CipherExceptions.NoneValue
			return Cipher.get_instance().encrypt(data)
		except Exception:
			return data

	@staticmethod
	def decrypt(data=None, asymetric=False):
		try:
			if data is None:
				raise CipherExceptions.NoneValue
			return Cipher.get_instance().decrypt(data)
		except Exception:
			return data

	@staticmethod
	def decrypt_list_items(*datalist, asymetric=False):
		try:
			return [Cipher.decrypt(i) for i in datalist]
		except Exception as e:
			return datalist

	@staticmethod
	def encrypt_list_items(*datalist, asymetric=False):
		try:
			return [Cipher.encrypt(i) for i in datalist]
		except Exception as e:
			return datalist

	@staticmethod
	def encode_base64(value):
		return base64.b64encode(bytes(str(value), 'utf-8'))

	@staticmethod
	def decode_base64(value, validate=False):
		return base64.b64decode(bytes(str(value), 'utf-8'), validate=validate).decode()

	@staticmethod
	def __auto_decipher(value: str):
		if not value.__str__().isnumeric():
			try:
				return Cipher.decode_base64(value, validate=True)
			except Exception as be:
				return Cipher.decrypt(value)
		return value

	@staticmethod
	def decipher(value: list | str):
		return [Cipher.__auto_decipher(i) for i in value] if isinstance(value, list) else Cipher.__auto_decipher(value)

	@staticmethod
	def decode_jwt(value, verify=False, **kwargs):
		try:
			algorithm = jwt.get_unverified_header(value).get("alg", 'HS256')
			return jwt.decode(value, options={"verify_signature": verify}, algorithm=algorithm, **kwargs)
		except (jwt.DecodeError, jwt.InvalidTokenError, Exception) as e:
			return value

	@staticmethod
	def encode_jwt(value, **kwargs):
		try:
			return jwt.encode(value, **kwargs)
		except Exception as e:
			return value

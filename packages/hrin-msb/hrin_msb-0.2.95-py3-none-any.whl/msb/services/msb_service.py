from msb.cipher import Cipher
from msb.dataclasses import Singleton
from msb.exceptions import MsbExceptionHandler


class MsbService(MsbExceptionHandler, metaclass=Singleton):
	service_name: str = None

	@property
	def cipher(self) -> Cipher:
		return Cipher

	@property
	def service_name_value(self) -> str | None:
		try:
			if not self.service_name:
				import re
				class_name = re.split('(?<=.)(?=[A-Z])', self.__class__.__name__.replace("Service", ""))
				return " ".join(class_name)
			return self.service_name
		except Exception:
			return None

	def __str__(self):
		return f"<MsbService: {self.service_name_value}>"

	def __repr__(self):
		return self.__str__()

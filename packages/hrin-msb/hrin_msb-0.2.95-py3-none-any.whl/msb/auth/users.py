from functools import cache

from django.utils.functional import cached_property

from .constants import AccessLevelsConst, RoleConst
from .exceptions import MsbAuthExceptions
from .token import AuthToken


class TokenUser(AuthToken):

	@cached_property
	def username(self):
		return self.session.get('username', None)

	@property
	def is_authenticated(self):
		return self.session.get('is_authenticated', False) and self.is_valid

	@cached_property
	def is_admin(self):
		return (self.role.id == RoleConst.ADMIN_ROLE_ID) and self.has_management_access

	@property
	def email(self):
		return self.session.get('email', None)

	@property
	def has_management_access(self) -> bool:
		return self.session.has_management_access

	@property
	def work_id(self) -> str:
		return self.session.work_id

	@property
	def image(self) -> str:
		return self.session.image

	@property
	def permissions(self) -> dict:
		return self.session.permissions

	@property
	def login_time(self):
		return self.session.login_time

	@property
	def location(self):
		return self.session.location

	@property
	def role(self):
		return self.session.role

	@property
	def subscriptions(self) -> str:
		return str(self.session.subscriptions)

	@property
	def dr_list(self):
		return self.session.dr_list

	def has_access_to(self, subscription_name: str) -> bool:
		return subscription_name in self.subscriptions.split(",")

	@cache
	def validate_employee_data_access(self, *user_ids) -> bool:
		""" This function raises an exception if the user is not authorized to access the employee data."""
		user_ids = map(lambda x: str(x), user_ids)
		if self.role.access_level == AccessLevelsConst.SELF:
			raise MsbAuthExceptions.UnauthorizedAccessToUserData

		if self.role.access_level == AccessLevelsConst.DIRECT_REPORTIES:
			if not set(user_ids).issubset(set(self.dr_list)):
				raise MsbAuthExceptions.UnauthorizedAccessToUserData

		# TODO : Add support for other access types.(RESTRICTED_EVERYONE)
		return True

	@cache
	def get_validated_employee_list(self, *user_ids: list | tuple) -> list | tuple:
		""" This function returns the list of employee ids that are authorized to access the employee data."""
		if isinstance(user_ids, list | tuple) and len(user_ids) > 0:
			self.validate_employee_data_access(*user_ids)
			return user_ids
		return self.get_accessible_employee_list()

	def get_accessible_employee_list(self) -> list:
		if self.role.access_level == AccessLevelsConst.DIRECT_REPORTIES:
			return self.dr_list if len(self.dr_list) else [self.userid]
		elif self.role.access_level == AccessLevelsConst.ALL or self.role.access_level == AccessLevelsConst.RESTRICTED_ALL:
			return []
		else:
			return [self.userid]

	def has_role(self, role) -> bool:
		return int(role) == self.role.id

	def has_role_permission(self, *permissions):
		return any([permission().has_role_permission(self) for permission in permissions])

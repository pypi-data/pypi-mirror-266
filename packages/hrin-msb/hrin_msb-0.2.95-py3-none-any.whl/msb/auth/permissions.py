from functools import cached_property

from rest_framework.permissions import BasePermission

from .constants import RoleConst
from .exceptions import MsbAuthExceptions
from .users import TokenUser


class Permissions:
	"""
		Default Permissions
	"""

	class Authenticated(BasePermission):
		def is_authenticated(self, request) -> bool:
			return request.user and request.user.is_authenticated

		def has_permission(self, request, view) -> bool:
			return self.is_authenticated(request)

	class IntraService(Authenticated):
		def has_permission(self, request, view) -> bool:
			return bool(self.is_authenticated(request) and request.user.is_intra_service_requester)

	class AuthenticatedUser(Authenticated):
		allowed_role_ids: list = RoleConst.ALL_USER_ROLE_IDS
		admin_is_allowed_by_default: bool = True

		@cached_property
		def __get_allowed_role_ids(self) -> list:
			allowed_ids: list = self.allowed_role_ids if isinstance(self.allowed_role_ids, list) else []
			if self.admin_is_allowed_by_default:
				allowed_ids.append(RoleConst.ADMIN_ROLE_ID)
			return allowed_ids

		def has_role_permission(self, user: TokenUser) -> bool:
			if len(self.__get_allowed_role_ids) > 0:
				return any([user.has_role(role=role_id) for role_id in self.__get_allowed_role_ids])
			return True

		def has_permission(self, request, view) -> bool:
			is_authenticated = self.is_authenticated(request)
			has_role_permission = self.has_role_permission(request.user)
			return is_authenticated and has_role_permission

		def has_object_permission(self, request, view, obj):
			return True

		@classmethod
		def check_role_permission(cls, *args, **kwargs):
			return cls()

		def check(self, request, view, obj=None) -> bool:
			if not self.has_permission(request, view, ) and self.has_object_permission(request, view, obj):
				raise MsbAuthExceptions.UnauthorizedAccess
			return True

	class Management(AuthenticatedUser):
		def has_permission(self, request, view) -> bool:
			return bool(super().has_permission(request, view) and request.user.has_management_access)

	class ManagementOrIntraService(Authenticated):
		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(
				super().has_permission(request, view) and
				(_user.has_management_access or _user.is_intra_service_requester)
			)

	"""
		Role Permissions
	"""

	class AdminRole(Management):
		def has_permission(self, request, view) -> bool:
			return bool(super().has_permission(request, view) and request.user.is_admin)

	"""
		Manager Role Permissions
	"""

	class ManagerRole(Management):
		allowed_role_ids = RoleConst.ALL_MANAGER_ROLE_IDS

	class ResourceManagerRole(ManagerRole):
		allowed_role_ids = [RoleConst.RESOURCE_MANAGER_ROLE_ID]

	class FinanceManagerRole(Management):
		allowed_role_ids = [RoleConst.FINANCE_MANAGER_ROLE_ID]

	class HrManagerRole(Management):
		allowed_role_ids = [RoleConst.HR_MANAGER_ROLE_ID]

	class OperationsManagerRole(Management):
		allowed_role_ids = [RoleConst.OPERATIONS_MANAGER_ROLE_ID]

	class ItManagerRole(Management):
		allowed_role_ids = [RoleConst.OPERATIONS_MANAGER_ROLE_ID]

		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_role(RoleConst.IT_MANAGER_ROLE_ID))

	"""
		Employee Role Permissions
	"""

	class EmployeeRole(AuthenticatedUser):
		allowed_role_ids = RoleConst.ALL_MANAGER_AND_EMPLOYEE_ROLE_IDS

	class HrEmployeeRole(Management):
		allowed_role_ids = [RoleConst.HR_EMPLOYEE_ROLE_ID, RoleConst.HR_MANAGER_ROLE_ID]

	class FinanceEmployeeRole(Management):
		allowed_role_ids = [RoleConst.FINANCE_MANAGER_ROLE_ID, RoleConst.FINANCE_EMPLOYEE_ROLE_ID]

	class OperationsEmployeeRole(Management):
		allowed_role_ids = [RoleConst.OPERATIONS_MANAGER_ROLE_ID, RoleConst.OPERATIONS_EMPLOYEE_ROLE_ID]

	class ItEmployeeRole(Management):
		allowed_role_ids = [RoleConst.IT_MANAGER_ROLE_ID, RoleConst.IT_EMPLOYEE_ROLE_ID]

	class ApplicationQaRole(Management):
		allowed_role_ids = [RoleConst.APPLICATION_QA_ROLE_ID, RoleConst.ADMIN_ROLE_ID]

	class GuestRole(AuthenticatedUser):
		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_role(RoleConst.GUEST_ROLE_ID))

	class ContractorRole(AuthenticatedUser):
		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_role(RoleConst.CONTRACTOR_ROLE_ID))

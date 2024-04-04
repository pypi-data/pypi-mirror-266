from celery import Celery
from django.conf import settings

from msb.env import NameConst, MsbConfigNames
from .msb_service import MsbService


class MsbQueue:

	def __init__(self, queue, **kwargs):
		self.celery = Celery()
		self.__queue = queue
		self.__service = kwargs.get('service', settings.MSB_SERVICE_NAME)

	@property
	def queue(self) -> str:
		return self.__queue

	@property
	def service(self) -> str:
		return self.__service

	def publish(self, task_name, data, **options):
		self.celery.send_task(name=task_name, queue=self.queue, args=[self.service], kwargs=data, **options)

	def __str__(self):
		return f'<{self.__class__.__name__} {self.queue} : {self.service} >'

	def __repr__(self):
		return self.__str__()


class QueueService(MsbService):

	@property
	def user_service_queue(self) -> MsbQueue:
		return MsbQueue(queue=NameConst.USER_SERVICE_QUEUE_NAME)

	@property
	def leave_service_queue(self) -> MsbQueue:
		return MsbQueue(queue=NameConst.LEAVE_SERVICE_QUEUE_NAME)

	@property
	def employee_service_queue(self) -> MsbQueue:
		return MsbQueue(queue=NameConst.EMPLOYEE_SERVICE_QUEUE_NAME)

	@property
	def project_service_queue(self) -> MsbQueue:
		return MsbQueue(queue=NameConst.PROJECT_SERVICE_QUEUE_NAME)

	@property
	def notification_service_queue(self) -> MsbQueue:
		return MsbQueue(queue=NameConst.NOTIFICATION_SERVICE_QUEUE_NAME)

	@property
	def autopilot_service_queue(self) -> MsbQueue:
		return MsbQueue(queue=NameConst.AUTOPILOT_SERVICE_QUEUE_NAME)


	def broadcast_to(self, *queues, task_name, data, **kwargs):
		for queue in queues:
			MsbQueue(queue=queue).publish(task_name=task_name, data=data, **kwargs)

	def brodcast(self, task_name, data, **kwargs):
		self.broadcast_to(
			*getattr(settings, MsbConfigNames.MSB_DEFAULT_BRODCAST_QUEUES, []),
			task_name=task_name, data=data, **kwargs
		)

	def get_queue(self, queue_name: str) -> MsbQueue:
		return MsbQueue(queue=queue_name)

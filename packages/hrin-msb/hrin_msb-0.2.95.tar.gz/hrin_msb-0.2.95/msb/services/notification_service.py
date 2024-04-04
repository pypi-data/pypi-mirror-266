from django.conf import settings

from msb.dataclasses.notification import (NotificationData, EmailNotificationData, YammerNotificationData)
from .exceptions import NotificationServiceExceptions
from .queue_service import (MsbQueue, MsbService, NameConst)


class NotificationService(MsbService):

	def __init__(self, **kwargs):
		super().__init__()
		self.queue = MsbQueue(
			queue=kwargs.get('queue', settings.MSB_NOTIFICATION_QUEUE_NAME),
			service=kwargs.get('service', settings.MSB_SERVICE_NAME)
		)

	def send_notification_task(self, data: NotificationData = None, task_name: str = NameConst.ASYNC_TASK_NAME):
		try:
			if not isinstance(data, NotificationData):
				raise NotificationServiceExceptions.InvalidNotificationData

			self.queue.publish(task_name=task_name, data=data.__dict__)
		except Exception as e:
			self.raise_exceptions(e, NotificationServiceExceptions.NotificationSendFailed())

	def send_email_notification(self, data: EmailNotificationData = None, task: str = None):
		return self.send_notification_task(
			data, (task or getattr(settings, 'MSB_EMAIL_NOTIFICATION_TASK_NAME', NameConst.EMAIL_NOTIFICATION_TASK_NAME))
		)

	def send_bulk_email_notification(self, data: list = None, task: str = None):
		raise NotImplementedError

	def send_yammer_notification(self, data: YammerNotificationData = None, task: str = None):
		return self.send_notification_task(
			data, (task or getattr(settings, 'MSB_YAMMER_NOTIFICATION_TASK_NAME', NameConst.YAMMER_NOTIFICATION_TASK_NAME))
		)


__all__ = ['NotificationService', 'NotificationData', 'EmailNotificationData', 'YammerNotificationData']

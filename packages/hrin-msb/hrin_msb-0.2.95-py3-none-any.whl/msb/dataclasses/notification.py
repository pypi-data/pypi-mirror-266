class NotificationData:

	def __init__(self, **kwargs):
		self.subject = kwargs.get('subject', "")
		self.template = kwargs.get('template', "")
		self.recipients = kwargs.get('recipients', [])
		self.context = kwargs.get('context', {})
		self.body = kwargs.get('body', "")
		self.attachments = kwargs.get('attachments', [])

	def set_body(self, body):
		self.body = body
		return self

	def set_subject(self, subject):
		self.subject = subject
		return self

	def set_template(self, template):
		self.template = template
		return self

	def add_recipients(self, *recipients):
		self.recipients.extend(recipients)
		return self

	def add_context(self, **context):
		self.context.update(context)
		return self

	def add_file(self, path: str, name: str = None, content_type: str = None):
		self.attachments.append(dict(path=path, filename=name, content_type=content_type))
		return self


class EmailNotificationData(NotificationData):

	def __init__(self, **kwargs):
		super(EmailNotificationData, self).__init__(**kwargs)
		self.sender = kwargs.get('sender', "")
		self.cc = kwargs.get('cc', [])
		self.bcc = kwargs.get('bcc', [])
		self.priority = kwargs.get('priority', 1)

	def set_sender(self, sender):
		self.sender = sender
		return self

	def add_cc(self, *cc):
		self.cc.extend(cc)
		return self

	def add_bcc(self, *bcc):
		self.bcc.extend(bcc)
		return self

	def add_attachment_list(self, **attachements):
		for attachement in attachements:
			self.add_file(**attachement)

	def set_priority(self, priority):
		self.priority = priority
		return self


class YammerNotificationData(NotificationData):

	def __init__(self, **kwargs):
		super(YammerNotificationData, self).__init__(**kwargs)
		self.body = kwargs.get('body', "")
		self.cc = kwargs.get('cc', [])

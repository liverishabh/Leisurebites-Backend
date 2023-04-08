import enum
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
from typing import Dict, Any, List

from jinja2 import BaseLoader, Environment

from app.config import config
from app.dependencies.logger import ApplicationLogger
from app.dependencies.ses import ses_utils
from app.dependencies.smtp import smtp_utils

logger = ApplicationLogger.get_logger(__name__)


class EmailServiceProviderEnum(str, enum.Enum):
    ses = "ses"
    smtp = "smtp"


class EmailSender:
    def __init__(self) -> None:
        self.__source_email = config.EMAIL_USERNAME
        self.__email_service_provider = config.EMAIL_SERVICE_PROVIDER
        self.__email_sender_client = None
        if self.__email_service_provider == EmailServiceProviderEnum.ses.value:
            self.__email_sender = ses_utils
        elif self.__email_service_provider == EmailServiceProviderEnum.smtp.value:
            self.__email_sender = smtp_utils
        else:
            raise ValueError("Unknown Email Service Provider")

    def get_email_message(
        self,
        destination_emails: List[str],
        email_subject: str,
        email_body: str,
        environment: Dict[str, Any] = None,
        attachment_file_path: str = None,
        attachment_file_buf: BytesIO = None,
        attachment_file_name: str = ''
    ) -> MIMEMultipart:
        email_message = MIMEMultipart()
        email_message['From'] = self.__source_email
        email_message['To'] = ", ".join(destination_emails)
        email_message['Subject'] = email_subject

        body = Environment(loader=BaseLoader).from_string(email_body)  # type: ignore
        body = body.render(**environment or {})
        email_message.attach(MIMEText(body, "html"))

        if attachment_file_path:
            with open(attachment_file_path, "rb") as attachment:
                email_payload = MIMEBase('application', 'octet-stream')
                email_payload.set_payload(attachment.read())
                encoders.encode_base64(email_payload)
                email_payload.add_header('Content-Disposition', "attachment; filename= %s" % attachment.name)

            email_message.attach(email_payload)

        if attachment_file_buf is not None and attachment_file_name != '':
            email_payload = MIMEBase('application', 'octet-stream')
            attachment_file_buf.seek(0)
            email_payload.set_payload(attachment_file_buf.read())
            encoders.encode_base64(email_payload)
            email_payload.add_header('Content-Disposition', "attachment; filename= %s" % attachment_file_name)

            email_message.attach(email_payload)

        return email_message

    def send_email(
        self,
        destination_emails: List[str],
        email_subject: str,
        email_body: str,
        environment: Dict[str, Any] = None,
        attachment_file_path: str = None,
        attachment_file_buf: BytesIO = None,
        attachment_file_name: str = '',
        raise_error: bool = True
    ) -> None:
        logger.info("Sending mail to %s with subject %s", ", ".join(destination_emails), email_subject)

        try:
            email_message = self.get_email_message(
                destination_emails=destination_emails,
                email_subject=email_subject,
                email_body=email_body,
                environment=environment,
                attachment_file_path=attachment_file_path,
                attachment_file_buf=attachment_file_buf,
                attachment_file_name=attachment_file_name
            )
            self.__email_sender.send_email(
                email_message=email_message,
                source_email=self.__source_email,
                destination_emails=destination_emails
            )
        except Exception as ex:
            logger.info("Can't send email: %s", ex.__repr__())
            if raise_error:
                raise ex


email_sender = EmailSender()

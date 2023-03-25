import smtplib
from email.mime.multipart import MIMEMultipart
from typing import List

from app.config import config
from app.dependencies.logger import ApplicationLogger

logger = ApplicationLogger.get_logger(__name__)


class SMTPUtils:
    """ utility class for SMTP """
    __client = None

    def __init__(self):
        self.__email_password = config.EMAIL_PASSWORD

    def send_email(
        self,
        email_message: MIMEMultipart,
        source_email: str,
        destination_emails: List[str]
    ) -> None:
        smtp_session = smtplib.SMTP('smtp.gmail.com', 587)

        smtp_session.starttls()
        smtp_session.login(source_email, self.__email_password)

        text = email_message.as_string()
        smtp_session.sendmail(source_email, destination_emails, text)
        smtp_session.quit()

        logger.info("Email sent to %s", ", ".join(destination_emails))


smtp_utils = SMTPUtils()

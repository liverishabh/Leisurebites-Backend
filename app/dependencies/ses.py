import json
from email.mime.multipart import MIMEMultipart
from typing import List

import boto3

from app.config import config
from app.dependencies.logger import ApplicationLogger

logger = ApplicationLogger.get_logger(__name__)


class SESUtils:
    """ utility class for SES """
    __client = None

    def __init__(self):
        self.__client = boto3.client(
            service_name="ses",
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name="ap-south-1"
        )

    def send_email(
        self,
        email_message: MIMEMultipart,
        source_email: str,
        destination_emails: List[str]
    ) -> None:
        response = self.__client.send_raw_email(
            Source=source_email,
            Destinations=destination_emails,
            RawMessage={"Data": email_message.as_string()}
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            logger.info("Email sent to %s", ", ".join(destination_emails))
        else:
            logger.info("Can't send email. SES Response: %s", json.dumps(response))
            raise Exception("Sending email failed")


ses_utils = SESUtils()

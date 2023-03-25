import traceback
import boto3

from app.config import config
from app.dependencies.logger import ApplicationLogger

logger = ApplicationLogger.get_logger(__name__)


class S3Utils:
    """ utility class for s3 """
    __client = None

    def __init__(self):
        self.__client = boto3.client(
            service_name="s3",
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
        )

    def upload_file(
        self,
        local_file_path,
        cloud_file_path: str,
        bucket_name: str = config.S3_BUCKET_NAME
    ) -> bool:
        """ Uploads file to AWS S3 """
        try:
            self.__client.upload_file(local_file_path, bucket_name, cloud_file_path)

        except Exception:
            logger.error("Can't upload file")
            logger.error(traceback.format_exc())
            return False

        return True

    def upload_file_obj(
        self,
        file,
        cloud_file_path: str,
        bucket_name: str = config.S3_BUCKET_NAME
    ) -> bool:
        """ Uploads file obj to AWS S3 """
        try:
            self.__client.upload_fileobj(file, bucket_name, cloud_file_path)

        except Exception:
            logger.error("Can't upload file")
            logger.error(traceback.format_exc())
            return False

        return True


s3_utils = S3Utils()

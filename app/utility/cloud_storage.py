import enum
import hashlib
import os
import random
from datetime import datetime

from starlette.datastructures import UploadFile

from app.config import config
# from app.dependencies.gcs import gcs_utils
from app.dependencies.s3 import s3_utils


class CloudStorageProviderEnum(str, enum.Enum):
    aws = "aws"
    gcp = "gcp"


def get_cloud_file_path(
    filename: str,
    directory: str
):
    """ get file path on cloud """
    name, ext = os.path.splitext(filename)
    curr_time = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    file_name = "".join(random.sample(curr_time, len(curr_time))) + name
    cloud_file_path = directory + "/" + hashlib.md5(file_name.encode()).hexdigest() + ext

    return cloud_file_path


class CloudStorageUtils:
    """ Utility class for uploading files on Cloud Storage """

    def __init__(self):
        self.__cloud_storage_provider = config.CLOUD_STORAGE_PROVIDER
        self.__cloud_storage_utils = None
        self.__cloud_storage_bucket_url = None
        if self.__cloud_storage_provider == CloudStorageProviderEnum.aws.value:
            self.__cloud_storage_utils = s3_utils
            self.__cloud_storage_bucket_url = config.S3_BUCKET_URL
        # elif self.__cloud_storage_provider == CloudStorageProviderEnum.gcp.value:
        #     self.__cloud_storage_utils = gcs_utils
        #     self.__cloud_storage_bucket_url = config.GCS_BUCKET_URL
        else:
            raise ValueError("Invalid Cloud Storage Provider")

    def upload_file(
        self,
        file,
        cloud_file_path: str
    ):
        """
        uploads file to current in-use cloud storage service
        returns Tuple(success, complete file url)
        """
        success = False
        if isinstance(file, UploadFile):
            success = self.__cloud_storage_utils.upload_file_obj(file.file, cloud_file_path)
        elif isinstance(file, str):
            success = self.__cloud_storage_utils.upload_file(file, cloud_file_path)
        # if self.__cloud_storage_provider == CloudStorageProviderEnum.aws.value:
        #     cloud_storage_bucket_url = config.S3_BUCKET_URL
        #     if isinstance(file, UploadFile):
        #         success = s3_utils.upload_file_obj(file.file, cloud_file_path)
        #     elif isinstance(file, str):
        #         success = s3_utils.upload_file(file, cloud_file_path)
        # elif self.__cloud_storage_provider == CloudStorageProviderEnum.gcp.value:
        #     cloud_storage_bucket_url = config.GCS_BUCKET_URL
        #     if isinstance(file, UploadFile):
        #         success = gcs_utils.upload_file_obj(file.file, cloud_file_path)
        #     elif isinstance(file, str):
        #         success = gcs_utils.upload_file(file, cloud_file_path)

        if success:
            return True, f"{self.__cloud_storage_bucket_url}/{cloud_file_path}"
        else:
            return False, None


cs_utils = CloudStorageUtils()

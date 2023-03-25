# import traceback
# from google.cloud import storage
# from google.cloud.storage import Bucket, Blob
#
# from app.config import config
# from app.dependencies.logger import ApplicationLogger
#
# logger = ApplicationLogger.get_logger(__name__)
#
#
# class GCSUtils:
#     """ utility class for google cloud storage """
#     __client = None
#
#     def __init__(self):
#         self.__client = storage.Client()
#
#     def upload_file(
#             self,
#             local_file_path: str,
#             cloud_file_path: str,
#             bucket_name: str = config.GCS_BUCKET_NAME
#     ) -> bool:
#         """ Uploads file to google cloud storage """
#
#         try:
#             bucket: Bucket = self.__client.bucket(bucket_name)
#             blob: Blob = bucket.blob(cloud_file_path)
#             blob.upload_from_filename(local_file_path)
#
#         except Exception:
#             logger.error("Can't upload file")
#             logger.error(traceback.format_exc())
#             return False
#
#         return True
#
#     def upload_file_obj(
#             self,
#             file,
#             cloud_file_path: str,
#             bucket_name: str = config.GCS_BUCKET_NAME
#     ) -> bool:
#         """ Uploads file to google cloud storage """
#
#         try:
#             bucket: Bucket = self.__client.bucket(bucket_name)
#             blob: Blob = bucket.blob(cloud_file_path)
#             blob.upload_from_string(file.read(), content_type='binary/octet-stream')
#
#         except Exception:
#             logger.error("Can't upload file")
#             logger.error(traceback.format_exc())
#             return False
#
#         return True
#
#
# gcs_utils = GCSUtils()

import logging

from asgi_correlation_id import CorrelationIdFilter


class ApplicationLogger:
    @classmethod
    def get_logger(cls, module_name):
        cid_filter = CorrelationIdFilter(uuid_length=32)
        formatter = logging.Formatter(
            "%(levelname)s: \t  %(asctime)s (%(processName)s[%(process)d]) -- %(name)s(%(lineno)d) "
            "[%(correlation_id)s] -- %(message)s",
            datefmt="%d-%b-%Y %I:%M:%S %p",
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.addFilter(cid_filter)

        logger = logging.getLogger(module_name)
        logger.setLevel(logging.INFO)
        logger.addHandler(console_handler)
        logger.propagate = False

        return logger


# import logging
# from logging import handlers
# import os
#
# from asgi_correlation_id import CorrelationIdFilter
#
# from app.config import config
#
# LOG_FILE_PATH = config.LOG_FILE_DIR + '/file.log'
# ERROR_LOG_FILE_PATH = config.LOG_FILE_DIR + '/error.log'


# class ApplicationLogger:
#     @classmethod
#     def get_logger(cls, module_name):
#         if not os.path.exists(config.LOG_FILE_DIR):
#             os.makedirs(config.LOG_FILE_DIR)
#
#         cid_filter = CorrelationIdFilter(uuid_length=32)
#         formatter = logging.Formatter(
#             "%(levelname)s: \t  %(asctime)s (%(processName)s[%(process)d]) -- %(name)s(%(lineno)d) "
#             "[%(correlation_id)s] -- %(message)s",
#             datefmt="%d-%b-%Y %I:%M:%S %p",
#         )
#
#         console_handler = logging.StreamHandler()
#         console_handler.setFormatter(formatter)
#         console_handler.addFilter(cid_filter)
#
#         all_log_handler = handlers.RotatingFileHandler(
#             filename=LOG_FILE_PATH, mode="a", maxBytes=2000000, backupCount=5, encoding=None, delay=False
#         )
#         all_log_handler.setFormatter(formatter)
#         all_log_handler.addFilter(cid_filter)
#
#         error_log_handler = handlers.RotatingFileHandler(
#             filename=ERROR_LOG_FILE_PATH, mode="a", maxBytes=2000000, backupCount=3, encoding=None, delay=False
#         )
#         error_log_handler.setLevel(logging.ERROR)
#         error_log_handler.setFormatter(formatter)
#         error_log_handler.addFilter(cid_filter)
#
#         logger = logging.getLogger(module_name)
#         logger.setLevel(logging.INFO)
#         logger.addHandler(console_handler)
#         logger.addHandler(all_log_handler)
#         logger.addHandler(error_log_handler)
#         logger.propagate = False
#
#         return logger


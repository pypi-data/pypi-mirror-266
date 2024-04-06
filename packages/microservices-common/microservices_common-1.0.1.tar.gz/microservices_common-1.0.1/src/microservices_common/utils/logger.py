import logging
import inspect


class Logger:
    def __init__(self):
        pass

    @classmethod
    def get_caller_info(cls, caller_frame):
        file_name = caller_frame.f_code.co_filename
        line_number = caller_frame.f_lineno
        function_name = caller_frame.f_code.co_name
        return file_name.rsplit("/", 1)[-1], line_number, function_name

    @classmethod
    def log(cls, level, message, caller_frame, logging_info=None):
        file_name, line_number, function_name = cls.get_caller_info(
            caller_frame)
        log_message = "{}:{} - {} - FUNC - {} - {}".format(
            file_name, line_number, message, function_name, logging_info if logging_info else "")
        getattr(logging, level)(log_message)

    @classmethod
    def info(cls, message, logging_info=None):
        caller_frame = inspect.currentframe().f_back
        cls.log("info", message, caller_frame, logging_info)

    @classmethod
    def error(cls, message, logging_info=None):
        caller_frame = inspect.currentframe().f_back
        cls.log("error", message, caller_frame, logging_info)

    @classmethod
    def warning(cls, message, logging_info=None):
        caller_frame = inspect.currentframe().f_back
        cls.log("warning", message, caller_frame, logging_info)

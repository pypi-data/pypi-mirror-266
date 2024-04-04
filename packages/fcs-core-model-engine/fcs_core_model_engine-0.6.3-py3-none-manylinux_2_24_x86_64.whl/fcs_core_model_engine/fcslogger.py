
import logging
import os
from sys import platform
import datetime

class FCSLogger:
    """
    Class used for logging for all FCS operations.
    """
    def __init__(self, user_id: str, path_to_log_file: str):
        self.logger = logging.getLogger(f'fcs_{user_id}')
        self.logger.setLevel(logging.INFO)
        self.path_to_log_file = path_to_log_file
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(logging.INFO)
        self.stream_handler.setFormatter(formatter)
        self.logger.addHandler(self.stream_handler)

        try:
            self.file_handler = logging.FileHandler(self.path_to_log_file)
            self.file_handler.setLevel(logging.INFO)
            self.file_handler.setFormatter(formatter)
            self.logger.addHandler(self.file_handler)
        except Exception as ex:
            self.wrn(f"Failed to add FileHandler that should write out logs to {self.path_to_log_file}. Reason: {ex.args}")

    def set_logging_context(self, context_name: str) -> None:
        """The logging may refer to a custom addin. If so, we want to indicate that these logging messages
        come from inside plugin.

        Args:
            context_name (str): Name of the application.
        """

        formatter = logging.Formatter(f"{context_name} - %(asctime)s - %(levelname)s - %(message)s")
        self.stream_handler.setFormatter(formatter)
        self.file_handler.setFormatter(formatter)

    def get_log_file_path(self) -> str:
        """Returns path to log file.
        """
        return self.path_to_log_file

    def log(self, message: str):
        clean_message = str(message).encode('ascii', 'replace').decode('ascii')
        self.logger.info(clean_message)

    def dbg(self, message: str):
        clean_message = str(message).encode('ascii', 'replace').decode('ascii')
        self.logger.debug(clean_message)

    def wrn(self, message: str):
        clean_message = str(message).encode('ascii', 'replace').decode('ascii')
        self.logger.warn(clean_message)

    def err(self, message: str):
        clean_message = str(message).encode('ascii', 'replace').decode('ascii')
        self.logger.error(clean_message)

    def fatal(self, message: str):
        """These should be errors that indicate the binary backend 
        failed or created unexpected results.
        """
        clean_message = str(message).encode('ascii', 'replace').decode('ascii')
        self.logger.critical(clean_message)

def create_generic_logger(name_of_logger: str) -> FCSLogger:
    """This type of logging is not user bound.

    Returns:
        FCSLogger: logging class
    """

    str_tmp_path = ''
    if platform == "win32":
        str_app_data = os.getenv('APPDATA')
        str_tmp_path = os.path.join(str_app_data, "Femsolve Kft")

        if not os.path.isdir(str_tmp_path):
            os.mkdir(str_tmp_path)

    elif platform == "linux":
        str_tmp_path = f"{os.path.dirname(__file__)}/../../LinuxAppData/"  

        if not os.path.isdir(str_tmp_path):
            os.mkdir(str_tmp_path)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path_to_log_file = os.path.join(str_tmp_path, f'{name_of_logger}_{timestamp}.log')
    return FCSLogger(name_of_logger, path_to_log_file)


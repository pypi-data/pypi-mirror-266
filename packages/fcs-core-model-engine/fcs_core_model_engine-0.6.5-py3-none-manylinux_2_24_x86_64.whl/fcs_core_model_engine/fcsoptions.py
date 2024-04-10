import enum

class StatusMessageType(enum.Enum):
    """
    Simple flags for status messages.
    """
    InfoStatus = 3
    WarningStatus = 4
    FailureStatus = 5

class ProcessExitStatus(enum.Enum):
    """
    Encompasses possible exit statuses for a process.
    """

    Successful = 0 
    Warning = 1
    Failure = 2

    @staticmethod
    def is_valid_status(allegedly_valid_status: 'ProcessExitStatus') -> bool:
        """
        Checks if the passed in `allegedly_valid_status` belongs to 
        any of the allowed options.

        Returns:
            bool: True, if the status passed is among the existing options.
        """
        return allegedly_valid_status in ProcessExitStatus
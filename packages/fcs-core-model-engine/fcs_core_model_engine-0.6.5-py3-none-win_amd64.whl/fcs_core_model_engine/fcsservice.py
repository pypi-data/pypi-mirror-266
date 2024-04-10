
# from .fcsviewer import FCSViewer
from .fcsviewer import gb
from .fcsviewer import ModelBuilder
from .geometrybuilder import GeometryBuilder

class BackendService(object):
    """
    Template class for hosting specific plugins.
    """

    def __init__(self, app_guid: str):
        """
        Constructor.
        """
        self.app_guid = app_guid
        self.fv: FCSViewer
        self.db: DocumentBuilder
        self.gb: GeometryBuilder

    def set_existing_services(self, fcs_viewer) -> None: 
        """
        To any backend service connect we pass on the instances of the main operators.
        """

        # ToDo: Set session services
        self.gb = gb # Only need a single instance right now
        self.fv = fcs_viewer
        self.db = self.fv.model_builder

    def run_command(self, command_name: str, command_args: dict={}) -> dict:
        """
        Returns true, if the command was found and run (even if it failed).
        Return false otherwise.
        """

        log = self.fv.get_logger()
        log.set_logging_context(self.app_guid)
        result = None

        if command_name not in self.get_available_callbacks():
            log.wrn(f'Request a command name that was not made available: {command_name}.')
            return {'Error' : f'Command name unavailable {command_name}'}

        try:
            command_ptr = getattr(self, command_name)
            result = command_ptr(command_args)
        except AttributeError as ex_atrr:
            log.err(f'Probably could not find {command_name}! (Exception: {ex_atrr.args})')
        except Exception as ex:
            log.err(f'Something failed: {ex.args}!')
        finally: 
            log.set_logging_context('')

        return result

#--------------------------------------------------------------------------------------------------
# Pure virtual methods that require implementation
#--------------------------------------------------------------------------------------------------

    def get_available_callbacks(self, args: dict=None) -> list:
        """
        List of available callbacks to be forwarded to the listeners of the cloud application.
        """
        raise NotImplementedError("`get_available_callbacks` needs to be implemented in the base class!")

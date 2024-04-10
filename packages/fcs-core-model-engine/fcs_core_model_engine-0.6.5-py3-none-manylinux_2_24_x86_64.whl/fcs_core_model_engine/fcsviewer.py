
import io
import os
import json
import requests
import math
import datetime
import urllib3

from .fcsoptions import ProcessExitStatus
from .fcsoptions import StatusMessageType
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from sys import platform

from .fcslogger import FCSLogger
from .fcscore import ColorSelection
from .fcscore import Palette
from .fcscore import ModelBuilder
from .fcscore import GEOM_Object

# Versioning check
from .fcscore import check_api_compatibility, get_backend_api_version

UINT32_MAX = (1 << 32) - 1

# Global instance for not user or document bound operations
global gb
from .geometrybuilder import GeometryBuilder
gb = GeometryBuilder()

class FCSViewer(object):
    """
    The primary interactor of the FCS web viewer.
    """

    def __init__(self, user_id: str='local', logger: FCSLogger=None, working_directory: str=None):
        """
        During instantiation connects to a viewer instance.
        """
        # `user_id` can be set to 'local' for debugging and dev purposes,
        # in production mode, this is filled in automatically
        self.user_id = user_id
        self.platform = platform
        self.model_builder = ModelBuilder(gb.geom_engine)
        self.geometry_builder = gb
        # Considers local and production development
        self.viewer_url = '127.0.0.1'
        self.viewer_port = 3000
        if 'FCS_BACKEND_URL' in os.environ and ':' in os.environ['FCS_BACKEND_URL']:
            self.viewer_url = os.environ['FCS_BACKEND_URL'].split(':')[0]
            self.viewer_port = int(os.environ['FCS_BACKEND_URL'].split(':')[1])
        else:
            self.viewer_url = 'host.docker.internal'
        self.viewer_request_url = f'http://{self.viewer_url}:{self.viewer_port}/viewer/toFrontend'
        self.is_available = self.has_active_viewer()
        # ToDo: Reinstate compatibility check
        # self.is_viewer_compatible = self.has_compatible_viewer()
        self.working_directory = self.__setup_working_directory() if working_directory == None else working_directory
        self.log = self.__setup_logging() if logger == None else logger
        self.log.log(f'Viewer request URL will be {self.viewer_request_url}.')
        self.log_debug_information = False
        # ToDo: For Docker use purposes always send the requests
        if 'docker' in self.viewer_request_url:
            if not self.is_available:
                self.log.log('Overriding is_available boolean so that requests can be sent!')
                self.is_available = True
        self.published_object_counter = 0
        self.nested_object_counter = 0
        self.active_document_name = self.model_builder.get_model_name()

    def get_logger(self) -> FCSLogger:
        """Getter for logger object

        Returns:
            Logger object bound to this viewer instance.
        """
        return self.log

    def set_model_name(self, model_name: str) -> None:
        """
        Renames the workspace binary. Do not include extension!
        """

        default_model_path = f"{self.user_id}/{self.active_document_name}.cbf"
        self.active_document_name = model_name
        self.model_builder.set_model_name(self.active_document_name)

        if os.path.exists(default_model_path):
            os.replace(default_model_path, f"{self.user_id}/{self.active_document_name}.cbf")

    def has_active_viewer(self) -> bool:
        """
        Checks if the cloud viewer's port is active by pinging it. 
        
        Legacy functionality: `salome.sg.hasDesktop()`
        """

        def is_port_in_use(port: int) -> bool:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex((f'{self.viewer_url}', port)) == 0

        try:
            is_running = is_port_in_use(self.viewer_port)
            return is_running                      
        except Exception as ex:
            print(f"has_active_viewer failed: {ex}. Will assume no Viewer is connected!")
            return False

    def has_compatible_viewer(self) -> bool:
        """
        If a viewer instance was found, we check if its version 
        is in coherence with the backend's version.
        """

        if not self.is_available: return False

        response = requests.get(f"http://{self.viewer_url}:{self.viewer_port}/version", verify=False)

        viewer_version = response.text
        if not check_api_compatibility(viewer_version):
            print(f"!!! Viewer instance version ({viewer_version}) is not compatible with current backend API version ({get_backend_api_version()})!!!")
            self.is_available = False

        return True

    def show_progress_tracker(self, progress_percentage: float, current_process_name: str, process_bundle_title: str='') -> None:
        """
        Can be used to communicate to the user the progress of a backend process.

        Args:
            progress_percentage (float): Has to be a value between 0 and 100. If is outside
                of these bounds an exception is thrown!
            current_process_name (str): Need to name the process that's running, or provide 
                some description otherwise it will throw an error
            process_bundle_title (str, optional): This will override the title of the dialog,
                by default its empty and is not overridden.

        """

        if progress_percentage < 0 or progress_percentage > 100:
            error_msg = f'Progress percentage ({progress_percentage}) is out of bounds!'
            self.log.err(error_msg)
            raise Exception(error_msg)
        
        if current_process_name == None or len(current_process_name.strip()) == 0:
            error_msg = f'Need to name the process!'
            self.log.err(error_msg)
            raise Exception(error_msg)
        
        msg_request = {
            "operation":"show_progress_tracker",
            "arguments":{
                "progress_percentage" : progress_percentage,
                "current_process_name" : current_process_name,
                "process_bundle_title" : process_bundle_title
                }
            }

        _ = self.__try_send_request(self.viewer_request_url, msg_request)

    def finish_progress_tracker(self, exit_status: ProcessExitStatus=ProcessExitStatus.Successful, exit_message: str='Operation Completed!', immediate_shutdown=False) -> None:
        """
        This will finish the progress tracking.

        Args:
            exit_status (bool, optional): Based on the exit status the dialog will change slightly in style.
            exit_message (str, optional): What should be shown to the user when the process finished. Defaults to 'Operation Completed!'.
            immediate_shutdown (bool, optional): If set to true, the progress tracker will immediately disappear. Defaults to False.
        """

        # Need to validate the correct optional status was passed in.
        if not ProcessExitStatus.is_valid_status(exit_status):
            error_msg = f'You need to pass in a valid exit status for the process!'
            self.log.err(error_msg)
            raise Exception(error_msg)

        msg_request = {
            "operation":"finish_progress_tracker",
            "arguments":{
                "exit_status" : exit_status.value,
                "exit_message" : exit_message,
                "immediate_shutdown" : immediate_shutdown
                }
            }

        _ = self.__try_send_request(self.viewer_request_url, msg_request)

    def show_status_message(self, message_type: StatusMessageType, message: str) -> None:
        """
        Propagates an info, warning, or error message to the frontend client.
        """

        if message_type not in StatusMessageType:
            error_msg = f'You need to pass in a valid status message for the process!'
            self.log.err(error_msg)
            raise Exception(error_msg)

        msg_request = {
            "operation":"show_status_message",
            "arguments":{
                "message_status" : message_type.value,
                "message" : message
                }
            }

        _ = self.__try_send_request(self.viewer_request_url, msg_request)


    def update_viewer(self) -> None:
        """
        Updates viewer's document. Will load all added entities to the viewer               
        Legacy functionality: `salome.sg.updateObjBrowser()`
        """

        #ToDo: Implement this on client side
        return; 

        msg_request = {
                "operation":"update_viewer",
                "arguments":{
                    }
            }

        is_ok = self.__try_send_request(self.viewer_request_url, msg_request)["status"]

    def clear_document(self) -> bool:
        """Clears the document and discards all entities in it.

        Returns:
            bool: If the document clearing was successful.
        """

        if not self.model_builder.clear_document():
            self.log.err('Failed to clear document!')
            return False

        # STEP 2: SEND data to frontend
        msg_request = {
            "operation":"clear_document",
            "arguments":{
                }
            }

        is_ok = self.__try_send_request(self.viewer_request_url, msg_request)
        return is_ok

    def open_new_document(self, new_document_name: str) -> None:
        """
        Sets a new document name.
        """
        self.model_builder.open_new_model(new_document_name)
        self.active_document_name = new_document_name

        # ToDo: Implement this on frontend.
        return
        msg_request = {
            "operation":"open_new_document",
            "arguments":{
                "document_name" : self.active_document_name,
                }
            }

        is_ok = self.__try_send_request(self.viewer_request_url, msg_request)

    def commit_to_document(self) -> None:
        """
        If we commit to a document it is deserialised into a file in the local working folder
        and it is uploaded to the server to synchronise with the server's working instance.

        This will enable 'Active' mode in the viewer allowing the user to actively
        interact / modify / export the model generated by the plugin. 
        """

        model_path = f"{self.user_id}/{self.active_document_name}.cbf"

        if self.model_builder.save_model_to(self.working_directory):
            self.log.log(f'Successfully saved model document to {model_path}')

        msg_request = {
            "operation":"commit_to_document",
            "arguments":{
                "model_path" : model_path,
                }
            }

        is_ok = self.__try_send_request(self.viewer_request_url, msg_request)

    def hide(self, entity_id: int) -> None:
        """
        Hides items in the viewer.
        """

        _ = self.model_builder.set_object_visibility(entity_id, False)

        msg_request = {
                "operation":"hide",
                "arguments":{
                    "entity_ids": [entity_id]
                    }
            }

        is_ok = self.__try_send_request(self.viewer_request_url, msg_request)["status"]

    def hide_only(self, entity_id: int) -> None:
        """
        Only sets this given item to be hidden all the rest will be shown.
        """

        #ToDo: Implement this on client side
        return; 

        list_component_ids = self.model_builder.get_added_component_ids()

        for component_id in list_component_ids:
            _ = self.model_builder.set_object_visibility(component_id, True)

        _ = self.model_builder.set_object_visibility(component_id, False)

        msg_request = {
            "operation": "hide_only",
            "arguments":{
                "entity_id": entity_id
                }
        }

        is_ok = self.__try_send_request(self.viewer_request_url, msg_request)["status"]

    def hide_all(self) -> None:
        """
        Hides everything in the active document             
        Legacy functionality: `salome.sg.EraseAll()`
        """

        list_component_ids = self.model_builder.get_added_component_ids()

        for component_id in list_component_ids:
            _ = self.model_builder.set_object_visibility(component_id, False)

        msg_request = {
                "operation":"hide_all",
                "arguments":{
                    }
            }

        is_ok = self.__try_send_request(self.viewer_request_url, msg_request)["status"]

    def show(self, entity_id: int) -> None:
        """
        Pass in unique ID of the object to activate entity in the viewer.              
        Legacy functionality: `salome.sg.Display(model_id)`
        """
        _ = self.model_builder.set_object_visibility(entity_id, True)

        msg_request = {
                "operation": "show",
                "arguments":{
                    "entity_ids": [entity_id]
                    }
            }

        is_ok = self.__try_send_request(self.viewer_request_url, msg_request)["status"]

    def show_only(self, entity_id: int) -> None:
        """
        Pass in unique ID of the object to show that entity only                
        Legacy functionality: `salome.sg.DisplayOnly(model_id)`
        """

        #ToDo: Implement this on client side
        return; 

        list_component_ids = self.model_builder.get_added_component_ids()

        for component_id in list_component_ids:
            if component_id == entity_id:
                _ = self.model_builder.set_object_visibility(component_id, True)
            else:
                _ = self.model_builder.set_object_visibility(component_id, False)

        msg_request = {
                "operation": "show_only",
                "entity_id": entity_id
            }

        is_ok = self.__try_send_request(self.viewer_request_url, msg_request)["status"]

    def show_all(self) -> None:
        """
        Displays all entities in the viewer.
        """

        list_component_ids = self.model_builder.get_added_component_ids()

        for component_id in list_component_ids:
            _ = self.model_builder.set_object_visibility(component_id, True)

        msg_request = {
                "operation": "show_all",
            }

        is_ok = self.__try_send_request(self.viewer_request_url, msg_request)["status"]

    def set_transparency(self, entity_id: int, opacity: float) -> None:
        """
        Sets transparency of the object in the viewer.
        Legacy functionality: `gg.setTransparency(model_id)`
        """

        if entity_id == -1: return

        _ = self.model_builder.set_object_opacity(entity_id, opacity)

        msg_request = {
                "operation": "set_transparency",
                "arguments":{
                    "entity_id": entity_id,
                    "opacity":opacity
                    }
            }

        is_ok = self.__try_send_request(self.viewer_request_url, msg_request)["status"]

    def center_view(self) -> None:
        """
        Adjust camera that all is visible               
        Legacy functionality: `salome.sg.FitAll()`
        """

        msg_request = {
                "operation":"center_view",
                "arguments":{
                    }
            }

        is_ok = self.__try_send_request(self.viewer_request_url, msg_request)["status"]

    def refresh_viewer(self) -> bool:
        """
        By default, the viewer is not rendering any added/removed/modified components,
        unless we are operating on views (view centering, camera position, etc.)
        """

        msg_request = {
            "operation" : "refresh_viewer",
            "arguments" : {
            }
        }

        is_ok = self.__try_send_request(self.viewer_request_url, msg_request)["status"]
        return is_ok

    def translate_vector(self, object_id: int, vector_xyz: list) -> GEOM_Object:
        """
        Eltol egy vektor altal megadott iranyba es a vektor meretevel
        """

        # Get object by id
        geom_object = self.model_builder.get_geom_object_by_id(object_id)

        # Create vector object
        dx = vector_xyz[0]
        dy = vector_xyz[1]
        dz = vector_xyz[2]
        vector_length = math.sqrt(dx**2 + dy**2 + dz**2) 
        if vector_length < 1e-9:
            self.log.wrn(f'Tried to offset entity {object_id} by a zero distance! Translation will be omitted.')
            return
        
        norm_vector_xyz = [dx/vector_length, dy/vector_length, dz/vector_length]
        geom_norm_vector_xyz = self.geometry_builder.make_vector(dx, dy, dz)
        geom_object = self.geometry_builder.translate_vector_distance(geom_object, geom_norm_vector_xyz, vector_length, False)

        msg_request = {
            "operation": 'translate_two_points',
            "arguments": {
                "entityUIDs" : [object_id],
                "vector_xyz" : [dx, dy, dz],
                "copy" : False,
                },
            }

        msg_response = self.__try_send_request(self.viewer_request_url, msg_request)
        return geom_object
        
    def translate_two_points(self, object1_id: int, object2_id: int, object3_id: int):
        """
        Eltol ket pont altal meghatarozott iranyba, a pontok kozti tavolsag metekevel

        arg1: objectumok (most csak faces), amiken az eltolast vegezzuk
        arg2: pont1
        arg2: pont2

        Todo: az object1_id-nak egy listanak kellene lennie, ami id-kat tartalmaz
        """

        # Find geom objects based on the two IDs
        g_obj1 = self.model_builder.get_geom_object_by_id(object1_id)
        g_obj2 = self.model_builder.get_geom_object_by_id(object2_id)
        g_obj3 = self.model_builder.get_geom_object_by_id(object3_id)

        # Translate the model and send response to the viewer
        obj = self.geometry_builder.translate_two_points(g_obj1, g_obj2, g_obj3)

        # Calculate vector of translation
        point2_xyz = self.geometry_builder.get_position(g_obj2)
        point3_xyz = self.geometry_builder.get_position(g_obj3)

        dx = point3_xyz[0] - point2_xyz[0]
        dy = point3_xyz[1] - point2_xyz[1]
        dz = point3_xyz[2] - point2_xyz[2]
        vector_xyz = [dx, dy, dz]

        msg_request = {
            "operation": 'translate_two_points',
            "arguments": {
                "entityUIDs" : [object1_id], # Egy listat ad vissza a kijelolt entity-k (items, face, edges, vertices) UID-jaival
                "vector_xyz" : vector_xyz,
                "copy" : False,
                },
            }

        msg_response = self.__try_send_request(self.viewer_request_url, msg_request)

    def translate_dx_dy_dz(self):
        """
        Eltol dx, dy, dz vektorkomponensek alapjan
        """
        pass

    def rotate_axis(self):
        """
        Egy tengely korul forgat
        """
        pass

    def position_shape(self):
        """
        Forgat es eltol egy kiindulo- es egy cel LCS alapjan
        """
        pass

    def add_new_container(self, name: str) -> int:
        """
        Creates a TOP LEVEL empty container that will not store any geometric objects 
        at its unique ID. It is used to group together and organize other entities
        in the model tree.
        """

        item_id = -1

        #ToDo: Implement this on client side
        # return item_id; 

        try:
            item_id = self.model_builder.add_new_container(name)
        except Exception as ex:
            self.log.err(f"FCSViewer: Could not publish container named {name}. Failure: {ex.args}")
            return item_id

        msg_request = {
            "operation":"add_new_container",
            "arguments":{
                "name" : name,
                "item_id" : str(item_id),
                "folderName": "Component", # !!! Hardcoded for now !!!
                }
            }

        msg_response = self.__try_send_request(self.viewer_request_url, msg_request)

        # ToDo: Increment only if response is correct
        self.published_object_counter += 1

        return item_id

    def add_new_container_under(self, name: str, parent_id: int) -> int:
        """
        Creates an empty container NESTED UNDER A PARENT that will not store any geometric 
        objects at its unique ID. It is used to group together and organize other entities
        in the model tree.
        """

        item_id = -1

        #ToDo: Implement this on client side
        # return item_id; 

        try:
            item_id = self.model_builder.add_new_container_under(name, parent_id)
        except Exception as ex:
            self.log.err(f"FCSViewer: Could not publish container named {name}. Failure: {ex.args}")
            return item_id

        msg_request = {
            "operation":"add_new_container_under",
            "arguments":{
                "name" : name,
                "item_id" : str(item_id),
                "parent_id": str(parent_id), # 0 means top level
                }
            }

        msg_response = self.__try_send_request(self.viewer_request_url, msg_request)

        # ToDo: Increment only if response is correct
        self.published_object_counter += 1

        return item_id
    
    def add_to_document(self, entity: GEOM_Object, geom_object_name: str, isVisible: bool = True) -> int:
        """
        Adds a brand new top-level component.
        Legacy functionality: `salome.sg.addToStudy(model, name)`
        """

        if entity.is_null():
            error_msg = f'FCSViewer: Cannot add `{geom_object_name}` to document because its geometry representation is null!'
            self.log.err(error_msg)
            raise Exception(error_msg)

        # Object order is not the same as the ID!
        object_order = self.published_object_counter + 1
        item_id = -1

        # Sanitize name of unwanted characters
        geom_object_name = self.__sanitize_name(geom_object_name)

        export_stl_name = f"{object_order}_{geom_object_name}.stl"
        export_t2g_name = f"{object_order}_{geom_object_name}_geom.json"

        # STEP 1: EXPORT geometry
        express_static_folder = f"{self.user_id}"
        t2g_path_static = f'{express_static_folder}/{export_t2g_name}'
        stl_path_static = f'{express_static_folder}/{export_stl_name}'
        try:
            export_to_path = self.working_directory
            item_id = self.model_builder.add_to_document(entity, geom_object_name, export_to_path)
            if item_id == UINT32_MAX:
                self.log.err("Max ID was returned, thus shape could not be properly processed!")
                return -1

            # Rename files so in complex runs files do not overwrite each other
            original_stl_file_path = os.path.join(export_to_path, f"{geom_object_name}.stl")
            new_stl_file_path = os.path.join(export_to_path, export_stl_name)
            if os.path.exists(new_stl_file_path):
                os.remove(new_stl_file_path)

            if os.path.exists(original_stl_file_path):
                os.rename(original_stl_file_path, new_stl_file_path)
            
            original_t2g_file_path = os.path.join(export_to_path, f"{geom_object_name}_geom.json")
            new_t2g_file_path = os.path.join(export_to_path, export_t2g_name)
            if os.path.exists(new_t2g_file_path):
                os.remove(new_t2g_file_path)

            if os.path.exists(original_t2g_file_path):
                os.rename(original_t2g_file_path, new_t2g_file_path)

        except Exception as ex:
            self.log.err(f"FCSViewer: Could not publish object named {geom_object_name}. Failure: {ex.args}")
            return item_id

        # STEP 2: SEND data to frontend
        msg_request = {
            "operation":"add_to_document",
            "arguments":{
                "name" : geom_object_name,
                "isVisible": isVisible,
                "item_id" : str(item_id),
                "t2g_file" : export_t2g_name,
                "stl_file" : export_stl_name,
                "stl_path" : express_static_folder,
                "stl_path_static" : stl_path_static,
                "t2g_path_static" : t2g_path_static
                }
            }
        
        # Collect full paths to written out asset files
        t2g_file_fullpath = os.path.join(self.working_directory, export_t2g_name)
        stl_file_fullpath = os.path.join(self.working_directory, export_stl_name)

        msg_response = self.__try_send_request_with_files(
            self.viewer_request_url, 
            msg_request,
            [t2g_file_fullpath, stl_file_fullpath])

        # ToDo: Increment only if response is correct
        self.published_object_counter += 1
        if self.log_debug_information:
            self.log.dbg(f'FCSViewer DEBUG: Total number of published objects {self.published_object_counter}')

        return item_id

    def remove_from_document(self, object_id: int) -> None:
        """
        Removes all child entities under this ID. 
        All components that were removed from the document
        need to be updated. The removed_ids must contain the passed in ID itself.
        """
        
        try:
            self.log.dbg(f'FCSViewer: Will try and remove {object_id}...')
            removed_ids = self.model_builder.remove_from_document(object_id)
            if len(removed_ids) == 0:
                self.log.wrn(f'FCSViewer: Did not remove {object_id} because it seems it is no longer in the document.')
        except Exception as ex:
            self.log.err(f'FCSViewer: Failed to remove {object_id}. Exception: {ex.args}')
            return

        removed_all_ids = []

        removed_all_ids.extend(removed_ids)

        msg_request = {
            "operation": 'remove_from_document',
            "arguments": {
                "removedUIDs" : removed_all_ids,
                },
            }

        msg_response = self.__try_send_request(self.viewer_request_url, msg_request)


    def add_to_document_under(self, entity: object, parent_entity_id: int, geom_object_name: str, isVisible: bool = False) -> int:
        """
        Adds entity under a parent entity               
        Legacy functionality: `geompy.addToStudyInFather( self.Model, i_Face, str_Name )`
        """

        if self.log_debug_information:
            self.log.dbg(f"FCSViewer DEBUG: Trying to add {geom_object_name} under {parent_entity_id}.")

        if entity == None or parent_entity_id == -1 or geom_object_name == "":
            raise Exception("Wrong input data provided for add_to_document_under!")

        item_id = -1
        if parent_entity_id == -1: return item_id

        # Sanitize name of unwanted characters
        geom_object_name = self.__sanitize_name(geom_object_name)

        # Object order is not the same as the ID!
        object_order = self.published_object_counter + 1

        export_stl_name = f"{object_order}_{geom_object_name}.stl"
        export_t2g_name = f"{object_order}_{geom_object_name}_geom.json"

        # STEP 1: EXPORT geometry
        express_static_folder = f"{self.user_id}"
        t2g_path_static = f'{express_static_folder}/{export_t2g_name}'
        stl_path_static = f'{express_static_folder}/{export_stl_name}'
        try:
            export_to_path = self.working_directory
            item_id = self.model_builder.add_to_document_under(entity, parent_entity_id, geom_object_name, export_to_path)
            if item_id == UINT32_MAX:
                self.log.err("Max ID was returned, thus shape could not be properly processed!")
                return -1

            # Rename files so in complex runs files do not overwrite each other
            original_stl_file_path = os.path.join(export_to_path, f"{geom_object_name}.stl")
            new_stl_file_path = os.path.join(export_to_path, export_stl_name)
            if os.path.exists(new_stl_file_path):
                os.remove(new_stl_file_path)

            if os.path.exists(original_stl_file_path):
                os.rename(original_stl_file_path, new_stl_file_path)
            
            original_t2g_file_path = os.path.join(export_to_path, f"{geom_object_name}_geom.json")
            new_t2g_file_path = os.path.join(export_to_path, export_t2g_name)
            if os.path.exists(new_t2g_file_path):
                os.remove(new_t2g_file_path)
            
            if os.path.exists(original_t2g_file_path):    
                os.rename(original_t2g_file_path, new_t2g_file_path)

        except Exception as ex:
            self.log.err(f"FCSViewer: Could not publish object named {geom_object_name}. Failure: {ex.args}")
            return item_id

        # STEP 2: SEND data to frontend
        msg_request = {
            "operation":"add_to_document_under",
            "arguments":{
                "name" : geom_object_name,
                "isVisible": isVisible,
                "item_id" : str(item_id),
                "parent_id":str(parent_entity_id),
                "t2g_file" : export_t2g_name,
                "stl_file" : export_stl_name,
                "stl_path" : express_static_folder,
                "stl_path_static" : stl_path_static,
                "t2g_path_static" : t2g_path_static
                }
            }

        # Collect full paths to written out asset files
        t2g_file_fullpath = os.path.join(self.working_directory, export_t2g_name)
        stl_file_fullpath = os.path.join(self.working_directory, export_stl_name)

        msg_response = self.__try_send_request_with_files(
            self.viewer_request_url, 
            msg_request,
            [t2g_file_fullpath, stl_file_fullpath])

        # ToDo: Increment only if response is correct
        self.published_object_counter += 1
        self.nested_object_counter += 1
        if self.log_debug_information:
            self.log.dbg(f'FCSViewer DEBUG: Published {self.nested_object_counter} nested objects. ({self.published_object_counter} in total)')

        # Set visibility
        # if not isVisible:
        #     self.hide(item_id)

        return item_id

    def find_object_from_viewer_by_name(self, name: str) -> list:
        """
        Returns all objects that can be found under the specified under
        the specified name.

        Legacy functionality: `salome.myStudy.FindObjectByName(self.name,'GEOM')[0]`
        """
        if not self.is_available: return []

        msg_request = {
            "operation":"find_object_by_name",
            "arguments":{
                "search_name": name
                }
            }

        dict_result = self.__try_send_request(self.viewer_request_url, msg_request)

        if dict_result["status"]: 
            list_result_ids = list(dict_result["result"]["IDs"])
        else:
            list_result_ids = []

        # ToDo: Use the FCS Viewer's document to access the GEOM_Object
        return list_result_ids
    
    def object_to_id(self, obj: object) -> int:
        """
        Returns ID for any FCS object.
        This only returns a positive integer if the object
        has been added to the FCS Viewer.

        Legacy functionality: `geompy.getObjectID(i_Face))`
        """

        # ToDo: Need to extend the GEOM_Object to store
        # GUIDs unique to every single GEOM_Object

        return -1

    def set_specific_object_color(self, id: int, red: int, green: int, blue: int) -> None:
        """
        Colours object in viewer. 
        Input are RGB integers between 0 to 255.

        Legacy functionality: `SALOMEDS.SetColor(i_Face, list_RGB)`
        """
        if id == -1: return

        if id == 3832:
            print('Debug')

        # Create paint 
        color = Palette.get_specific_colour(red, green, blue)

        # Set color
        self.model_builder.set_object_colour(id, color)

        # Inform viewer
        msg_request = {
            "operation":"set_object_color",
            "arguments":{
                "item_id" : str(id),
                "red": color.R,
                "green" : color.G,
                "blue" : color.B
                }
            }

        msg_response = self.__try_send_request(self.viewer_request_url, msg_request)

    def set_object_color(self, id: int, selected_color: ColorSelection) -> None:
        """
        Colours object in viewer.

        Input is a specific colour that is available in the selection.
        """
        if id == -1: return

        # Create paint
        color = Palette.get_colour(selected_color)

        # Set colour
        self.model_builder.set_object_colour(id, color)        

        # SEND data to viewer
        msg_request = {
            "operation":"set_object_color",
            "arguments":{
                "item_id" : str(id),
                "red": color.R,
                "green" : color.G,
                "blue" : color.B
                }
            }

        msg_response = self.__try_send_request(self.viewer_request_url, msg_request)

    def show_message(self, message: str) -> None:
        """Creates a pop-up window to the user.

        Args:
            message (str): The message to be shown in the pop-up window.
        """

        msg_request = {
            "operation":"show_message_to_user",
            "arguments":{
                'message' : message
                }
        }

        msg_response = self.__try_send_request(self.viewer_request_url, msg_request)

    def __try_send_request(self, viewer_url: str, request: dict) -> dict:
        """
        Private method to try forward request to cloud viewer.
        """

        self.log.log(f"Sending request to viewer... {request}")

        if not self.is_available: 
            self.log.log(f"Oops, sorry, we are not sending anything to viewer because it is not available!")
            return {
            "status" : True
            }

        
        request['user_id'] = self.user_id
        dict_result: dict = None
        try:
            headers = {'Content-type': 'application/json'}
            response = requests.post(viewer_url, json=request, headers=headers, verify=False)
            dict_result = {
                "status" : True
            }
        except:
            dict_result = {
                "status": False
                }

        return dict_result


    def __try_send_request_with_files(self, viewer_url: str, request: dict, file_paths: list) -> dict:
        """
        Private method to try forward request to cloud viewer WITH files.
        """

        self.log.dbg(f"Sending request to viewer... {request}")

        if not self.is_available: 
            self.log.dbg(f"Oops, sorry, we are not sending anything to viewer because it is not available!")
            return {
            "status" : True
            }

        request['user_id'] = self.user_id
        dict_result: dict = None
        try:
            # Define the multipart/form-data payload
            files = []
            for i, file_path in enumerate(file_paths):
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    files.append((f'file{i}', (file_path, io.BytesIO(file_data))))

            data = {'message': json.dumps(request)}
            
            # Send the POST request
            response = requests.post(viewer_url, files=files, data=data, verify=False)
            self.log.dbg(f'Response: {response}!')
            dict_result = {
                "status" : True
            }

        except Exception as ex:
            self.log.err(f'Exception occured during request sending: {ex}!')
            dict_result = {
                "status": False
            }

        return dict_result


    def __setup_working_directory(self):
        """
        Creates a Femsolve Kft folder if it does not yet exist.
        Returns path to AppData folder. This is only done on Windows.
        """

        str_tmp_path = ""

        try:
            if self.platform == "win32":

                str_app_data = os.getenv('APPDATA')
                str_tmp_path = os.path.join(str_app_data, "Femsolve Kft", self.user_id)

                if not os.path.isdir(str_tmp_path):
                    os.mkdir(str_tmp_path)

            elif self.platform == "linux":
                # ToDo: This would need to be in an environment file
                str_tmp_path = os.path.join(os.path.dirname(__file__),"../../LinuxAppData",self.user_id)
                
                if not os.path.isdir(str_tmp_path):
                    os.mkdir(str_tmp_path)
                    print(f"Created temporary folder for exports : {str_tmp_path}!")

        except Exception as ex:

            if self.is_available: 
                
                print(f"Failed to create TEMP directories with an AVAILABLE viewer hooked up! Exception: {ex} \n")
                self.is_available = False

            else:

                print(f"Failed to create TEMP directories. Exception: {ex} \n")
        
        if not self.is_available:

            print("\n !!! WARNING !!! Because no viewer is attached to external application there will not be any model files exported"
                   +" (and thus no temporary work path is setup). Note in Batch mode, unless the user manually saves the document"
                   +" no results will be saved! \n")

        return str_tmp_path
    
    def __setup_logging(self) -> object:
        """
        Creates a new logging instance. This is already user bound and will output to a text file
        formatted as follows: <YEAR-MM-DD-HR-MN-SEC>_<User>.txt
        Returns:
            object: Object responsible for logging.
        """

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path_to_log_file = os.path.join(self.working_directory, f'{self.user_id}_{timestamp}.log')
        return FCSLogger(self.user_id, path_to_log_file)

    def __sanitize_name(self, original_item_name: str) -> str:
        """
        Removes invalid characters in item name, so that when the STL file of the object is 
        exported to hard-disk, it can be serialized. Invalid characters such as '\' or ':'
        would cause errors when the file's written out.

        This method also warns the 

        Background: 
            Added based on task FCS-244, where the item names had '\' characters and thus
            during add_to_document operation it failed to generate STL and T2G file assets.
        """
        invalid_chars = r'\/:*?"<>|'
        sanitized_name = ''
        was_sanitized = False

        for c in original_item_name:
            if c in invalid_chars:
                sanitized_name += '_'
                was_sanitized = True
            else:
                sanitized_name += c

        if was_sanitized:
            self.log.wrn(f'The item name {original_item_name} had to be sanitized to {sanitized_name}!')

        return sanitized_name
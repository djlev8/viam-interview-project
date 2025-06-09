# sensor-pd/src/models/pdetect.py
#Importing the necessary typing libraries for the Pdetect sensor class
from typing import (Any, ClassVar, Dict, Final, List, Mapping, Optional,
                    Sequence, Tuple)
#Importing the typing_extensions library for the Self type
from typing_extensions import Self
#Importing the cast function from the typing library
from typing import cast
#Importing the Viam SDK components for Sensor, ComponentConfig, Geometry, ResourceName, ResourceBase, Model, ModelFamily, SensorReading, ValueTypes, Vision, and VisionClient
from viam.components.sensor import Sensor
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes
from viam.resource.easy_resource import EasyResource
from viam.services.vision import Vision
from viam.services.vision import VisionClient

#Defining the Pdetect sensor class that inherits from the Sensor and EasyResource classes
class Pdetect(Sensor, EasyResource):
    # To enable debug-level logging, either run viam-server with the --debug option,
    # or configure your resource/machine to display debug logs.
    MODEL: ClassVar[Model] = Model(ModelFamily("dl-org", "sensor-pd"), "pdetect")

    #Initializing the Pdetect sensor instance
    def __init__(self, name: str):
        """
        Initialize a new Pdetect sensor instance.

        Args:
            name (str): The name of the sensor.
        """
        #Initializing the superclass (Sensor) with the name of the sensor
        super().__init__(name)
        #Initializing the vision attribute as an optional VisionClient
        self.vision: Optional[VisionClient] = None

    #Defining the new method that instantiates a new Pdetect sensor instance and configures it with the given settings
    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """
        Instantiate a new Pdetect sensor instance and configure it with the given settings.

        Args:
            config (ComponentConfig): The configuration for this sensor
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both implicit and explicit)

        Returns:
            Self: A fully initialized instance of the Pdetect sensor.
        """
        #Instantiating a new Pdetect sensor instance with the name of the sensor
        sensor = cls(config.name)
        #Configuring the sensor with the given settings
        sensor.reconfigure(config, dependencies)
        return sensor
    
    #Defining the validate_config method that validates the configuration object received from the machine 
    @classmethod
    def validate_config(
        cls, config: ComponentConfig
    ) -> Tuple[Sequence[str], Sequence[str]]:
        """
        This method allows you to validate the configuration object received from the machine,
        as well as to return any required dependencies or optional dependencies based on that `config`.

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Tuple[Sequence[str], Sequence[str]]: A tuple where the
                first element is a list of required dependencies (detector_name) and the
                second element is a list of optional dependencies (empty in this case)
        """
        req_deps = []
        #Checking if the camera_name attribute is present in the config
        if "camera_name" not in config.attributes.fields:
            #If the camera_name attribute is not present, raise an exception
            raise Exception("Missing required attribute: camera_name")
        elif not config.attributes.fields["camera_name"].HasField("string_value"):
            #If the camera_name attribute is not a string, raise an exception
            raise Exception("camera_name must be a string")
        if "detector_name" not in config.attributes.fields:
            #If the detector_name attribute is not present, raise an exception
            raise Exception("Missing required attribute: detector_name")
        elif not config.attributes.fields["detector_name"].HasField("string_value"):
            #If the detector_name attribute is not a string, raise an exception
            raise Exception("detector_name must be a string")
        
        detector_name = config.attributes.fields["detector_name"].string_value
        req_deps.append(detector_name)

        #Returning the list of required dependencies  and an empty list of optional dependencies
        return req_deps, []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """This method allows you to dynamically update your service when it receives a new `config` object.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any dependencies (both implicit and explicit)
        """
        fields = config.attributes.fields

        # Validate and extract camera_name
        if "camera_name" not in fields or not fields["camera_name"].HasField("string_value"):
            raise ValueError("Missing or invalid 'camera_name' attribute")

        # Validate and extract detector_name
        if "detector_name" not in fields or not fields["detector_name"].HasField("string_value"):
            raise ValueError("Missing or invalid 'detector_name' attribute")
        detector_name = fields["detector_name"].string_value

        # Lookup Vision service using user-provided detector_name
        vision_resource = dependencies.get(Vision.get_resource_name(detector_name))
        if not vision_resource:
            raise ValueError(f"Required Vision service '{detector_name}' not found")
        
        #Setting the vision attribute to the vision resource (casting the vision resource to a VisionClient)
        self.vision = cast(VisionClient, vision_resource)

        #Setting the camera_name attribute to the value of the camera_name attribute in the config 
        # (to be used in the do_command method)
        self.camera_name = fields["camera_name"].string_value

        #Returning the result of the superclass (Sensor) reconfigure method
        return super().reconfigure(config, dependencies)

    async def get_readings(
        self,
        *,
        extra: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, int]:
        """
        Retrieve the latest reading from the person detection sensor.

        This method queries the associated vision service to check whether a person
        is currently detected in the video feed from the configured camera. It returns
        a dictionary containing a single reading: 1 if a person is detected, 0 otherwise.

        Args:
            extra (Optional[Mapping[str, Any]]): Additional metadata or parameters
                passed to the sensor (not used in this implementation).
            timeout (Optional[float]): Timeout in seconds for the operation, if applicable.
            **kwargs: Additional keyword arguments passed to the method (unused).

        Returns:
            Mapping[str, int]: A dictionary with the key `"person_detected"` 
            mapped to an integer with a value of 1 (detected) or 0 (not detected).
        """
        #Executing the do_command method with an empty command
        result = await self.do_command({})
        #Returning the result of the do_command method
        return {"person_detected": int(result["person_detected"])}
    
    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        """
        Execute a custom command to check for the presence of a person using the vision service.

        This method queries the configured vision service (`detector_name`) for object
        detections from the specified camera. If any detection is classified as a "person"
        with a confidence greater than 0.5, the method returns a result indicating a person
        was detected. Otherwise, it indicates no person was found.

        Args:
            command (Mapping[str, ValueTypes]): A dictionary of command arguments.
                This implementation does not use any input arguments.
            timeout (Optional[float]): An optional timeout in seconds for the operation.
            **kwargs: Additional optional keyword arguments.

        Returns:
            Mapping[str, ValueTypes]: A dictionary with a single key `"person_detected"`:
                - 1 if a person is detected
                - 0 if no person is detected
        """
        #Getting the detections from the camera using the vision resource
        detections = await self.vision.get_detections_from_camera(self.camera_name)
        #Iterating through the detections
        for d in detections:
            #Checking if the class name is "person" and the confidence is greater than 0.5
            if d.class_name.lower() == "person" and d.confidence > 0.5:
                #Returning the result of the do_command method
                return {"person_detected": 1}
        #Returning the result of the do_command method
        return {"person_detected": 0}



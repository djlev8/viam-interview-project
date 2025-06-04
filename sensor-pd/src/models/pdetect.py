# sensor-pd/src/models/pdetect.py
#Importing the necessary typing libraries for the Pdetect sensor class
from typing import (Any, ClassVar, Dict, Final, List, Mapping, Optional,
                    Sequence, Tuple)
#Importing the typing_extensions library for the Self type
from typing_extensions import Self
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
                first element is a list of required dependencies (myPeopleDetector) and the
                second element is a list of optional dependencies (empty in this case)
        """
        #Checking if the camera_name attribute is present in the config
        if "camera_name" not in config.attributes.fields:
            #If the camera_name attribute is not present, raise an exception
            raise Exception("Missing required attribute: camera_name")
        #Returning the list of required dependencies (myPeopleDetector) and an empty list of optional dependencies
        return ["myPeopleDetector"], []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """This method allows you to dynamically update your service when it receives a new `config` object.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any dependencies (both implicit and explicit)
        """
        #Checking if the camera_name attribute is present in the config
        if not config.attributes or "camera_name" not in config.attributes.fields:
            #If the camera_name attribute is not present, raise an exception
            raise ValueError("Missing required attribute: camera_name")
        #Setting the camera_name attribute to the value of the camera_name attribute in the config
        self.camera_name = str(config.attributes.fields["camera_name"].string_value)
        #Getting the vision resource from the dependencies
        vision_resource = dependencies.get(Vision.get_resource_name("myPeopleDetector"))
        #Checking if the vision resource is present
        if not vision_resource:
            #If the vision resource is not present, raise an exception
            raise ValueError("Required dependency 'myPeopleDetector' not found")
        #Setting the vision attribute to the vision resource
        self.vision = vision_resource
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

        This method queries the configured vision service (`myPeopleDetector`) for object
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



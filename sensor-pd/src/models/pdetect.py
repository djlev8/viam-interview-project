from typing import (Any, ClassVar, Dict, Final, List, Mapping, Optional,
                    Sequence, Tuple)

from typing_extensions import Self
from viam.components.sensor import Sensor
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import Geometry, ResourceName
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily
from viam.utils import SensorReading, ValueTypes
from viam.resource.easy_resource import EasyResource

from viam.services.vision import Vision
from viam.services.vision import VisionClient

class Pdetect(Sensor, EasyResource):
    # To enable debug-level logging, either run viam-server with the --debug option,
    # or configure your resource/machine to display debug logs.
    MODEL: ClassVar[Model] = Model(ModelFamily("dl-org", "sensor-pd"), "pdetect")

    def __init__(self, name: str):
        super().__init__(name)
        self.vision: Optional[VisionClient] = None

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
        sensor = cls(config.name)
        sensor.reconfigure(config, dependencies)
        return sensor

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
        if "camera_name" not in config.attributes.fields:
            raise Exception("Missing required attribute: camera_name")
        return ["myPeopleDetector"], []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """This method allows you to dynamically update your service when it receives a new `config` object.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any dependencies (both implicit and explicit)
        """
        if not config.attributes or "camera_name" not in config.attributes.fields:
            raise ValueError("Missing required attribute: camera_name")
            
        self.camera_name = str(config.attributes.fields["camera_name"].string_value)
        
        vision_resource = dependencies.get(Vision.get_resource_name("myPeopleDetector"))
        if not vision_resource:
            raise ValueError("Required dependency 'myPeopleDetector' not found")
            
        self.vision = vision_resource
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
        result = await self.do_command({})
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
        detections = await self.vision.get_detections_from_camera(self.camera_name)
        for d in detections:
            if d.class_name.lower() == "person" and d.confidence > 0.5:
                return {"person_detected": 1}
        return {"person_detected": 0}



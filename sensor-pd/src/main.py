# sensor-pd/src/main.py
#Importing the necessary libraries
#Importing the asyncio library for asynchronous operations
import asyncio
#Importing the Viam SDK components for Module, Registry, ResourceCreatorRegistration, Sensor, and DuplicateResourceError
from viam.module.module import Module
from viam.resource.registry import Registry, ResourceCreatorRegistration
#Importing the Viam SDK components for Sensor
from viam.components.sensor import Sensor
from viam.errors import DuplicateResourceError

#Importing the Pdetect sensor class from the models.pdetect module
try:
    from models.pdetect import Pdetect
except ModuleNotFoundError:
    # when running as local module with run.sh
    from .models.pdetect import Pdetect

#Defining the main function
async def main():
    """
    Register the custom sensor model and start the module.

    This function registers the `Pdetect` sensor model with the Viam resource registry
    and initializes a `Module` instance using command-line arguments. It handles
    duplicate registration errors, then starts the module to serve
    the registered model.
    """
    #Registering the Pdetect sensor model with the Viam resource registry
    try:
        Registry.register_resource_creator(Sensor.API, Pdetect.MODEL, ResourceCreatorRegistration(Pdetect.new, Pdetect.validate_config))
    except DuplicateResourceError:
        #If the Pdetect sensor model is already registered, pass
        pass

    #Initializing a new Module instance using command-line arguments
    module = Module.from_args()
    #Adding the Pdetect sensor model to the module
    module.add_model_from_registry(Sensor.API, Pdetect.MODEL)
    #Starting the module
    await module.start()

if __name__ == '__main__':
    asyncio.run(main())

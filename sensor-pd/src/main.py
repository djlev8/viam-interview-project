import asyncio
from viam.module.module import Module
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.components.sensor import Sensor
from viam.errors import DuplicateResourceError

try:
    from models.pdetect import Pdetect
except ModuleNotFoundError:
    # when running as local module with run.sh
    from .models.pdetect import Pdetect

async def main():
    """
    Register the custom sensor model and start the module.

    This function registers the `Pdetect` sensor model with the Viam resource registry
    and initializes a `Module` instance using command-line arguments. It handles
    duplicate registration errors, then starts the module to serve
    the registered model.
    """
    try:
        Registry.register_resource_creator(Sensor.API, Pdetect.MODEL, ResourceCreatorRegistration(Pdetect.new, Pdetect.validate_config))
    except DuplicateResourceError:
        pass

    module = Module.from_args()
    module.add_model_from_registry(Sensor.API, Pdetect.MODEL)
    await module.start()

if __name__ == '__main__':
    asyncio.run(main())

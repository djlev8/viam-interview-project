import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.camera import Camera
from viam.services.mlmodel import MLModelClient
from viam.services.vision import VisionClient

async def connect():
    """
    Establish a connection to the Viam robot using an API key.

    Returns:
        RobotClient: An authenticated client connected to the robot.
    """
    opts = RobotClient.Options.with_api_key( 
        api_key='MY-API-KEY',
        api_key_id='MY-KEY-ID'
    )
    return await RobotClient.at_address('MY-ROBOT-ADDRESS', opts)

async def main():
    """
    Connects to the robot, initializes camera and vision services, 
    retrieves detected people using a vision model, and prints the results.

    This function demonstrates how to:
        - Connect to a remote Viam robot
        - Retrieve an image from a camera
        - Access an ML model and print its metadata
        - Use a Vision service to detect people in the camera feed
        - Filter detections by confidence and class name

    Raises:
        Exception: If the robot connection fails or services are misconfigured.
    """
    machine = await connect()

    print('Resources:')
    print(machine.resource_names)
    
    # cam
    cam = Camera.from_robot(machine, "cam")
    cam_return_value = await cam.get_image()
    #print(f"cam get_image return value: {cam_return_value}")

    # people
    people = MLModelClient.from_robot(machine, "people")
    people_return_value = await people.metadata()
    #print(f"people metadata return value: {people_return_value}")

    # myPeopleDetector
    my_people_detector = VisionClient.from_robot(machine, "myPeopleDetector")
    #my_people_detector_return_value = await my_people_detector.get_properties()
    #print(f"myPeopleDetector get_properties return value: {my_people_detector_return_value}")

    detected_people = [
        person for person in (await my_people_detector.get_detections_from_camera("cam"))
        if person.confidence > 0.5 and person.class_name == "Person"
    ]
    print(f"detected_people: {detected_people}")

    # Don't forget to close the machine when you're done!
    await machine.close()

if __name__ == '__main__':
    asyncio.run(main())


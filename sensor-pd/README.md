# Module sensor-pd

This module from `dl-org` implements a custom sensor that uses a Viam Vision service to detect whether a person is present in the view of a specified camera. It provides a simplified binary reading (`person_detected`) to indicate detection status. The module queries a configured vision model (e.g. `myPeopleDetector`) and returns 1 if a person is detected with confidence > 0.5, and 0 otherwise.

This module was developed using the Viam Python SDK and supports hot reloading for efficient local development and testing.

## Model dl-org:sensor-pd:pdetect

The `pdetect` model is a sensor component that wraps around a `VisionService` capable of detecting people in a camera feed. It returns a 1 if a person is detected, and a 0 otherwise.

### Configuration

The following attribute template can be used to configure this model:

```json
{
  "camera_name": "<string>"
  "detector_name": "<string>"
}
```

#### Attributes

The following attributes are available for this model:

| Name          | Type   | Inclusion | Description                                                |
|---------------|--------|-----------|------------------------------------------------------------|
| `camera_name` | string | Required  |The name of the camera resource to use for person detection.|
| `detector_name` | string | Required  |The name of the detector to use for person detection.|
|


#### Example Configuration

```json
{
  "camera_name": "cam"
  "detector_name": "myPeopleDetector"
}
```
#### Dependencies

This model requires a configured Vision service (e.g. `VisionService`) that is capable of performing object detection and must be named `myPeopleDetector` (or match the dependency name used in your config):

| Name              | Type           | Inclusion | Description                                                |
|-------------------|----------------|-----------|------------------------------------------------------------|
| `myPeopleDetector`| Vision Service | Required  | A vision model configured to detect people in images.      |
|

The Vision service should be configured to use an ML model that can detect people in a camera feed.

#### Example Vision Service Configuration

```json
{
  "name": "myPeopleDetector",
      "api": "rdk:service:vision",
      "model": "rdk:builtin:mlmodel",
      "attributes": {
      "mlmodel_name": "model-name-that-detects-people"
      }
}
```

### DoCommand

This model implements do_command to run the person detection logic and return a result indicating whether a person was detected.

#### Example DoCommand Response

```json
{
  "person_detected": 1
}
```

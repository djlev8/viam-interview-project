# Viam Solutions Engineer Interview Project

This project demonstrates a custom integration with the Viam (https://www.viam.com) robotics platform using the Python SDK. It includes:

- A custom sensor module (`sensor-pd`) that detects people using Viam's Vision service
- A Python script to test camera, ML model, and vision service connectivity
- Slides and screenshots documenting implementation steps and results

---

## Project Structure

```bash
viam-interview-project/
├── camera_vision/           # Task 1: Vision service test script
├── sensor-pd/               # Task 3: Custom person-detection sensor module
├── screenshots/             # Screenshots/notes documenting steps for Tasks 1,2,3
├── slides/                  # Presentation deck for final submission
├── README.md                # This file
└── .gitignore               # Ignores virtual environments, cache, etc.
```

### Task Overview
---
### Task 1: Vision

Goal: Use a local camera and Viam’s Vision service to detect objects.

•	Configured a laptop camera (cam) in the Viam app.

•	Created a Vision Service (`myPeopleDetector`) using a built-in ML model to detect people.

•	Wrote a script (`camera_vision/vision_service.py`) to test detection logic and print detection output if a “person” is found.

•	Used `get_detections_from_camera()` to verify detection confidence > 0.5.

Directory: `camera_vision/`

Sample output: See `screenshots/task1_person_detected.png`

---
### Task 2: Cloud Integration

Goal: Store camera frames in the cloud and prepare for future ML customization.

•	Enabled Data Capture in the Viam app to log camera snapshots during detection.

•	Verified that image frames were stored under the “Data” tab.

•	Discussed how these frames could be used for training a custom ML model to improve detection.

Configuration done in the Viam UI

Sample output: See `screenshots/task2_data_capture.png`

---
### Task 3: Modular Registry

Goal: Create a custom Sensor Module using the Viam Registry system.

•	Created a custom sensor model: `dl-org:sensor-pd:pdetect`.

•	Calls the Vision Service (myPeopleDetector) internally and returns: `{"person_detected": 1}` if person is detected, `{"person_detected": 0}` otherwise

•	Supports hot reload via reload.sh

•	Full module is documented and available under `sensor-pd/README.md`

Directory: `sensor-pd/`

Test: Navigate to Control > pdetect > Test > GetReadings in Viam app

---
### Task 4: Presentation

Includes a slide deck summarizing:

•	Setup and approach

•	Key code snippets and architecture

•	Screenshots of working implementations

•	Lessons learned and implementation notes

Slides: `slides/viam_project_presentation.pdf`

---
### Notes

•	The `.venv/` folders have been excluded from version control.

•	All custom module code is located in `sensor-pd/src/`.

•	Additional screenshots and a log of all steps taken to complete the three tasks and solve debugging challenges can be found in screenshots/project_notes.pdf.

---
### Contact

For questions about this project, please contact: 

David Levine

david.j.levine8@gmail.com
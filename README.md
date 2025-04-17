# MediapipeFaceLandmarker
## Introduction
`MediapipeFaceLandmarker` is a python script that makes it easy to launch an instance of [Google's Mediapipe Face Landmarker task](%5Benter%20link%20description%20here%5D%28https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker%29).
## Features
- Supports up to Python 3.12 due to mediapipe releases
- Two backends, DirectShow (using [pyGrabber](https://github.com/bunkahle/pygrabber), Windows only) and OpenCV
- Linux support
- Sends data over UDP
- Allows for limited camera discovery
- Very simple, designed for further integration
## Set up
- Clone the repository
- Download the model file available at the bottom of [this webpage](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker)
- Create a virtual enviroment
- Install mediapipe with `pip install mediapipe`
- If you'd like to use the `dshow` backend, also install pygrabber with `pip install pygrabber`
- Windows builds might be set up in the future but as this is is planned to be bundled alongside other tools it is not a priority
## Usage
From the virtual enviroment, run `python main.py <backend>` where the backend is either `dshow` or `opencv`. `dshow` can only be chosen on Windows platforms. Some arguments areonly available on the specific subparser. Use `--help` as needed.

There are some extra args you can change such as:

- Host and Port using `--host` and `--port` respectively
- Camera selection with `--camera` 
- The model filepath defaults to the working folder but can be changed with `--model-file`
- The `dshow` backend can give a detailed camera list with `--list-cameras` and its supported formats with `--list-caps`. It defaults to the first format and can be overriden with `--cap`
- The `opencv` backend is very limited. It will default to 640x480 but you can change it with `--format W H FPS` 

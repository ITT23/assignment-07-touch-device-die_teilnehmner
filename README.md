## 1 Build a Camera-Based Touch Sensor 
- touch-input.py

Program to read the camera feed of the 'touch box' and send DIPPID-events to the local host. To calibrate the program to the current lighting conditions you must place your finger on the touch screen for a 'touch event'. For the calibrating process pay attention to the commands in your terminal. It will tell you the time to put your finger on the 'touch box' and the time it is calibrated and you can start interacting with it. To see the processing steps of the touch-input.py you can read the documentation. The input channel can be configured by setting the 'CAMERA_FEED' constant in the config.py file. By changing the 'DEBUG_FLAG_TOUCH_INPUT' constant to 'True' in the config.py file a video of the processed image will be displayed.

## 2 Multitouch Application
- multitouch-demo.py
- img

Program to receive DIPPID events from the 'touch box' and uses them to manipulate images in a pyglet window. Touch events are represented by a blue circle, hover events are represented by a green circle.

Supported gestures:
- You can move an image by touching it (using a touch event) with one finger and then move your finger while touching.
- You can scale an image by touching it (using touch events) with two fingers and make a pinch gesture
- You can rotate a image by touching it (using touch event) with two fingers and rotate them

## 3 Gesture-Based Application Launcher
- application-launcher.py
- applications.txt
- gesture_templates

Program to start applications on your system by recognizing gestures form the 'touch box' or from the window in which you can draw gestures with you mouse. The path to the program can be specified in the applications.txt by writing it next to the gestures that should be linked to the program separated by on white space for example 'circle /usr/bin/firefox'. The $1 recognizer is used in this implementation, so you should perform your gestures according to https://depts.washington.edu/acelab/proj/dollar/index.html
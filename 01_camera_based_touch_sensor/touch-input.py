'''
This module translates inputs from the touch sensor box into DIPPID events and broadcasts them.

Image processing is performed on each webcam frame to:
-   distinguish fingers
-   detect finger position
-   distinguish between hover and touch
'''
import time
from json import dumps
from socket import AF_INET, SOCK_DGRAM, socket

import config
import cv2
import numpy as np

THRESHOLD_TAB = 35
THRESHOLD_HOVER = 65

IP = '127.0.0.1'
PORT = 5700

message = {
    'events': {}
}
sock = socket(AF_INET, SOCK_DGRAM)
frame_width = 0
frame_height = 0


def calibrate(cap):
    '''
    Calibrates threshold to adapt to different lighting situations

    Args:
        cap     video capture source
    '''
    global THRESHOLD_TAB, THRESHOLD_HOVER
    print("Place finger on touchscreen")
    time.sleep(2)
    print('Starting calibration...')
    time_end = time.time() + 5
    thresholds = []
    while time.time() < time_end:
        thresh = get_otsu_thresh(cap)
        thresholds.append(thresh)
    print('Calibration complete')
    thresh_sum = 0
    for thresh in thresholds:
        thresh_sum += thresh
    average = thresh_sum/len(thresholds)

    THRESHOLD_TAB = average / 2.8
    THRESHOLD_HOVER = average / 1.8


def get_otsu_thresh(cap):
    '''
    Retrieves threshold of Otsu's Binarization on frame

    Args:
        cap     video capture source

    Returns:
        otsu_thresh     value if threshold with Otsu Binarization
    '''
    _, frame = cap.read()
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
    otsu_thresh, _ = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return otsu_thresh


def main():
    '''
    Retrieves frame from webcam, detects fingers and sends DIPPID events according to position and input type
    '''
    global frame_width, frame_height, cap
    cap = cv2.VideoCapture(config.CAMERA_FEED)
    kernel = np.ones((10, 10), dtype=np.float64)
    calibrate(cap)
    while (True):
        touched = False
        event_counter = 0
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        if (frame_width == 0):
            frame_width = len(frame[1])
            frame_height = len(frame)
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        contours = []
        ret, thresh_tab = cv2.threshold(
            img_gray, THRESHOLD_TAB, 255, cv2.THRESH_BINARY)
        dilation_tab = cv2.dilate(thresh_tab, kernel)
        closing_tab = cv2.erode(dilation_tab, kernel)
        contours, hierarchy = cv2.findContours(
            closing_tab, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = filter_contours(contours, hover=False)
        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            x, y, w, h = cv2.boundingRect(contour)
            touched = True
            cv2.rectangle(closing_tab, (x, y), (x+w, y+h), (0, 255, 0), 2)
            construct_event(event_counter, True, x, y)
            event_counter += 1

        blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
        ret, thresh = cv2.threshold(
            img_gray, THRESHOLD_HOVER, 255, cv2.THRESH_BINARY)

        dilation = cv2.dilate(thresh, kernel)
        closing = cv2.erode(dilation, kernel)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = filter_contours(contours, hover=True)

        if (not touched):
            counter = 0
            for contour in contours:
                (x, y), radius = cv2.minEnclosingCircle(contour)
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(closing, (x, y), (x+w, y+h), (0, 255, 0), 2)
                construct_event(event_counter, False, x, y)
                event_counter += 1

        img_contours = cv2.cvtColor(closing_tab, cv2.COLOR_BGR2RGB)
        img_contours = cv2.drawContours(
            img_contours, contours, -1, (255, 0, 0), 3)
        send_data()
        message['events'] = {

        }
        if (config.DEBUG_FLAG_TOUCH_INPUT):
            cv2.imshow('frame', closing)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def construct_event(counter, touched: bool, x, y):
    '''
    Creates a dictionary with x,y coordinates for DIPPID broadcast

    Args:
        intcounter:      identifier for event
        bool touched:    flag whether touching or hovering was performed
        x                x-coordinate
        y                y-coordinate
    '''
    event_type = 'hover'
    x, y = normalize(x, y)
    if (touched):
        event_type = 'touch'
    message['events'][counter] = {
        'type': event_type,
        'x': x,
        'y': y
    }


def normalize(x, y):
    '''
    Transforms a pair of coordinates to their relative position on the frame

    Args:
        x:   x-coordinate
        y:   y-coordinate

    Returns:
        normalized_x    relative x position
        normalized_y    relative y position
    '''
    normalized_x = x/frame_width
    normalized_y = y/frame_height
    return normalized_x, normalized_y


def filter_contours(contours, hover: bool):
    '''
    Filters out contours of certain sizes to remove false positives

    Args;
        List[contours]  List of all contours
        bool            Flag if filtering for hover or touch inputs

    Returns:
        List[contours]  List of filtered contours
    '''
    filtered_contours = []
    for cont in contours:
        epsilon = 0.005*cv2.arcLength(cont, True)
        approx = cv2.approxPolyDP(cont, epsilon, True)
        area = cv2.contourArea(approx)
        if hover and area > 500 and area < 2000:
            (x, y), radius = cv2.minEnclosingCircle(approx)
            filtered_contours.append(approx)
        if not hover and area > 50 and area < 10000:
            filtered_contours.append(approx)
    return filtered_contours


def send_data():
    '''
    Converts the dictionary to a json and sends it to localhost via DIPPID protocol
    '''
    sock.sendto(dumps(message).encode(), (IP, PORT))


main()

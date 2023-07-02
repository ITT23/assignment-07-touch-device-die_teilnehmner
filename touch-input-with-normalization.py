import time
from json import dumps
from socket import AF_INET, SOCK_DGRAM, socket

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
    # TODO
    # Hover over touchscreen
    # Determine threshold with Otsu
    # Substract 50 (or any suitable value) from threshold
    # => THRESHOLD_HOVER

    # either:
    # repeat for THRESHOLD_TAB

    # substract higher value from threshold to generate THRESHOLD_TAB
    global THRESHOLD_TAB, THRESHOLD_HOVER
    # Don't place anything on touchscreen
    print("Place finger on touchscreen")
    time.sleep(2)
    print('Starting calibration...')
    # Place finger on touchscreen
    time_end = time.time() + 5
    while time.time() < time_end:
        thresh = get_otsu_thresh(cap)
    print('Calibration complete')
    print(thresh)

    THRESHOLD_TAB = thresh/2.5
    THRESHOLD_HOVER = thresh/1.5
    # print(f'Difference Hover: {otsu_thresh-THRESHOLD_HOVER}')
    # print(f'Difference Tab: {otsu_thresh-THRESHOLD_TAB}')


def get_otsu_thresh(cap):
    _, frame = cap.read()
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
    otsu_thresh, _ = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return otsu_thresh


def main():
    global frame_width, frame_height, cap
    cap = cv2.VideoCapture(6)
    kernel = np.ones((10, 10), dtype=np.float64)
    calibrate(cap)
    while (True):
        touched = False
        event_counter = 0
        ret, frame = cap.read()
        if (frame_width == 0):
            frame_width = len(frame[1])
            frame_height = len(frame)
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        contours = []
        # Threshold Tab
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
            if (radius > 40 or radius < 1):
                continue
            touched = True
            cv2.rectangle(thresh_tab, (x, y), (x+w, y+h), (0, 255, 0), 2)
            # center = (int(x), int(y))
            # radius = int(radius)
            construct_event(event_counter, True, x, y)
            event_counter += 1
            # cv2.circle(thresh_tab, center, radius, (0,255,0), 2)

        # Threshold hover
        blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
        ret, thresh = cv2.threshold(
            img_gray, THRESHOLD_HOVER, 255, cv2.THRESH_BINARY)

        dilation = cv2.dilate(thresh, kernel)
        closing = cv2.erode(dilation, kernel)
        contours, _ = cv2.findContours(
            closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = filter_contours(contours, hover=True)

        if (not touched):
            for contour in contours:
                (x, y), radius = cv2.minEnclosingCircle(contour)
                x, y, w, h = cv2.boundingRect(contour)
                if (radius > 40 or radius < 10):
                    continue
                cv2.rectangle(closing, (x, y), (x+w, y+h), (0, 255, 0), 2)
                # center = (int(x), int(y))
                # radius = int(radius)
                construct_event(event_counter, False, x, y)
                # cv2.circle(thresh, center, radius, (0,0,255), 2)

        img_contours = cv2.cvtColor(thresh_tab, cv2.COLOR_BGR2RGB)
        img_contours = cv2.drawContours(
            img_contours, contours, -1, (255, 0, 0), 3)
        send_data()
        message['events'] = {

        }
        # cv2.drawContours(img_contours, contours, -1, (255, 0, 0), 3)
        cv2.imshow('frame', img_contours)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # to quite the program
            break


def construct_event(counter, touched, x, y):
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
    normalized_x = x/frame_width
    normalized_y = y/frame_height
    return normalized_x, normalized_y


def filter_contours(contours, hover: bool):
    filtered_contours = []
    for cont in contours:
        epsilon = 0.005*cv2.arcLength(cont, True)
        approx = cv2.approxPolyDP(cont, epsilon, True)
        area = cv2.contourArea(approx)
        if hover and area > 1000 and area < 5000:
            (x, y), radius = cv2.minEnclosingCircle(approx)
            if (radius > 80) or (radius < 10):
                continue
            filtered_contours.append(approx)
        if not hover and area > 150 and area < 2000:
            filtered_contours.append(approx)
    return filtered_contours


def send_data():
    # print(message)
    # converts the dict to a json and sends it to local host
    sock.sendto(dumps(message).encode(), (IP, PORT))


main()

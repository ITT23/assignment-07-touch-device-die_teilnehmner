from json import dumps
from socket import AF_INET, SOCK_DGRAM, socket

import cv2
import numpy as np

THRESHOLD_TAB = 30
THRESHOLD_HOVER = 65

IP = '127.0.0.1'
PORT = 5700

message = {
    'events': {

    }
}
sock = socket(AF_INET, SOCK_DGRAM)
frame_width = 0
frame_height = 0


# def calibrate():
#     global hover_thresh, touch_thresh, frame_width, frame_height
#     kernel =
#     hover_thresh = 100
#     print("Hover finger over center of touchscreen")
#     ret, frame = cap.read()
#     # while True:
#     #     cv2.imshow('frame', frame)
#     #     if cv2.waitKey(1) & 0xFF == ord('q'):  # to quite the program
#     #         break
#     if (frame_width == 0):
#         frame_width = len(frame[1])
#         frame_height = len(frame)
#     img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     contours = []
#     ret, thresh = cv2.threshold(img_gray, hover_thresh, 255, cv2.THRESH_BINARY)
#     dilation = cv2.dilate(thresh, kernel)
#     closing = cv2.erode(dilation, kernel)
#     contours, hierarchy = cv2.findContours(
#         closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#     contours = filter_contours(contours)

#     print(len(contours))

#     while len(contours) != 0:
#         hover_thresh = hover_thresh - 5
#         ret, thresh = cv2.threshold(
#             img_gray, hover_thresh, 255, cv2.THRESH_BINARY)
#         dilation = cv2.dilate(thresh, kernel)
#         closing = cv2.erode(dilation, kernel)
#         contours, hierarchy = cv2.findContours(
#             closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#         contours = filter_contours(contours)
#         if len(contours) == 1:
#             upper_bound = hover_thresh
#         print(f'Recalibrating: thresh at {hover_thresh}')

#     print(f'Tresh between {hover_thresh} and {upper_bound}')


def main():
    global frame_width, frame_height, cap
    cap = cv2.VideoCapture(6)
    kernel = np.ones((10, 10), dtype=np.float64)
    # calibrate()
    while (True):
        # read image
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
        # dilation_tab = cv2.dilate(thresh_tab, kernel)
        # closing_tab = cv2.erode(dilation_tab, kernel)
        # thresh = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        contours, hierarchy = cv2.findContours(
            thresh_tab, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = filter_contours(contours)
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
        ret, thresh = cv2.threshold(
            img_gray, THRESHOLD_HOVER, 255, cv2.THRESH_BINARY)
        # thresh = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        dilation = cv2.dilate(thresh, kernel)
        closing = cv2.erode(dilation, kernel)
        contours, hierarchy = cv2.findContours(
            closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = filter_contours(contours)

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


def filter_contours(contours):
    filtered_contours = []
    for cont in contours:
        epsilon = 0.005*cv2.arcLength(cont, True)
        approx = cv2.approxPolyDP(cont, epsilon, True)
        area = cv2.contourArea(approx)
        print(area)
        if area > 1000 and area < 5000:
            # (x, y), radius = cv2.minEnclosingCircle(approx)
            # if (radius > 80) or (radius < 10):
            #     continue
            filtered_contours.append(approx)
    return filtered_contours


def send_data():
    print(message)
    # sock.sendto(dumps(message).encode(), (IP, PORT)) # converts the dict to a json and sends it to local host


main()

import os
import sys
import time
from json import dumps
from socket import AF_INET, SOCK_DGRAM, socket

import config
import pyglet
from DIPPID import SensorUDP
from dollar_recognizer import Dollar_Recognizer
from pynput import mouse

sock = socket(AF_INET, SOCK_DGRAM)
sensor = SensorUDP(config.PORT)
timer = 0
window = pyglet.window.Window(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)


def setup_gestures():
    gesture_mapping = []
    with open('03_gesture_based_application_launcher/applications.txt', encoding='utf8') as file:
        for line in file:
            line = line.strip('\n')
            tokens = line.split()
            if len(tokens) != 2:
                print(
                    f"Line:\n{line}\nin 'applications.txt could not be parsed")
                continue
            if tokens[0] not in config.LABELS:
                print(
                    f"'{tokens[0]}' is not a valid gesture. It has to be one of the following:\n{config.LABELS}")
                continue
            if not os.path.exists(tokens[1]):
                print(f"Couldn't find '{tokens[1]}'")
                continue
            gesture_mapping.append({
                'gesture': tokens[0],
                'program': tokens[1]
            })
    return gesture_mapping


def init():
    global coords, gestures, recognizer
    gestures = setup_gestures()
    if gestures:
        recognized_gestures = get_gesture_labels(gestures)
        recognizer = Dollar_Recognizer(recognized_gestures)
    else:
        print('You have to enter gestures with paths in your application.txt')
        return

    coords = []


@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.Q:
        window.close()
        sys.exit()


@window.event
def on_draw():
    global coords, timer
    events = sensor.get_value('events')
    if events:
        for event in events:
            type = events[event]['type']
            if (type == 'touch'):
                timer = time.time()
                x = events[event]['x']
                y = events[event]['y']
                coords.append([x, y])
    elif coords and (time.time() - timer > 0.5):
        recognize()
        coords = []
        timer = 0


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    y = config.WINDOW_HEIGHT - y
    x /= config.WINDOW_WIDTH
    y /= config.WINDOW_HEIGHT
    message = {
        'events': {
            0: {
                'type': 'touch',
                'x': x,
                'y': y
            }
        }
    }
    sock.sendto(dumps(message).encode(), (config.IP, config.PORT))


@window.event
def on_mouse_release(x, y, button, modifiers):
    message = {
        'events': {}
    }
    sock.sendto(dumps(message).encode(), (config.IP, config.PORT))


def recognize():
    global coords
    print(coords)
    if (coords[0][0] == coords[len(coords) - 1][0] and coords[0][1] == coords[len(coords) - 1][1]):
        return
    result = recognizer.recognize(coords)
    print(result)
    for mapping in gestures:
        if mapping['gesture'] == result[0]:
            os.system(mapping['program'])


def get_gesture_labels(gestures):
    recognized_gestures = []
    for gesture in gestures:
        recognized_gestures.append(gesture['gesture'])
    return recognized_gestures


if __name__ == '__main__':
    init()
    pyglet.app.run()

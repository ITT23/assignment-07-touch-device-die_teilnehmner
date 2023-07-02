'''
This module launches programs depending on an input gesture.

Gestures are received via the DIPPID protocol and are classified using Wobbock et al's One Dollar Recognizer.
Gestures and programs can be customized in the 'applications.txt' file.
'''
import os
import sys
import time
from json import dumps
from socket import AF_INET, SOCK_DGRAM, socket

import config
import pyglet
from dollar_recognizer import Dollar_Recognizer

from DIPPID import SensorUDP

sock = socket(AF_INET, SOCK_DGRAM)
sensor = SensorUDP(config.PORT)
window = pyglet.window.Window(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)


def setup_gestures() -> dict[str, str]:
    '''
    Reads and validates gestures and program paths from 'applications.txt'

    Returns:
        dict[str,str]: Mapping of gesture and corresponding program
    '''
    gesture_mapping: dict[str, str] = {}
    with open('03_gesture_based_application_launcher/applications.txt', encoding='utf8') as file:
        for line in file:
            line = line.strip('\n')
            tokens = line.split()
            if len(tokens) != 2:
                print(
                    f"Line:\n{line}\nin 'applications.txt' could not be parsed")
                continue
            if tokens[0] not in config.LABELS:
                print(
                    f"'{tokens[0]}' is not a valid gesture. It has to be one of the following:\n{config.LABELS}")
                continue
            if not os.path.exists(tokens[1]):
                print(f"Couldn't find '{tokens[1]}'")
                continue
            gesture_mapping[tokens[0]] = tokens[1]
    return gesture_mapping


def init():
    '''
    Sets up global variables and One Dollar Recognizer
    '''
    global coords, gestures, recognizer, timer
    gestures = setup_gestures()
    if gestures:
        recognizer = Dollar_Recognizer(gestures.keys())
    else:
        print("You have to add gestures and paths to your 'applications.txt'")
        return
    coords = []
    timer = 0


@window.event
def on_draw():
    '''
    Catches DIPPID events and starts recognition
    '''
    window.clear()
    global coords, timer
    events = sensor.get_value('events')
    if events:
        for event in events:
            event_type = events[event]['type']
            if event_type == 'touch':
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
    '''
    Sends DIPPID events with mouse coordinates whenever left mouse button is pressed and mouse is moved
    '''
    if buttons & pyglet.window.mouse.LEFT:
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
def on_key_press(symbol, modifiers):
    '''
    Exits script on 'Q' press
    '''
    if symbol == pyglet.window.key.Q:
        window.close()
        sys.exit()


@window.event
def on_mouse_release(x, y, button, modifiers):
    '''
    Sends empty DIPPID event when a mouse button is released to indicate end of gesture input
    '''
    message = {
        'events': {}
    }
    sock.sendto(dumps(message).encode(), (config.IP, config.PORT))


def recognize():
    '''
    Retrieves One Dollar Recognizer result and launches corresponding program
    '''
    print(coords)
    # Brauchen wir das?
    # if (coords[0][0] == coords[-1][0] and coords[0][1] == coords[-1][1]):
    #     return
    result = recognizer.recognize(coords)
    print(result)
    for label, program in gestures.items():
        if label == result[0]:
            os.system(program)


if __name__ == '__main__':
    init()
    pyglet.app.run()

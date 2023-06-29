import os
from dollar_recognizer import Dollar_Recognizer
import config
from pynput import mouse
from json import dumps
import pyglet
from socket import socket, AF_INET, SOCK_DGRAM
from DIPPID import SensorUDP
import time

IP = '127.0.0.1'
PORT = 5700
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

sock = socket(AF_INET, SOCK_DGRAM)
sensor = SensorUDP(PORT)
timer = 0

def on_click(x, y, button, pressed):
    global mouse_pressed
    print(pressed)
    if button == mouse.Button.right and pressed:
        mouse_pressed = pressed
    else:
        mouse_pressed = not pressed
        return False


def on_move(x, y):
    global coords
    y = WINDOW_HEIGHT - y
    x /= WINDOW_WIDTH
    y /= WINDOW_HEIGHT
    message = {
        'events': {
            0 : {
                'type' : 'touch',
                'x' : x,
                'y' : y
            }
        }
    }
    sock.sendto(dumps(message).encode(), (IP, PORT))


def setup_gestures():
    gesture_mapping = []
    with open('applications.txt', encoding='utf8') as file:
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


def run():
    global coords, mouse_pressed, gestures, recognizer
    gestures = setup_gestures()
    if(len(gestures) != 0):
        recognized_gestures = get_gestures(gestures)
        recognizer = Dollar_Recognizer(recognized_gestures)
    else:
        print('you have to enter gestures with paths in your application.txt')
        return
    #recognizer = Dollar_Recognizer()
    win = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
    coords = []
    @win.event
    def on_draw():
        global coords, timer
        events = sensor.get_value('events')
        if(events != None and len(events) != 0):
            for event in events:
                type = events[event]['type']
                if(type == 'touch'):
                    timer = time.time()
                    x = events[event]['x']
                    y = events[event]['y']
                    coords.append([x, y])
        elif(len(coords) != 0 and time.time() - timer > 0.5):
            recognize()
            coords = []
        #print(coords)
    @win.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        on_move(x, y)
    @win.event
    def on_mouse_release(x, y, button, modifiers):
        message = {
            'events': {
            
            }
        }
        sock.sendto(dumps(message).encode(), (IP, PORT))

    pyglet.app.run()


def recognize():
    global coords
    print(coords)
    #for coord in coords:
        #coord[0] = coord[0] * WINDOW_WIDTH
        #coord[1] = coord[1] * WINDOW_HEIGHT
    #print(coords)
    if(coords[0][0] == coords[len(coords) - 1][0] and coords[0][1] == coords[len(coords) - 1][1]):
        return
    result = recognizer.recognize(coords)
    print(result)
    for mapping in gestures:
        if mapping['gesture'] == result[0]:
            os.system(mapping['program'])

def get_gestures(gestures):
    recognized_gestures =  []
    for i in range(3):
        recognized_gestures.append(gestures[i]['gesture'])
    return recognized_gestures




if __name__ == '__main__':
    run()

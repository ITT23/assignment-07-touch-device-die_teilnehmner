import os
from dollar_recognizer import Dollar_Recognizer
import config
from pynput import mouse
from json import dumps
import pyglet
from socket import socket, AF_INET, SOCK_DGRAM
from DIPPID import SensorUDP

IP = '127.0.0.1'
PORT = 5700
#sensor = SensorUDP(PORT)
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

sock = socket(AF_INET, SOCK_DGRAM)
sensor = SensorUDP(PORT)
recognizer = Dollar_Recognizer()

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
    #if mouse_pressed:
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
    #coords.append(dumps(message).encode())
    #print(coords)


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
    global coords, mouse_pressed, gestures
    gestures = setup_gestures()
    #recognizer = Dollar_Recognizer()
    win = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
    coords = []
    @win.event
    def on_draw():
        global coords
        events = sensor.get_value('events')
        if(events != None and len(events) != 0):
            for event in events:
                type = events[event]['type']
                if(type == 'touch'):
                    x = events[event]['x']
                    y = events[event]['y']
                    coords.append([x, y])
        elif(len(coords) != 0):
            recognize()
            coords = []
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
    #while True:
        #coords = []
        #mouse_pressed = False
        #with mouse.Listener(on_click=on_click, on_move=on_move, suppress=False) as listener:
            #listener.join()
        #if coords:
            #result = recognizer.recognize(coords)
            #print(result)
            #for mapping in gestures:
                #if mapping['gesture'] == result[0]:
                    #os.system(mapping['program'])

def recognize():
    global coords
    print(coords)
    #for coord in coords:
        #coord[0] = coord[0] * WINDOW_WIDTH
        #coord[1] = coord[1] * WINDOW_HEIGHT
    #print(coords)
    result = recognizer.recognize(coords)
    print(result)
    for mapping in gestures:
        if mapping['gesture'] == result[0]:
            os.system(mapping['program'])


if __name__ == '__main__':
    run()

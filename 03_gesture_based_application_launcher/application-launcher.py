import os
from dollar_recognizer import Dollar_Recognizer
import config
from pynput import mouse


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
    if mouse_pressed:
        coords.append([x, y])


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


def run():
    global coords, mouse_pressed
    gestures = setup_gestures()
    recognizer = Dollar_Recognizer()
    while True:
        coords = []
        mouse_pressed = False
        with mouse.Listener(on_click=on_click, on_move=on_move, suppress=True) as listener:
            listener.join()
        result = recognizer.recognize(coords)
        print(result)
        for mapping in gestures:
            if mapping['gesture'] == result[0]:
                os.system(mapping['program'])


if __name__ == '__main__':
    run()

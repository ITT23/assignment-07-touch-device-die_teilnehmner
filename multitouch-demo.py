'''
This module launches a program that receives input events in the DIPPID-format form the touch box and can be used to manipulate images with it.

When you touch with one finger on an image you can move it around.

When you touch with two fingers on an image you can scale it by using a pinch gesture and rotate it with the rotation of your fingers.

A blue circle indicates a touch event, a green circle indicates a hover event.
'''
import math
import os
import random
import sys
import numpy as np
import pyglet
from DIPPID import SensorUDP
import config

TOUCH_RADIUS = 10
HOVER_RADIUS = 20
SCALING_FACTOR = 0.008
MOVE_REJECTION = 50

window = pyglet.window.Window(fullscreen=True)
sensor = SensorUDP(config.PORT)
'''
list to store the received events, is reset after the events are read
'''
current_events = []
'''
dict to store the images with corresponding events
'''
current_events_dict = {

}
'''
dict to safe the last events when new events are detected to recognize gestures
'''
last_events = {

}

'''
Event class to represent the DIPPID events
'''
class Event:
    def __init__(self, type, x, y):
        self.type = type
        self.x = x
        self.y = y


'''
This method is used to load the images in the 'img' folder and display them in random positions and with random rotations
'''
def init():
    global batch, sprites, backgound_group, foreground_group
    batch = pyglet.graphics.Batch()
    backgound_group = pyglet.graphics.Group(order=0)
    foreground_group = pyglet.graphics.Group(order=1)
    sprites = []
    for root, _, files in os.walk('img'):
        for file in files:
            file_type = file.split('.')[-1]
            if file_type in ['jpg', 'png']:
                sprite_image = pyglet.image.load(f'{root}/{file}')
                sprite_image.anchor_x = sprite_image.width//2
                sprite_image.anchor_y = sprite_image.height//2
                sprite = pyglet.sprite.Sprite(
                    sprite_image, batch=batch)
                sprite.scale = random.uniform(0.1, 0.5)
                x_pos = random.randint(sprite.width//2,
                                       (window.width-sprite.width//2))
                y_pos = random.randint(sprite.height//2,
                                       window.height-sprite.height//2)
                random_rotation = random.randint(0, 359)
                sprite.update(x=x_pos, y=y_pos, rotation=random_rotation)
                sprites.append(sprite)
                last_events[id(sprite)] = []

'''
This method checks if an event (represented by an x- and y-coordinate) lies in any picture.
It returns the picture the event is in and 'None' if there is no picture at this point.
Sprites with events are grouped in the foreground, sprites with no events are grouped in a background group
Idea from: https://pyglet.readthedocs.io/en/latest/modules/graphics/#pyglet.graphics.Group
'''
def get_selected_sprite(x_pos: int, y_pos: int) -> pyglet.sprite.Sprite | None:
    selected_sprite = None
    for sprite in sprites:
        x = sprite.x
        y = sprite.y
        height = sprite.height
        width = sprite.width
        angle = sprite.rotation / 180 * np.pi

        '''
        Rotate the coordinates of the event when the image is rotated to check if the are in the rotated image
        '''
        rotated_x_pos = x + math.cos(angle) * \
            (x_pos - x) - math.sin(angle) * (y_pos - y)
        rotated_y_pos = y + math.sin(angle) * \
            (x_pos - x) + math.cos(angle) * (y_pos - y)

        if rotated_x_pos < (x-width//2) or rotated_x_pos > (x + width//2):
            if sprite.group == foreground_group:
                sprite.group = backgound_group
            continue
        if rotated_y_pos < (y-height//2) or rotated_y_pos > (y + height//2):
            if sprite.group == foreground_group:
                sprite.group = backgound_group
            continue
        if sprite.group == foreground_group:
            return sprite
        selected_sprite = sprite
    if selected_sprite:
        selected_sprite.group = foreground_group
    return selected_sprite


@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.Q:
        sys.exit(0)

'''
In every draw cycle the program checks for new DIPPID-events, updates the cursor positions and checks if the events are in an image.
'''
@window.event
def on_draw():
    window.clear()
    get_dippid_events()
    update_cursors()
    check_events()

    batch.draw()

'''
This method checks for DIPPID-events, calculates the absolute positions, and writes them in the current event list
'''
def get_dippid_events():
    global current_events
    current_events = []
    events = sensor.get_value('events')
    if (events != None):
        for event in events:
            type = events[event]['type']
            x = events[event]['x']
            y = events[event]['y']
            x = x * window.width
            y = window.height - (y * window.height)
            current_events.append(Event(type, x, y))

'''
This method creates a 'cursors' list and fills it with circles to represent the DIPPID-events
'''
def update_cursors():
    global cursors
    cursors = []
    cursor_group = pyglet.graphics.Group(order=2)
    for event in current_events:
        touch_event = False
        if (event.type == 'touch'):
            touch_event = True
        if touch_event:
            '''
            Touch events are represented by a smaller blue circle
            '''
            cursors.append(pyglet.shapes.Circle(event.x, event.y, TOUCH_RADIUS, color=(
                0, 0, 255), batch=batch, group=cursor_group))
        else:
            '''
            Hover events are represented by a bigger green circle
            '''
            cursors.append(pyglet.shapes.Circle(event.x, event.y, HOVER_RADIUS, color=(
                0, 255, 0), batch=batch, group=cursor_group))

'''
This method handles the events and image manipulation. It checks for every event if it is positioned in a image.
If there is one touch event in a sprite the image will be moved.
If there are two fingers in a sprite the image will be scaled and rotated
'''
def check_events():
    global current_events_dict, last_events, current_events
    last_events = current_events_dict
    current_events_dict = {}
    for event in current_events:
        if(event.type != 'touch'):
            continue
        sprite = get_selected_sprite(event.x, event.y)
        if(sprite == None):
            continue
        if id(sprite) in current_events_dict:
            current_events_dict[id(sprite)].append(event)
        else:
            current_events_dict[id(sprite)] = [event]
    for key in current_events_dict:
        if key in current_events_dict and key in last_events:
            if (len(current_events_dict[key]) == 1 and len(last_events[key]) == 1):
                move_picture(last_events[key][0], current_events_dict[key][0], get_sprite(key))
            elif(len(current_events_dict[key]) == 2 and len(last_events[key]) == 2):
                scale_picture(last_events[key], current_events_dict[key], get_sprite(key))
                rotate_picture(last_events[key], current_events_dict[key], get_sprite(key))
            elif(len(current_events_dict[key]) > 2):
                print('you should use 2 fingers per sprite at maximum')

'''
Helper function to return the sprite object that belongs to the id that is given
'''
def get_sprite(sprite_id):
    for sprite in sprites:
        if(id(sprite) == sprite_id):
            return sprite     

'''
Method to move a given picture at the distance of two events
'''
def move_picture(first_event, second_event, sprite):
    dx = second_event.x - first_event.x
    dy = second_event.y - first_event.y
    # used to be more robust against false move detections
    if(dx > MOVE_REJECTION or dy > MOVE_REJECTION):
        return
    new_x = sprite.x + dx
    new_y = sprite.y + dy
    sprite.update(x=new_x, y=new_y)

'''
This method requires two event-lists (two events that exist at the same time) and a sprite.
It calculates the difference in distance between the two event lists to detect pinch gestures.
The image is scaled according to the detected distance difference.
'''
def scale_picture(first_event_list, second_event_list, sprite):
    previous_distance = calc_distance(first_event_list)
    current_distance = calc_distance(second_event_list)
    pinch_distance = current_distance - previous_distance

    scale = sprite.scale
    if (pinch_distance > 0):
        scale += SCALING_FACTOR
    elif (pinch_distance < 0):
        scale -= SCALING_FACTOR
    sprite.update(scale=scale)

'''
Helper function to calculate the distance between two events in a event list
'''
def calc_distance(event_list):
    first_event = event_list[0]
    second_event = event_list[1]
    dx = abs(first_event.x - second_event.x)
    dy = abs(first_event.y - second_event.y)
    d_square = (dx ** 2) + (dy ** 2)
    d = math.sqrt(d_square)
    return d

'''
This method requires two event-lists (two events that exist at the same time) and a sprite.
It calculates the angle between these two event list and rotates the given sprite accordingly
'''
def rotate_picture(first_event_list, second_event_list, sprite):
    rotation_angle_rad = get_angle(first_event_list, second_event_list)
    if(rotation_angle_rad > 1 or rotation_angle_rad < -1):
        return
    rotation_angle = -math.degrees(rotation_angle_rad)
    sprite.update(rotation=sprite.rotation + rotation_angle)

'''
Helper function to calculate the angle between the two event lists.
The code is based on: https://stackoverflow.com/questions/2663570/how-to-calculate-both-positive-and-negative-angle-between-two-lines
'''
def get_angle(first_event_list, second_event_list):

    a = first_event_list[1].x - first_event_list[0].x
    b = first_event_list[1].y - first_event_list[0].y
    c = second_event_list[1].x - second_event_list[0].x
    d = second_event_list[1].y - second_event_list[0].y


    atanA = math.atan2(a, b)
    atanB = math.atan2(c, d)

    return atanA - atanB

if __name__ == '__main__':
    init()
    pyglet.app.run()

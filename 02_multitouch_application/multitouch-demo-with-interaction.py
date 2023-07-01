import os
import random
import sys
import math

import pyglet

from DIPPID import SensorUDP

# TODO
# click detection on sprite
# receive dippida
# render cursors according to dippid events
# shape manipulation
# distinguish gestures

PORT = 5700

#window = pyglet.window.Window(fullscreen=True)
window = pyglet.window.Window(800, 600)
sensor = SensorUDP(PORT)
# list to store the received events (should be reset after the events are read)
current_events = []
last_events = {

}

class Event:
    def __init__(self, type, x, y):
        self.type = type
        self.x = x
        self.y = y
        


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
                sprite = pyglet.sprite.Sprite(
                    sprite_image, batch=batch)
                sprite.scale = random.uniform(0.1, 0.5)
                x_pos = random.randrange(
                    (window.width-sprite.width))
                y_pos = random.randrange(
                    window.height-sprite.height)
                sprite.update(x=x_pos, y=y_pos)
                sprites.append(sprite)
                last_events[id(sprite)] = []


# Idee:
# Wenn man auf einen sprite clickt fügt man ihn zur foreground gruppe hinzu
# => wird vor allen anderen sprites dargestellt
# Click auf anderen Sprite:
# => alle Sprites zur Gruppe background, geclickter sprite zur gruppe foreground
# https://pyglet.readthedocs.io/en/latest/modules/graphics/#pyglet.graphics.Group


@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.Q:
        sys.exit(0)


@window.event
def on_draw():
    window.clear()
    get_dippid_events()
    check_events_in_sprite()
    update_cursors()
    batch.draw()

# receives dippid events and stores them in the current event list
def get_dippid_events():
    global current_events
    current_events = []
    events = sensor.get_value('events')
    if(events != None):
        for event in events:
            type = events[event]['type']
            x = events[event]['x']
            y = events[event]['y']
            x = x * window.width
            y = window.height - (y * window.height)
            current_events.append(Event(type, x, y))

def update_cursors():
    global cursors
    cursors = []
    cursor_group = pyglet.graphics.Group(order=2)
    for event in current_events:
        touch_event = False
        if(event.type == 'touch'):
            touch_event = True
        if touch_event:
            cursors.append(pyglet.shapes.Circle(event.x, event.y, 10, color=(0, 0, 255), batch= batch, group= cursor_group))
        else:
            cursors.append(pyglet.shapes.Circle(event.x, event.y, 20, color=(0, 255, 0), batch= batch, group= cursor_group))

def check_events_in_sprite():
    global sprites, current_events, last_events
    for sprite in sprites:
        event_list = []
        if(len(last_events[id(sprite)]) != 0):
            for event in current_events:
                if(check_event_in_sprite(event, sprite)):
                    event_list.append(event)
            if(len(event_list) == len(last_events[id(sprite)])):
                if(len(event_list) == 1):
                    move_picture(last_events[id(sprite)][0], event_list[0], sprite)
                if(len(event_list) == 2):
                    scale_picture(last_events[id(sprite)], event_list, sprite)
                    #rotate_picture(last_events[id(sprite)], event_list, sprite)
                if(len(event_list) >= 2):
                    print('you should use 2 fingers per sprite at maximum')
            last_events[id(sprite)] = event_list
            return
        for event in current_events:
            if(check_event_in_sprite(event, sprite)):
                    event_list.append(event)
            last_events[id(sprite)] = event_list



def check_event_in_sprite(event, sprite):
    if(event.type == 'touch'):
        if(event.x < sprite.x + sprite.width and event.x > sprite.x):
            if(event.y < sprite.y + sprite.height and event.y > sprite.y):
                return True
    return False

def move_picture(first_event, second_event, sprite):
    dx =  second_event.x - first_event.x
    dy =  second_event.y - first_event.y
    new_x = sprite.x + dx
    new_y = sprite.y + dy
    sprite.update(x= new_x, y= new_y)

def scale_picture(first_event_list, second_event_list, sprite):
    previous_distance = calc_distance(first_event_list)
    current_distance = calc_distance(second_event_list)
    pinch_distance = current_distance - previous_distance

    sprite_diagonal = math.sqrt((sprite.width ** 2) + (sprite.height ** 2))
    base_value = sprite_diagonal - (sprite_diagonal * (sprite.scale - 1))
    scale = (sprite_diagonal + pinch_distance) / base_value
    sprite.update(scale= scale)

def rotate_picture(first_event_list, second_event_list, sprite):
    midpoint_x = ((first_event_list[0].x - first_event_list[1].x) / 2) + first_event_list[1].x
    midpoint_y = ((first_event_list[0].y - first_event_list[1].y) / 2) + first_event_list[1].y

    a = calc_distance([first_event_list[0], Event('helper_event', midpoint_x, midpoint_y)])
    c = calc_distance([second_event_list[0], Event('helper_event', midpoint_x, midpoint_y)])


    rotation_angle = math.acos(a/c)

    sprite.update(rotation= sprite.rotation + rotation_angle)


def calc_distance(event_list):
    first_event = event_list[0]
    second_event = event_list[1]
    dx = abs(first_event.x - second_event.x)
    dy = abs(first_event.y - second_event.y)
    d_square = (dx ** 2) + (dy ** 2)
    d = math.sqrt(d_square)
    return d




if __name__ == '__main__':
    init()
    pyglet.app.run()
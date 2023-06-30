import os
import random
import sys

import pyglet

from DIPPID import SensorUDP

# TODO
# click detection on sprite
# receive dippida
# render cursors according to dippid events
# shape manipulation
# distinguish gestures

PORT = 5700

window = pyglet.window.Window(fullscreen=True)
sensor = SensorUDP(PORT)
# list to store the received events (should be reset after the events are read)
current_events = []

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
    print(cursors)
    for event in current_events:
        touch_event = False
        if(event.type == 'touch'):
            touch_event = True
        if touch_event:
            cursors.append(pyglet.shapes.Circle(event.x, event.y, 10, color=(0, 0, 255), batch= batch, group= cursor_group))
        else:
            cursors.append(pyglet.shapes.Circle(event.x, event.y, 20, color=(0, 255, 0), batch= batch, group= cursor_group))

if __name__ == '__main__':
    init()
    pyglet.app.run()




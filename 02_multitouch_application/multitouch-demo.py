import os
import random
import sys

import pyglet

# TODO
# click detection on sprite
# receive dippida
# render cursors according to dippid events
# shape manipulation
# distinguish gestures

window = pyglet.window.Window(fullscreen=True)


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
    batch.draw()


if __name__ == '__main__':
    init()
    pyglet.app.run()

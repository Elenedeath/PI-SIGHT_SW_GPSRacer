#!/usr/bin/python

import os

from pynput import keyboard

def keymap():
    """keyboard mapping"""

    global preview_on
    preview_on = False

    def on_press(key):

        global preview_on

        try:
            if key.char == 'u':
                keyboard.Controller().press(keyboard.Key.shift)
                keyboard.Controller().press(keyboard.Key.tab)
                keyboard.Controller().release(keyboard.Key.tab)
                keyboard.Controller().release(keyboard.Key.shift)

            elif key.char == 'd':
                keyboard.Controller().press(keyboard.Key.tab)
                keyboard.Controller().release(keyboard.Key.tab)

            elif key.char == 'l':
                keyboard.Controller().press(keyboard.Key.left)
                keyboard.Controller().release(keyboard.Key.left)

            #elif key.char == 'a':

            elif key.char == 'r':
                keyboard.Controller().press(keyboard.Key.right)
                keyboard.Controller().release(keyboard.Key.right)

            #elif key.char == 'z':

            elif key.char == 'e':
                keyboard.Controller().press(keyboard.Key.space)
                keyboard.Controller().release(keyboard.Key.space)

            #elif key.char == 'q':

            #elif key.char == 'f':

            elif key.char == 'g':
                os.system('xset dpms force off')

        except AttributeError:
            pass

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def main():
    keymap()

if __name__ == '__main__':
    main()

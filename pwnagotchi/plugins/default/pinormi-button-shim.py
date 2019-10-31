__author__ = 'Tisboyo'
__version__ = '1.0.0'
__name__ = 'pinormi-button-shim'
__license__ = 'GPL3'
__description__ = 'This plugin allows the use of the Pinormi Button Shim'

'''
Pinormi Button Shim - https://shop.pimoroni.com/products/button-shim
Install with: curl https://get.pimoroni.com/buttonshim | bash
'''

import logging
import subprocess
import buttonshim


# Will be set with the options in config.yml config['main']['plugins'][__name__]
OPTIONS = dict()

button_held = False
led_color = (255, 0, 0) #Used to keep track of color so it can be changed in on_press then revert back.


def on_loaded():
    global led_color

    logging.info("Pinormi button shim: Successfully loaded.")
    led_color = OPTIONS['led_color'].split(",", 3)
    set_led(led_color)

@buttonshim.on_press(buttonshim.BUTTON_A)
def button_a_press(button, pressed):
    #Set the led purple to signify button is pressed.
    set_led((128, 0, 128))

@buttonshim.on_release(buttonshim.BUTTON_A)
def button_a_release(button, pressed):
    global button_held, led_color

    #Revert to the old color
    set_led(led_color)

    if button_held == True: #Button was held, so don't run this code.
        button_held = False
        return

    command = OPTIONS['buttons_press'][1]
    if command: #Run the command specified in config.yml
        logging.info(f"Button 1 Pressed! Running command: {command}")
        process = subprocess.Popen(command, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()
    else:
        #Default command
        logging.info(f"Button 1 Pressed! Running command: No command set.")
        pass


@buttonshim.on_hold(buttonshim.BUTTON_A, hold_time=2)
def button_a_hold(button):
    global button_held, led_color, display
    button_held = True

    command = OPTIONS['buttons_hold'][1]
    if command: #Run the command specified in config.yml
        logging.info(f"Button 1 Held! Running command: {command}")
        process = subprocess.Popen(command, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()
    else: #Default command
        logging.info(f"Button 1 Held! Running command: No command set.")
        pass


@buttonshim.on_press(buttonshim.BUTTON_B)
def button_b_press(button, pressed):
    #Set the led purple to signify button is pressed.
    set_led((128, 0, 128))

@buttonshim.on_release(buttonshim.BUTTON_B)
def button_b_release(button, pressed):
    global button_held, led_color

    #Revert to the old color
    set_led(led_color)

    if button_held == True: #Button was held, so don't run this code.
        button_held = False
        return

    command = OPTIONS['buttons_press'][2]
    if command: #Run the command specified in config.yml
        logging.info(f"Button 2 Pressed! Running command: {command}")
        process = subprocess.Popen(command, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()
    else:
        #Default command
        logging.info(f"Button 2 Pressed! Running command: No command set.")
        pass


@buttonshim.on_hold(buttonshim.BUTTON_B, hold_time=2)
def button_b_hold(button):
    global button_held, led_color, display
    button_held = True

    command = OPTIONS['buttons_hold'][2]
    if command: #Run the command specified in config.yml
        logging.info(f"Button 2 Held! Running command: {command}")
        process = subprocess.Popen(command, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()
    else: #Default command
        logging.info(f"Button 2 Held! Running command: No command set.")
        pass

@buttonshim.on_press(buttonshim.BUTTON_C)
def button_c_press(button, pressed):
    #Set the led purple to signify button is pressed.
    set_led((128, 0, 128))

@buttonshim.on_release(buttonshim.BUTTON_C)
def button_c_release(button, pressed):
    global button_held, led_color

    #Revert to the old color
    set_led(led_color)

    if button_held == True: #Button was held, so don't run this code.
        button_held = False
        return

    command = OPTIONS['buttons_press'][3]
    if command: #Run the command specified in config.yml
        logging.info(f"Button 3 Pressed! Running command: {command}")
        process = subprocess.Popen(command, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()
    else:
        #Default command
        logging.info(f"Button 3 Pressed! Running command: No command set.")
        pass


@buttonshim.on_hold(buttonshim.BUTTON_C, hold_time=2)
def button_c_hold(button):
    global button_held, led_color, display
    button_held = True

    command = OPTIONS['buttons_hold'][3]
    if command: #Run the command specified in config.yml
        logging.info(f"Button 3 Held! Running command: {command}")
        process = subprocess.Popen(command, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()
    else: #Default command
        logging.info(f"Button 3 Held! Running command: No command set.")
        pass

@buttonshim.on_press(buttonshim.BUTTON_D)
def button_d_press(button, pressed):
    #Set the led purple to signify button is pressed.
    set_led((128, 0, 128))

@buttonshim.on_release(buttonshim.BUTTON_D)
def button_d_release(button, pressed):
    global button_held, led_color

    #Revert to the old color
    set_led(led_color)

    if button_held == True: #Button was held, so don't run this code.
        button_held = False
        return

    command = OPTIONS['buttons_press'][4]
    if command: #Run the command specified in config.yml
        logging.info(f"Button 4 Pressed! Running command: {command}")
        process = subprocess.Popen(command, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()
    else:
        #Default command
        logging.info(f"Button 4 Pressed! Running command: No command set.")
        pass


@buttonshim.on_hold(buttonshim.BUTTON_D, hold_time=2)
def button_d_hold(button):
    global button_held, led_color, display
    button_held = True

    command = OPTIONS['buttons_hold'][4]
    if command: #Run the command specified in config.yml
        logging.info(f"Button 4 Held! Running command: {command}")
        process = subprocess.Popen(command, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()
    else: #Default command
        logging.info(f"Button 4 Held! Running command: No command set.")
        pass

@buttonshim.on_press(buttonshim.BUTTON_E)
def button_e_press(button, pressed):
    #Set the led purple to signify button is pressed.
    set_led((128, 0, 128))

@buttonshim.on_release(buttonshim.BUTTON_E)
def button_e_release(button, pressed):
    global button_held, led_color

    #Revert to the old color
    set_led(led_color)

    if button_held == True: #Button was held, so don't run this code.
        button_held = False
        return

    command = OPTIONS['buttons_press'][5]
    if command: #Run the command specified in config.yml
        logging.info(f"Button 5 Pressed! Running command: {command}")
        process = subprocess.Popen(command, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()
    else:
        #Default command
        logging.info(f"Button 5 Pressed! Running command: No command set.")
        pass


@buttonshim.on_hold(buttonshim.BUTTON_E, hold_time=2)
def button_e_hold(button):
    global button_held, led_color, display
    button_held = True

    command = OPTIONS['buttons_hold'][5]
    if command: #Run the command specified in config.yml
        logging.info(f"Button 5 Held! Running command: {command}")
        process = subprocess.Popen(command, shell=True, stdin=None, stdout=open("/dev/null", "w"), stderr=None, executable="/bin/bash")
        process.wait()
    else: #Default command
        logging.info(f"Button 5 Held! Running command: No command set.")
        pass

def set_led(led_color):
    '''
    Used for setting the LED color
    Accepts a tuple of an RGB color value and breaks it out
    to the invididual values needed by pinormi library
    '''

    buttonshim.set_pixel(int(led_color[0]), int(led_color[1]), int(led_color[2]))

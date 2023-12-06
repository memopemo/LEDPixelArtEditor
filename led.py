#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

import time
import os
import copy
from rpi_ws281x import *
import argparse
import RPi.GPIO as GPIO

# LED strip configuration:
LED_COUNT      = 256     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 64    # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

array = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
clipboard = []
frames = []
frames.append(array)
current_frame = 0
play_mode = False
ticks = 0
ticks_per_frame = 50
command_activated = False
held_pen = 0
colorMode = 0
colorSel = 5
colorPallete = [
    [(0, 99, 202), (228, 9, 9 ), (255, 211, 0)],
    [(93, 75, 229), (255, 55, 159), (251, 174, 254)],
    [(2, 151, 50), (255, 54, 8), (255, 222, 6)],
    [(0, 179, 157), (255, 112, 1), (252, 221, 113)],
    [(85, 57, 220), (226, 38, 167), (34, 236, 1)],
    [(106, 1, 153), (255, 13, 0), (254, 185, 2)],
    [(0, 127, 253), (2, 206, 55), (255, 231, 29)],
    [(2, 165, 255), (254, 67, 232), (230, 255, 3)],
]

def colorWipe(strip, color, wait_ms=0):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        time.sleep(wait_ms/1000.0)
    strip.show()

def display(strip):
    global current_frame
    global frames
    for y in range(16):
        for x in range(16):
            offset = y*16 + (15-x) if y % 2 == 0  else y*16 + x #magic
            # decide pen color or normal color?
            if(cursor[0] == x and cursor[1] == y and not play_mode):
                strip.setPixelColor(offset, is_lit_pen(frames[current_frame][y][x]))
            else:
                strip.setPixelColor(offset, is_lit(frames[current_frame][y][x],offset+i))
# light pen depending on if the pen is on a 1 or 0 in the display.
def is_lit_pen(i):
    return Color(128,128,128) if i > 0 else Color(25,25,25)

# light (with a rainbow color) depending on if there is a 1 or 0 in the display.
def is_lit(i,offset):
    return wheel(offset) if i > 0 else Color(0,0,0)

# generate rainbow colors depending on pixel position
def wheel(pos):
    pos %= 255 #255 max
    if(colorMode == 0): #rainbow
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)
    elif(colorMode == 1):
        if pos < 85:
            return Color(colorPallete[colorSel][0][0],colorPallete[colorSel][0][1],colorPallete[colorSel][0][2])
        elif pos < 170:
            return Color(colorPallete[colorSel][1][0],colorPallete[colorSel][1][1],colorPallete[colorSel][1][2])
        else:
            return Color(colorPallete[colorSel][2][0],colorPallete[colorSel][2][1],colorPallete[colorSel][2][2])
    else:
        return Color(255,255,255)

def save():
    with open(args.filename, "wb") as binary_file:
        for i in frames:
            for y in range(16):
                byte = 0; 
                for x in range(16):
                    byte <<= 1              #shift left by 1 for next integer
                    byte |= i[y][x]         #xxxxx0 bitwise OR with
                                            #00000x (pixel data) 
                binary_file.write(byte.to_bytes(2, 'big'))
    print("Finished Saving to file: " + args.filename)
## todo: fix
def load_file():
    if not os.path.exists(args.filename):
        with open(args.filename, 'wb') as temp:
            temp.write(b'\x00' * 32)

    file_size_bytes = os.path.getsize(args.filename)

    if(file_size_bytes % 32 != 0):
        print("File structure is not valid.")
        exit(1)
    
    with open(args.filename, 'rb') as binary_file:
        bytes_remaining = file_size_bytes
        print(file_size_bytes // 32)
        for i in range(file_size_bytes // 32):
            for y in range(16):

                # get left half of array
                byte_left = binary_file.read(1)
                left_array = [byte_left[0] >> j & 0x1 for j in range(8)]

                #get right half of array
                byte_right = binary_file.read(1)
                right_array = [byte_right[0] >> j & 0x1 for j in range(8)]
                
                
                # arrays are reversed after doing that so we have to unreverse them (i give up)
                array = right_array + left_array
                array.reverse()
                     
                frames[i][y] = array

                bytes_remaining -= 2

            if(i != (file_size_bytes//32) - 1):
                frames.append(copy.deepcopy(frames[i]))
    print("Loaded " + args.filename)
    print(frames)


# Main program logic follows:

# Process arguments
parser = argparse.ArgumentParser(description= "Play ")
parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
parser.add_argument('filename')
args = parser.parse_args()


# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()

print ('Press Ctrl-C to quit.')
if not args.clear:
    print('Use "-c" argument to clear LEDs on exit')


load_file()

# button pins
u_pin = 23
d_pin = 17
l_pin = 27
r_pin = 22
p_pin = 24
n_pin = 5
v_pin = 6
a_pin = 26

# index for rainbow color (global)
i = 0

is_pressed_right = False
is_pressed_left = False
is_pressed_up = False
is_pressed_down = False
is_pressed_pen = False
is_pressed_next = False
is_pressed_prev = False
is_pressed_play = False

#setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(u_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(d_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(l_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(r_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(p_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(n_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(v_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(a_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# setup editor variables
cursor = [0,0]
input_requested = False

def handle_down(ev=None):
    global current_frame
    global frames
    global command_activated

    #ignore on play mode
    if(play_mode):
        global colorSel
        colorSel = 0 if GPIO.input(p_pin) != 0 else 4
        global colorMode
        colorMode = 1 
        return
    
    # check if paste (Play + Down)
    if(GPIO.input(a_pin) == 0):
        global clipboard
        if(len(clipboard) == 16): #clipboard is full
            frames[current_frame] = copy.deepcopy(clipboard)
            print("Pasted over Frame " + str(current_frame))
        command_activated = True
        return
    
    # move cursor down
    cursor[1] += 1
    loop_cursor()
    if(GPIO.input(p_pin) == 0):
        pen_eraser()
    
def handle_up(ev=None):
    global current_frame
    global frames
    global command_activated

    # ignore on play mode (add pallete options later)
    if(play_mode):
        global colorSel
        colorSel = 1 if GPIO.input(p_pin) != 0 else 5
        global colorMode
        colorMode = 1 
        return
    
    # check if copy (Play + Up)
    if(GPIO.input(a_pin) == 0):
        global clipboard
        clipboard = copy.deepcopy(frames[current_frame])
        print("Copied Frame " + str(current_frame))
        command_activated = True
        return
    
    # move cursor up
    cursor[1] -= 1
    loop_cursor()
    if(GPIO.input(p_pin) == 0):
        pen_eraser()
    
def handle_left(ev=None):
    global current_frame
    global command_activated
    
    #ingore if in play mode
    if(play_mode):
        global colorSel
        colorSel = 2 if GPIO.input(p_pin) != 0 else 6
        global colorMode
        colorMode = 1 
        return
    
    #check if go to first frame (Play + Left)
    if(GPIO.input(a_pin) == 0):
        current_frame = 0
        print("Frame: 0")
        command_activated = True
    
    # move cursor left
    cursor[0] -= 1
    loop_cursor()
    if(GPIO.input(p_pin) == 0):
        pen_eraser()
    
def handle_right(ev=None):
    global current_frame
    global command_activated
    
    #ignore if in play mode
    if(play_mode):
        global colorSel
        colorSel = 3 if GPIO.input(p_pin) != 0 else 7
        global colorMode
        colorMode = 1 
        return
    
    #check if go to first frame (Play + Left)
    if(GPIO.input(a_pin) == 0):
        current_frame = len(frames)-1
        print("Frame: ", current_frame+1)
        command_activated = True

    #move cursor right
    cursor[0] += 1
    loop_cursor()
    if(GPIO.input(p_pin) == 0):
        pen_eraser()

def handle_next_frame(ev=None):
    global current_frame
    global frames
    global command_activated

    # speed up if in play mode
    if(play_mode):
        global ticks_per_frame
        ticks_per_frame -= 5
        if(ticks_per_frame < 5):
            ticks_per_frame = 5
        print("Speed: " + str(20-(ticks_per_frame//5)+1))
        return
    
    # check if duplicate current frame (Play + Next)
    if(GPIO.input(a_pin) == 0):
        frames.append(copy.deepcopy(frames[current_frame]))
        print("Created New Frame")
        command_activated = True
        
    
    current_frame += 1
    current_frame %= len(frames)
    print("Current Frame: ", current_frame+1)

def handle_previous_frame(ev=None):
    global current_frame
    global frames
    global command_activated

    # slow down if in play mode
    if(play_mode):
        global ticks_per_frame
        ticks_per_frame += 5
        if(ticks_per_frame > 100):
            ticks_per_frame = 100
        print("Speed: " + str(20-(ticks_per_frame//5)+1))
        return
    
    #check if delete current frame (Play + Previous)
    if(GPIO.input(a_pin) == 0):
        if(len(frames) <= 1):
            print("This is our only frame!!! ;0ᗝ0")
            command_activated = True
            return
        if(current_frame == len(frames)-1):
            print("Deleting the last frame just breaks the display code and I have NO IDEA WHY Q-Q")
            command_activated = True
            return
        frames.pop(current_frame)
        print("Deleted Current Frame")    
        command_activated = True

    current_frame -= 1
    current_frame %= len(frames)
    print("Current Frame: ", current_frame+1)

def handle_pen_eraser(ev=None):
    global command_activated
    global current_frame
    global held_pen
    
    if(play_mode):
        global colorMode
        colorMode += 1
        colorMode %= 3
        return
    if(GPIO.input(a_pin) == 0):
        save()
        command_activated = True
        return
    held_pen = 1 - frames[current_frame][cursor[1]][cursor[0]]
    pen_eraser()


def handle_play(ev=None):
    global play_mode
    global input_requested
    global command_activated
    global held_pen
    
    if(command_activated):
        command_activated = False
        return
    
    if(play_mode):
        play_mode = False
        print("Play Mode Disabled")
    else:
        play_mode = True
        print("Play Mode Enabled")

# toggles pixel
def pen_eraser():
    global current_frame
    if(play_mode):
        return
    print(held_pen)
    frames[current_frame][cursor[1]][cursor[0]] = held_pen
    
def loop_cursor():
    cursor[0] %= 16
    cursor[1] %= 16

def play_mode_update():
    global ticks
    global ticks_per_frame
    global current_frame
    ticks += 1
    ticks %= ticks_per_frame
    if(ticks == 0):
        if(len(frames) > 1):
            current_frame += 1
            current_frame %= len(frames)




# we use the input requested bool to not call this function again until a button has been pushed.
def GetInput():
    GPIO.add_event_detect(d_pin, GPIO.FALLING, callback=handle_down, bouncetime=200)
    GPIO.add_event_detect(u_pin, GPIO.FALLING, callback=handle_up, bouncetime=200)
    GPIO.add_event_detect(l_pin, GPIO.FALLING, callback=handle_left, bouncetime=200)
    GPIO.add_event_detect(r_pin, GPIO.FALLING, callback=handle_right, bouncetime=200)
    GPIO.add_event_detect(p_pin, GPIO.FALLING, callback=handle_pen_eraser, bouncetime=200)
    GPIO.add_event_detect(n_pin, GPIO.FALLING, callback=handle_next_frame, bouncetime=200)
    GPIO.add_event_detect(v_pin, GPIO.FALLING, callback=handle_previous_frame, bouncetime=200)
    GPIO.add_event_detect(a_pin, GPIO.RISING, callback=handle_play, bouncetime=200)
    global input_requested
    input_requested = True

try:
    input_requested = False
    current_frame = 0
    while True:
        if play_mode == True:
            play_mode_update()
        if input_requested == False:
            GetInput()
        display(strip)
        strip.show()
        i += 1
        i %= 255

        

except KeyboardInterrupt:
    if args.clear:
        colorWipe(strip, Color(0,0,0), 0)

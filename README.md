# LEDPixelArtEditor
Code for an LED Matrix and buttons for drawing animated pixel art.

## Features
- Pixelart Drawing
- Creating and Deleting Frames
- Copy / Pasting Between Frames
- Playing the Resulting Animation
- 10 Different Color Modes
- Speeding Up and Slowing Down Animation
- Saving / Loading Animations
- Limitless Animation Size Using a Small, Byte-wise File Structure

## Hardware
- LED Matrix (WS2812B) https://a.co/d/1zSOD06
- Raspberry Pi 4 Model B https://a.co/d/h651MbH
- Sunfounder Kit (Breadboard, Buttons, and Wires) https://a.co/d/3v5l4Hg
   - NOTE: THE SUNFOUNDER KIT ONLY COMES WITH 5 BUTTONS. YOU NEED TO PURCHASE 3 MORE. 

## Libraries
```
sudo pip3 install rpi_ws281x
sudo pip3 install adafruit-circuitpython-neopixel
sudo python3 -m pip install --force-reinstall adafruit-blinka
```

## Pin Layout

### LED

Name | Pin #
---|---
Data | 18
5V | Any 5V Pin
GND | Any Ground Pin

### Buttons

Button | Pin #
---|---
Up | 23
Down | 17
Left | 27
Right | 22
Pen | 24
Next | 5
Previous | 6
Play | 26

## Using The Program
1. Run ``` sudo python3  led.py -c [filename]``` where [filename] is the file you want to create/load.
    a. If the file does not exist, it will create a new one. 
2. Move the directional buttons to move the cursor.
3. Press the pen button to draw
    a. You can hold the button down to draw faster.
4. Press the Play button to enter Play Mode and display.
5. Press the Next and Previous frames to switch frames.

### Editing Command Combinations
Button + | Button = | Command
---|---|---
Play + | Next Frame = | Add New Current Frame
Play + | Previous Frame = | Delete Current Frame
Play + | Up = | Copy Frame
Play + | Down = | Paste and Overwrite Frame
Play + | Left = | Go to First Frame
Play + | Right = | Go to Last Frame
Play + | Pen = | Save Animation to File.

### Play Mode Commands
- Directional Buttons : Change to Pallete 1-4
- Pen + Directional Buttons: Change to Pallete 5-8
- Pen : Switch between 3 Different Color Modes: Rainbow, Pallete, and All White.
- Previous Frame : Slow Down Animation
- Next Frame : Speed Up Animation
- Play : Exit Play Mode.


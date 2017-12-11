# -*- coding: utf-8 -*-

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import Adafruit_ILI9341 as TFT
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

def draw_rotated_text(image, text, position, angle, font, fill=(255,255,255)):
    # Get rendered font width and height.
    draw = ImageDraw.Draw(image)
    width, height = draw.textsize(text, font=font)
    # Create a new image with transparent background to store the text.
    textimage = Image.new('RGBA', (width, height), (0,0,0,0))
    # Render the text.
    textdraw = ImageDraw.Draw(textimage)
    textdraw.text((0,0), text, font=font, fill=fill)
    # Rotate the text image.
    rotated = textimage.rotate(angle, expand=1)
    # Paste the text into the image, using it as a mask for transparency.
    image.paste(rotated, position, rotated)

def convert_sec_to_time(seconds):

    if seconds is None:
        seconds = 0
    result = ''
    if seconds > 3600:
        h = seconds / 3600
        m = (seconds % 3600) / 60
        s  = seconds % 60
        result += '%d:%02d:%02d' % (h,m,s)
    else :
        m = (seconds % 3600) / 60
        s  = seconds % 60
        result += '%d:%02d' % (m,s)

    return result

MaxCharsPerLine = 18
progress_bar_max_size = 20
TURQ = (84, 198, 136)
DARK_RED = (215,90,74)
ORANGE =(229,170,23)
DARK_TURQ = (0,51,51)
BLACK = (255,255,255)

# Raspberry Pi configuration.
DC = 18
RST = 23
SPI_PORT = 0
SPI_DEVICE = 0

PIC_SIZE = 70
# Create TFT LCD display class.
disp = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))

# Initialize display.
disp.begin()

#clear screen
disp.clear((0, 0, 0))

playImage = Image.open('/data/plugins/user_interface/web_configuration/python_project/lcd/play.png')
playImage = playImage.resize((PIC_SIZE, PIC_SIZE)).rotate(270)
pauseImage = Image.open('/data/plugins/user_interface/web_configuration/python_project/lcd/pause.png')
pauseImage = pauseImage.resize((PIC_SIZE, PIC_SIZE)).rotate(270)
stopImage = Image.open('/data/plugins/user_interface/web_configuration/python_project/lcd/stop.png')
stopImage = stopImage.resize((PIC_SIZE, PIC_SIZE)).rotate(270)
font = ImageFont.truetype("/data/plugins/user_interface/web_configuration/python_project/lcd/DejaVuSans.ttf",30)
bar = Image.new('RGBA', (30, 310), DARK_TURQ)
clear = Image.new('RGBA', (240, 320), (0,0,0,255))

LED_GPIO = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_GPIO, GPIO.OUT)
GPIO.output(LED_GPIO, False)

def turn_on_led():
    GPIO.output(LED_GPIO, False)

def turn_off_led():
    GPIO.output(LED_GPIO, True)

def displayData(data,offset_title,offset_artist,offset_album):

    try:
        # Clears text area
        disp.buffer.paste(clear,(0,0))

        title = data['title'][offset_title : MaxCharsPerLine + 1 + offset_title]
        artist = data['artist'][offset_artist : MaxCharsPerLine + 1 + offset_artist]
        album = data['album'][offset_album : MaxCharsPerLine + 1 + offset_album]

        draw_rotated_text(disp.buffer, title , (200, 10), 270, font, fill=TURQ )
        draw_rotated_text(disp.buffer, artist, (160, 10), 270, font, fill=TURQ )
        draw_rotated_text(disp.buffer, album, (120, 10), 270, font, fill=TURQ )

        try:
            volume = data['volume']
        except KeyError:
            volume = 0

        try:
            mute = data['mute']
        except KeyError:
            mute = False

        if mute:
            mute_sign = u'\u2718'
        else:
            mute_sign = u'\u266b'

        draw_rotated_text(disp.buffer, "Volume:"+ str(volume) + mute_sign , (85, 110), 270, font, fill=TURQ )

        try:
            seek_sec = data['seek']/1000
        except KeyError:
            seek_sec = 0

        try:
            duration_sec = data['duration']
        except KeyError:
            duration_sec = 0

        if duration_sec == 0:
            progress = 0
            time_to_print = ""
        else:
            if seek_sec>duration_sec:
                seek_sec = duration_sec
            time_to_print =  convert_sec_to_time(seek_sec) + '/'+ convert_sec_to_time(duration_sec)
            progress = float(seek_sec)/duration_sec

        draw_rotated_text(disp.buffer,  time_to_print, (45, 110), 270, font, fill=TURQ )

        disp.buffer.paste(bar,(5,5))

        progress_bar = Image.new('RGBA', (30, int(310*progress)), TURQ)
        disp.buffer.paste(progress_bar,(5,5))

        if data['status'] == 'play':
            disp.buffer.paste(playImage,(40,15))
            progress_bar = Image.new('RGBA', (30, int(310*progress)), TURQ)
        elif data['status'] == 'pause':
            disp.buffer.paste(pauseImage,(40,15))
            progress_bar = Image.new('RGBA', (30, int(310*progress)), ORANGE)
        elif data['status'] == 'stop':
            disp.buffer.paste(stopImage,(40,15))
            progress_bar = Image.new('RGBA', (30, int(310*progress)), DARK_RED)

        disp.buffer.paste(progress_bar,(5,5))
        disp.display()
    except Exception as e:
        print "Error during display",e

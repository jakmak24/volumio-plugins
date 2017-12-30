# -*- coding: utf-8 -*-
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import Adafruit_ILI9341 as TFT
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

DC = 24
RST = 25
SPI_PORT = 0
SPI_DEVICE = 0
LED_GPIO = 4

TURQ = (84, 198, 136)
DARK_RED = (225,40,40)
ORANGE =(229,170,23)
DARK_TURQ = (0,51,51)
BLACK = (255,255,255)

MAX_CHARS_PER_LINE = 18
PIC_SIZE = 70

playImage = Image.open('/data/plugins/user_interface/web_configuration/python_project/lcd/play.png').resize((PIC_SIZE, PIC_SIZE)).rotate(270)
pauseImage = Image.open('/data/plugins/user_interface/web_configuration/python_project/lcd/pause.png').resize((PIC_SIZE, PIC_SIZE)).rotate(270)
stopImage = Image.open('/data/plugins/user_interface/web_configuration/python_project/lcd/stop.png').resize((PIC_SIZE, PIC_SIZE)).rotate(270)
font = ImageFont.truetype("/data/plugins/user_interface/web_configuration/python_project/lcd/DejaVuSans.ttf",30)
bar = Image.new('RGBA', (30, 310), DARK_TURQ)

class TFT_Displayer():

    def __init__(self):
        self.disp = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
        self.disp._spi.set_clock_hz(12000000)
        self.disp.begin()
        self.disp.clear((0, 0, 0))
        self.led_state = True

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED_GPIO, GPIO.OUT)
        GPIO.output(LED_GPIO, False)

    def _draw_rotated_text(self,image, text, position, angle, font, fill=(255,255,255)):

        draw = ImageDraw.Draw(image)
        width, height = draw.textsize(text, font=font)
        textimage = Image.new('RGBA', (width, height), (0,0,0,0))
        textdraw = ImageDraw.Draw(textimage)
        textdraw.text((0,0), text, font=font, fill=fill)
        rotated = textimage.rotate(angle, expand=1)
        image.paste(rotated, position, rotated)

    def _convert_sec_to_time(self,seconds):

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

    def turn_on_led(self):
        GPIO.output(LED_GPIO, False)
        self.led_state=True

    def turn_off_led(self):
        GPIO.output(LED_GPIO, True)
        self.led_state=False

    def toggle_led(self):
        if self.led_state == True:
            self.turn_off_led()
        else:
            self.turn_on_led()

    def displayData(self,data,offset_title,offset_artist,offset_album):

        try:
            self.disp.clear((0, 0, 0))

            title_to_display = data['title'][offset_title : MAX_CHARS_PER_LINE + 1 + offset_title]
            artist_to_display = data['artist'][offset_artist : MAX_CHARS_PER_LINE + 1 + offset_artist]
            album_to_display = data['album'][offset_album : MAX_CHARS_PER_LINE + 1 + offset_album]

            self._draw_rotated_text(self.disp.buffer, title_to_display , (200, 10), 270, font, fill=TURQ )
            self._draw_rotated_text(self.disp.buffer, artist_to_display, (160, 10), 270, font, fill=TURQ )
            self._draw_rotated_text(self.disp.buffer, album_to_display, (120, 10), 270, font, fill=TURQ )

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

            self._draw_rotated_text(self.disp.buffer, "Volume:"+ str(volume) + mute_sign , (85, 110), 270, font, fill=TURQ )

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
                time_to_print =  self._convert_sec_to_time(seek_sec) + '/'+ self._convert_sec_to_time(duration_sec)
                progress = float(seek_sec)/duration_sec

            self._draw_rotated_text(self.disp.buffer,  time_to_print, (45, 110), 270, font, fill=TURQ )

            self.disp.buffer.paste(bar,(5,5))

            progress_bar = Image.new('RGBA', (30, int(310*progress)), TURQ)
            self.disp.buffer.paste(progress_bar,(5,5))

            if data['status'] == 'play':
                self.disp.buffer.paste(playImage,(40,15))
                progress_bar = Image.new('RGBA', (30, int(310*progress)), TURQ)
            elif data['status'] == 'pause':
                self.disp.buffer.paste(pauseImage,(40,15))
                progress_bar = Image.new('RGBA', (30, int(310*progress)), ORANGE)
            elif data['status'] == 'stop':
                self.disp.buffer.paste(stopImage,(40,15))
                progress_bar = Image.new('RGBA', (30, int(310*progress)), DARK_RED)

            self.disp.buffer.paste(progress_bar,(5,5))
            self.disp.display()
        except Exception as e:
            print "Error during display",e

        def __destroy__(self):
            self.turn_off_led()
            GPIO.cleanup()

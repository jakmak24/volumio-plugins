import RPi.GPIO as GPIO
from socketIO_client import SocketIO, LoggingNamespace
import subprocess

DEBOUNCE = 500
buttons_gpio = {"PLAY":12,"NEXT":25,"PREV":16,"SEEK_UP":21,"SEEK_DOWN":20,"SHUTDOWN":3}

class Buttons:

    def __init__(self,command_router):
        self.command_router = command_router
        GPIO.setmode(GPIO.BCM)
        for key, value in buttons_gpio.iteritems():
            GPIO.setup(value, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        self.enable_gpio()

    def play_pause(self,channel):
        print("Button pressed!" + str(channel))
        self.command_router.toggle_play_pause()

    def next(self,channel):
        print("Button pressed!" + str(channel))
        self.command_router.next()

    def prev(self,channel):
        print("Button pressed!" + str(channel))
        self.command_router.prev()

    def vol_up(self,channel):
        print("Button pressed!" + str(channel))
        self.command_router.vol_up()

    def vol_down(self,channel):
        print("Button pressed!" + str(channel))
        self.command_router.vol_down()

    def seek_up(self,channel):
        print("Button pressed!" + str(channel))
        self.command_router.seek(5)

    def seek_down(self,channel):
        print("Button pressed!" + str(channel))
        self.command_router.seek(-5)

    def shutdown(self,channel):
        subprocess.call("sudo shutdown -t now",shell = True)

    def enable_gpio(self):
        GPIO.add_event_detect(buttons_gpio["PLAY"], GPIO.RISING, callback= self.play_pause, bouncetime=DEBOUNCE)
        GPIO.add_event_detect(buttons_gpio["NEXT"], GPIO.RISING, callback=self.next, bouncetime=DEBOUNCE)
        GPIO.add_event_detect(buttons_gpio["PREV"], GPIO.RISING, callback=self.prev, bouncetime=DEBOUNCE)
        GPIO.add_event_detect(buttons_gpio["SEEK_UP"], GPIO.RISING, callback=self.seek_up, bouncetime=DEBOUNCE)
        GPIO.add_event_detect(buttons_gpio["SEEK_DOWN"], GPIO.RISING, callback=self.seek_down, bouncetime=DEBOUNCE)
        GPIO.add_event_detect(buttons_gpio["SHUTDOWN"], GPIO.RISING, callback=self.shutdown, bouncetime=DEBOUNCE)

    def __destroy__(self):
        GPIO.cleanup()

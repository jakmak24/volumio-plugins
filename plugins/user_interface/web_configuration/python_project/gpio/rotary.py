#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

RotateAPin = 16 # Define as CLK Pin
RotateBPin = 12 # Define as DT Pin
MuteButton = 21 # Define as Push Button Pin

class Decoder:

    def __init__(self, gpioA, gpioB, callback):

        self._gpioA = gpioA
        self._gpioB = gpioB
        self._callback = callback

        self._levA = 0
        self._levB = 0

        self._lastGpio = None
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(gpioA, GPIO.IN,pull_up_down = GPIO.PUD_UP)
        GPIO.setup(gpioB, GPIO.IN,pull_up_down = GPIO.PUD_UP)

        GPIO.add_event_detect(gpioA, GPIO.BOTH, self._pulse)
        GPIO.add_event_detect(gpioB, GPIO.BOTH, self._pulse)

    def _pulse(self, gpio):

        level = GPIO.input(gpio)
        if gpio == self._gpioA:
            self._levA = level
        else:
            self._levB = level;

        if gpio != self._lastGpio: # debounce
            self._lastGpio = gpio

            if   gpio == self._gpioA and level == 1:
                if self._levB == 1:
                    print("+")
                    self._callback(1)
            elif gpio == self._gpioB and level == 1:
                if self._levA == 1:
                    print("-")
                    self._callback(-1)


class Rotary:
    def __init__(self,command_router):
        self.command_router = command_router
        self._counter = 0
        GPIO.setmode(GPIO.BCM) # Set GPIO pin as numbered
        GPIO.setup(RotateAPin, GPIO.IN,pull_up_down = GPIO.PUD_UP) # Set to input mode
        GPIO.setup(RotateBPin, GPIO.IN,pull_up_down = GPIO.PUD_UP) # Set to input mode
        GPIO.setup(MuteButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(MuteButton, GPIO.FALLING, callback=self._toggle_mute, bouncetime=300)
        Decoder(RotateBPin,RotateAPin,self._callbackVolume)


    def _toggle_mute(self,channel):
        status = self.command_router.data["mute"]
        if status == False:
            self.command_router.mute()
        else:
            self.command_router.unmute()

    def _callbackVolume(self,volumeStep):
        self._counter += volumeStep

    def loop(self):

        while True :

            if self._counter != 0:
                try:
                    volume = int(self.command_router.data["volume"])
                except:
                    volume = 0
                volume += self._counter * abs(self._counter)
                if volume < 0:                  # limit volume to 0...100
                    volume = 0
                if volume > 100:               # limit volume to 0...100
                    volume = 100
                print volume, self._counter
                self.command_router.set_vol(volume)
                self.command_router.data["volume"]=volume

                # if self.counter > 0:
                #     self.command_router.vol_up()
                # else:
                #     self.command_router.vol_down()
            self._counter = 0
            time.sleep(0.3)


    def __destroy__(self):
        GPIO.cleanup() # Release resource

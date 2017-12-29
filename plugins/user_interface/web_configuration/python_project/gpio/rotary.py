#!/usr/bin/env python
import RPi.GPIO as GPIO
import time

RotateAPin = 16 # Define as CLK Pin
RotateBPin = 12 # Define as DT Pin
SwitchPin = 21 # Define as Push Button Pin

class decoder:

    def __init__(self, gpioA, gpioB, callback):

        self.gpioA = gpioA
        self.gpioB = gpioB
        self.callback = callback

        self.levA = 0
        self.levB = 0

        self.lastGpio = None
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(gpioA, GPIO.IN,pull_up_down = GPIO.PUD_UP)
        GPIO.setup(gpioB, GPIO.IN,pull_up_down = GPIO.PUD_UP)

        self.cbA = GPIO.add_event_detect(gpioA, GPIO.BOTH, self._pulse)
        self.cbB = GPIO.add_event_detect(gpioB, GPIO.BOTH, self._pulse)

    def _pulse(self, gpio):

        level = GPIO.input(gpio)
        if gpio == self.gpioA:
            self.levA = level
        else:
            self.levB = level;

        if gpio != self.lastGpio: # debounce
            self.lastGpio = gpio

            if   gpio == self.gpioA and level == 1:
                if self.levB == 1:
                    print("+")
                    self.callback(1)
            elif gpio == self.gpioB and level == 1:
                if self.levA == 1:
                    print("-")
                    self.callback(-1)

    def cancel(self):
        self.cbA.cancel()
        self.cbB.cancel()


class Rotary:
    def __init__(self,command_router):
        self.command_router = command_router
        self.counter = 0
        GPIO.setmode(GPIO.BCM) # Set GPIO pin as numbered
        GPIO.setup(RotateAPin, GPIO.IN,pull_up_down = GPIO.PUD_UP) # Set to input mode
        GPIO.setup(RotateBPin, GPIO.IN,pull_up_down = GPIO.PUD_UP) # Set to input mode
        GPIO.setup(SwitchPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


    def mute(self,channel):
        status = self.command_router.data["mute"]
        if status == False:
            self.command_router.mute()
        else:
            self.command_router.unmute()

    def callbackVolume(self,volumeStep):
        self.counter += volumeStep

    def loop(self):

        GPIO.add_event_detect(SwitchPin, GPIO.FALLING, callback=self.mute, bouncetime=300)
        volume_decoder = decoder(RotateBPin,RotateAPin,self.callbackVolume)

        while True :

            if self.counter != 0:
                try:
                    volume = int(self.command_router.data["volume"])
                except:
                    volume = 0
                volume += self.counter * abs(self.counter)
                if volume < 0:                  # limit volume to 0...100
                    volume = 0
                if volume > 100:               # limit volume to 0...100
                    volume = 100
                print volume, self.counter
                self.command_router.set_vol(volume)
                self.command_router.data["volume"]=volume

                # if self.counter > 0:
                #     self.command_router.vol_up()
                # else:
                #     self.command_router.vol_down()
            self.counter = 0
            time.sleep(0.3)


    def __destroy__(self):
        GPIO.cleanup() # Release resource

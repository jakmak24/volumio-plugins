import RPi.GPIO as GPIO

DEBOUNCE = 500
buttons_gpio = {"PLAY":13,"NEXT":19,"PREV":6,"SEEK_UP":26,"SEEK_DOWN":5,"SHUTDOWN":3,"LED":20}

class Buttons:

    def __init__(self,command_router):
        self.command_router = command_router
        GPIO.setmode(GPIO.BCM)
        for key, value in buttons_gpio.iteritems():
            GPIO.setup(value, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        self._enable_gpio()

    def _toggle_play_pause(self,channel):
        print("Button pressed!" + str(channel))
        self.command_router.toggle_play_pause()

    def _next(self,channel):
        print("Button pressed!" + str(channel))
        self.command_router.next()

    def _prev(self,channel):
        print("Button pressed!" + str(channel))
        self.command_router.prev()

    def _vol_up(self,channel):
        print("Button pressed!" + str(channel))
        self.command_router.vol_up()

    def _vol_down(self,channel):
        print("Button pressed!" + str(channel))
        self.command_router.vol_down()

    def _seek_up(self,channel):
        print("Button pressed!" + str(channel))
        self.command_router.seek(5)

    def _seek_down(self,channel):
        print("Button pressed!" + str(channel))
        self.command_router.seek(-5)

    def _shutdown(self,channel):
        print("Button pressed!" + str(channel))
        self.command_router.shutdown()

    def _toggle_led(self,channel):
        print("Button pressed!" + str(channel))
        self.command_router.toggle_led()

    def _enable_gpio(self):
        GPIO.add_event_detect(buttons_gpio["PLAY"], GPIO.RISING, callback= self._toggle_play_pause, bouncetime=DEBOUNCE)
        GPIO.add_event_detect(buttons_gpio["NEXT"], GPIO.RISING, callback=self._next, bouncetime=DEBOUNCE)
        GPIO.add_event_detect(buttons_gpio["PREV"], GPIO.RISING, callback=self._prev, bouncetime=DEBOUNCE)
        GPIO.add_event_detect(buttons_gpio["SEEK_UP"], GPIO.RISING, callback=self._seek_up, bouncetime=DEBOUNCE)
        GPIO.add_event_detect(buttons_gpio["SEEK_DOWN"], GPIO.RISING, callback=self._seek_down, bouncetime=DEBOUNCE)
        GPIO.add_event_detect(buttons_gpio["SHUTDOWN"], GPIO.RISING, callback=self._shutdown, bouncetime=DEBOUNCE)
        GPIO.add_event_detect(buttons_gpio["LED"], GPIO.RISING, callback=self._toggle_led, bouncetime=DEBOUNCE)


    def __destroy__(self):
        GPIO.cleanup()

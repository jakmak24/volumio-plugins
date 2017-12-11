import subprocess
from lcd import tft_simple
import json
import time

class CommandRouter:
    def __init__(self,data,socket):
        self.data = data
        self.socket = socket
        try:
            with open('/home/volumio/komunikaty/conf.json') as json_data:
                self.alert_config = json.load(json_data)
                print(self.alert_config)
        except:
            print("Could not load alert config file")
            self.alert_config = None

    def pause(self):
        self.socket.emit("pause")

    def play(self):
        self.socket.emit("play")

    def toggle_play_pause(self):
        if self.data['status'] == 'play':
            self.pause()
        else:
            self.play()

    def stop(self):
        self.socket.emit("stop")

    def next(self):
        self.socket.emit("next")

    def prev(self):
        self.socket.emit("prev")

    def seek(self,step):
        value = self.data["seek"]/1000 + step
        if value < 0:
            value = 0
        if value> self.data["duration"]:
            value = self.data["duration"]
        self.socket.emit("seek",value)

    def vol_up(self):
        prev = time.time()
        self.socket.emit("volume",'+')
        #subprocess.Popen(["volumio", "volume","plus"])
        print(time.time()-prev)

    def vol_down(self):
        prev = time.time()
        self.socket.emit("volume",'-')
        print(time.time()-prev)

    def set_vol(self,value):
        self.socket.emit("volume",value)

    def unmute(self):
        self.socket.emit("volume","unmute")

    def mute(self):
        self.socket.emit("volume","mute")

    def night_mode(self):
        self.stop()
        tft_simple.turn_off_led()

    def normal_mode(self):
        self.play()
        tft_simple.turn_on_led()

    def play_alert(self,alert_number):
        if self.alert_config is not None:
            try:
                alert_name = self.alert_config['alerts'][ord(alert_number)]
            except:
                print("Alert not found")
                return

            try:
                with open('/data/configuration/audio_interface/alsa_controller/config.json') as alsa_config_file:
                    alsa_config = json.load(alsa_config_file)
            except:
                print("Could not load alsa config file")
                return

            wasPlaying = False
            if self.data['status'] == 'play':
                self.pause()
                wasPlaying = True

            timeout = 2
            while self.data['status'] == 'play' and timeout>0:
                time.sleep(0.2)
                timeout -= 0.2

            toCall = "mpg123 -a hw:"+alsa_config["outputdevice"]["value"]+",0 "+"/home/volumio/komunikaty/"+alert_name
            subprocess.call(toCall, shell=True)
            if wasPlaying:
                self.play()
        else:
            print("No alert config file")

import subprocess
import json
import time
import threading

class CommandRouter:
    def __init__(self,socket,displayer):
        self.data = {'title':'Unknown','artist':'Unknown','album':'Unknown','status':'stop','volume':0,'duration':0,'seek':0,'mute':False}
        self.lock = threading.Lock()
        self.socket = socket
        self.displayer = displayer
        self.nite = False
        self.playing_alert = False
        self.path_to_alerts = "/data/plugins/user_interface/web_configuration/alerts/"
        try:
            with open(self.path_to_alerts+'conf.json') as json_data:
                self.alert_config = json.load(json_data)
                print(self.alert_config)
        except:
            print("Could not load alert config file")
            self.alert_config = None

    def updateData (self,*args):

        self.lock.acquire()
        self.data = args[0]

        try:
            if self.data['title'] is None or "":
                self.data['title'] = "Unknown"
        except KeyError, e:
            print e
            self.data['title'] = "Unknown"
        try:
            if self.data['album'] is None or "":
                self.data['album'] = "Unknown"
        except KeyError, e:
            print e
            self.data['album'] = "Unknown"
        try:
            if self.data['artist'] is None or "":
                self.data['artist'] = "Unknown"
        except KeyError, e:
            print e
            self.data['artist'] = "Unknown"
        self.lock.release()


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

    def toggle_mute(self):
        if self.data['mute'] == True:
            self.unmute()
        else:
            self.mute()

    def night_mode(self):
        self.stop()
        self.turn_off_led()

    def normal_mode(self):
        self.play()
        self.turn_on_led()

    def toggle_nite(self):
        if self.nite == True:
            self.normal_mode()
            self.nite=False
        else:
            self.night_mode()
            self.nite=True

    def turn_on_led(self):
        if self.displayer is not None:
            self.displayer.turn_on_led()
            self.nite = False

    def turn_off_led(self):
        if self.displayer is not None:
            self.displayer.turn_off_led()

    def toggle_led(self):
        if self.displayer is not None:
            self.displayer.toggle_led()

    def shutdown(self):
        subprocess.call("sudo shutdown -t now",shell = True)

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

            while self.playing_alert:
                time.sleep(0.2)
            self.playing_alert = True

            wasPlaying = False
            if self.data['status'] == 'play':
                wasPlaying = True
                self.pause()

            timeout = 2
            while self.data['status'] == 'play' and timeout>0:
                time.sleep(0.2)
                timeout -= 0.2

            if self.data['status'] == 'play':
                print("Couldnt pause playlist")
                return

            hw = "hw:"+alsa_config["outputdevice"]["value"]+",0"
            if alsa_config["outputdevice"]["value"] == "softvolume":
                hw = "softvolume"
            toCall = "mpg123 -a "+hw+" "+ self.path_to_alerts + alert_name
            subprocess.call(toCall, shell=True)

            if wasPlaying:
                self.play()
                timeout = 2
                while self.data['status'] != 'play' and timeout>0:
                    time.sleep(0.2)
                    timeout -= 0.2

            self.playing_alert = False
        else:
            print("No alert config file")

from lcd import tft_simple as tft
import time

class ScreenUpdater():
    def __init__(self,command_router):
        self.command_router = command_router
        self.lastUpdate = 0
        self.offset_title =0
        self.offset_artist = 0
        self.offset_album = 0
        self.pause = 0
        offset_state = 0

    def reset_offset(self):
        self.lastUpdate = int(time.time())
        self.offset_title =0
        self.offset_artist = 0
        self.offset_album = 0
        self.pause = 0
        self.offset_state = 0

    def updateScreen(self):

        last_title = None
        while (True):
            time.sleep(0.2)
            if last_title != self.command_router.data['title']:
                self.reset_offset()
                last_title = self.command_router.data['title']
                
            if self.command_router.data['status'] == 'play':
                currentTime = int(time.time())
                if currentTime - self.lastUpdate > 0:

                    if self.offset_state == 0:
                        if self.pause <5:
                            self.pause += 1
                        else:
                            self.pause = 0
                            self.offset_state = 1
                    elif self.offset_state == 1:
                        if tft.MaxCharsPerLine + self.offset_title < len(self.command_router.data['title']):
                            self.offset_title += 1
                        else:
                            self.offset_title = 0
                            self.offset_state = 2
                    elif self.offset_state == 2:
                        if tft.MaxCharsPerLine + self.offset_artist < len(self.command_router.data['artist']):
                            self.offset_artist += 1
                        else:
                            self.offset_artist = 0
                            self.offset_state = 3
                    elif self.offset_state == 3:
                        if tft.MaxCharsPerLine + self.offset_album < len(self.command_router.data['album']):
                            self.offset_album += 1
                        else:
                            offset_state = 0
                            offset_album = 0

                    self.command_router.data['seek']  += (1000*(currentTime - self.lastUpdate))
                    self.lastUpdate = currentTime
            tft.displayData(self.command_router.data,self.offset_title,self.offset_artist,self.offset_album)

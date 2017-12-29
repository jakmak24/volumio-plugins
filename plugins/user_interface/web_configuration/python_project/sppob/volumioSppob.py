# -*- coding: utf-8 -*-
import serial
import threading
import os
import spp
import cmdid
import time
import json
import signal

VOLUMIO_PLAY = 0x01
VOLUMIO_VOL = 0x02
VOLUMIO_TITLE = 0x03
VOLUMIO_ARTIST = 0x04
VOLUMIO_ALBUM = 0x05
VOLUMIO_ALERT = 0x06

DEFAULT_ADDRESS = 0x11

class VolumioSppob:
    def __init__(self,command_router):

        self.ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        spp.init(self.ser)
        self.load_src()
        self.command_router=command_router
        self.current_position = None
        signal.signal(16,self.reload_src)

    def __destroy__(self):
        self.ser.close()

    def reload_src(self, signum, frame):
        time.sleep(3)
        self.load_src()

    def load_src(self):
        try:
            with open('/data/configuration/user_interface/web_configuration/config.json') as json_data:
                data = json.load(json_data)
                src = data['sppobAddress']['group']['value']*16 + data['sppobAddress']['device']['value']
                print("RELOAD SRC:" + format(src,'02x'))
                spp.set_src(src)
        except:
            print("Failed to load data")
            spp.set_src(DEFAULT_ADDRESS)



    def listen(self):
        while True:
            packet_buffer = spp.listen_packet()
            if packet_buffer is not None:
                if packet_buffer.payload[0] == chr(VOLUMIO_PLAY | cmdid.SPP_ID_CHAN_ON) and len(packet_buffer.payload) == 1:
                    print "Performing play"
                    self.command_router.play()
                elif packet_buffer.payload[0] == chr(VOLUMIO_PLAY | cmdid.SPP_ID_CHAN_OFF) and len(packet_buffer.payload) == 1:
                    print "Performing pause"
                    self.command_router.pause()
                elif packet_buffer.payload[0] == chr(VOLUMIO_PLAY | cmdid.SPP_ID_CHAN_OFF_ALT) and len(packet_buffer.payload) == 1:
                    print "Performing stop"
                    self.command_router.stop()
                elif packet_buffer.payload[0] == chr(VOLUMIO_PLAY | cmdid.SPP_ID_CHAN_UP) and len(packet_buffer.payload) == 1:
                    print "Performing next"
                    self.command_router.next()
                elif packet_buffer.payload[0] == chr(VOLUMIO_PLAY | cmdid.SPP_ID_CHAN_DN) and len(packet_buffer.payload) == 1:
                    print "Performing prev"
                    self.command_router.prev()
                elif packet_buffer.payload[0] == chr(VOLUMIO_VOL | cmdid.SPP_ID_CHAN_UP) and len(packet_buffer.payload) == 1:
                    print "Performing volume +"
                    self.command_router.vol_up()
                elif packet_buffer.payload[0] == chr(VOLUMIO_VOL | cmdid.SPP_ID_CHAN_DN) and len(packet_buffer.payload) == 1:
                    print "Performing volume -"
                    self.command_router.vol_down()
                elif packet_buffer.payload[0] == chr(VOLUMIO_VOL | cmdid.SPP_ID_CHAN_VALUE) and len(packet_buffer.payload) == 2:
                    print "Performing volume "+ str(ord(packet_buffer.payload[1]))
                    self.command_router.set_vol(ord(packet_buffer.payload[1]))
                elif packet_buffer.payload[0] == chr(VOLUMIO_VOL | cmdid.SPP_ID_CHAN_ON) and len(packet_buffer.payload) == 1:
                    print "Performing volume unmute"
                    self.command_router.unmute()
                elif packet_buffer.payload[0] == chr(VOLUMIO_VOL | cmdid.SPP_ID_CHAN_OFF) and len(packet_buffer.payload) == 1:
                    print "Performing volume mute"
                    self.command_router.mute()
                elif packet_buffer.payload[0] == chr(cmdid.SPP_ID_TEXT):
                    print packet_buffer.payload[1:]
                elif packet_buffer.payload[0] == chr(cmdid.SPP_ID_REQ | VOLUMIO_PLAY):
                    print "command_router request"
                    packet_to_send = spp.Packet(packet_buffer.src_address, spp.src_address, len(self.command_router.data['status'].encode('charmap','replace'))+1, chr(cmdid.SPP_ID_RESP | VOLUMIO_PLAY) + str(self.command_router.data['status'].encode('charmap','replace')))
                    spp.send(packet_to_send)
                elif packet_buffer.payload[0] == chr(cmdid.SPP_ID_REQ | VOLUMIO_VOL):
                    print "command_router volume"
                    packet_to_send = spp.Packet(packet_buffer.src_address, spp.src_address, 2, chr(cmdid.SPP_ID_RESP | VOLUMIO_VOL) + chr(self.command_router.data['volume']))
                    spp.send(packet_to_send)
                elif packet_buffer.payload[0] == chr(cmdid.SPP_ID_REQ | VOLUMIO_TITLE):
                    print "title request"
                    packet_to_send = spp.Packet(packet_buffer.src_address, spp.src_address, len(self.command_router.data['title'].encode('charmap','replace'))+1, chr(cmdid.SPP_ID_RESP | VOLUMIO_TITLE) + self.command_router.data['title'].encode('charmap','replace'))
                    spp.send(packet_to_send)
                elif packet_buffer.payload[0] == chr(cmdid.SPP_ID_REQ | VOLUMIO_ARTIST):
                    print "artist request"
                    packet_to_send = spp.Packet(packet_buffer.src_address, spp.src_address, len(self.command_router.data['artist'].encode('charmap','replace'))+1, chr(cmdid.SPP_ID_RESP | VOLUMIO_TITLE) + self.command_router.data['artist'].encode('charmap','replace'))
                    spp.send(packet_to_send)
                elif packet_buffer.payload[0] == chr(cmdid.SPP_ID_REQ | VOLUMIO_ALBUM):
                    print "album request"
                    packet_to_send = spp.Packet(packet_buffer.src_address, spp.src_address, len(self.command_router.data['album'].encode('charmap','replace'))+1, chr(cmdid.SPP_ID_RESP | VOLUMIO_TITLE) + self.command_router.data['album'].encode('charmap','replace'))
                    spp.send(packet_to_send)
                elif packet_buffer.payload[0] == chr(cmdid.SPP_ID_NITEMODE_ON) and len(packet_buffer.payload) == 1:
                    print "Performing sleep"
                    self.command_router.night_mode()
                elif packet_buffer.payload[0] == chr(cmdid.SPP_ID_NITEMODE_OFF) and len(packet_buffer.payload) == 1:
                    print "Performing normal"
                    self.command_router.normal_mode()
                elif packet_buffer.payload[0] == chr(VOLUMIO_ALERT) and len(packet_buffer.payload) == 2:
                    print "Performing alert"
                    self.command_router.play_alert(packet_buffer.payload[1])
                else:
                    print("Unkown command: "+packet_buffer.payload)

    def broadcast_info(self):
        while True:
            if self.command_router.data["position"] != self.current_position:
                self.current_position = self.command_router.data["position"]
                spp.send(spp.Packet(0xFF,spp.src_address, len(self.command_router.data['title'].encode('charmap','replace'))+1, chr(cmdid.SPP_ID_MULTICAST) + self.command_router.data['title'].encode('charmap','replace')))
            time.sleep(0.5)

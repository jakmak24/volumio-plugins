# -*- coding: utf-8 -*-
import threading
import os
import spp
import cmdid
import time
import json


VOLUMIO_PLAY = 0x01
VOLUMIO_VOL = 0x02
VOLUMIO_TITLE = 0x03
VOLUMIO_ARTIST = 0x04
VOLUMIO_ALBUM = 0x05
VOLUMIO_ALERT = 0x06

DEFAULT_ADDRESS = 0x11

class VolumioSppob:
    def __init__(self,command_router,config):

        self.command_router=command_router
        self.sppob =spp.SPPoB()
        self.current_position = None
        try:
            src = config['sppob']['group']['value']*16 + config['sppob']['device']['value']
            self.sppob.set_src(src)
        except:
            print("Failed to load data")
            self.sppob.set_src(DEFAULT_ADDRESS)

    def listen(self):
        while True:
            packet_buffer = self.sppob.listen_packet()
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
                self.sppob.send(spp.Packet(0xFF,self.sppob.src_address, len(self.command_router.data['title'].encode('charmap','replace'))+1, chr(cmdid.SPP_ID_MULTICAST) + self.command_router.data['title'].encode('charmap','replace')))
            time.sleep(0.5)

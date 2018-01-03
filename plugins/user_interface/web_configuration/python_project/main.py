# -*- coding: utf-8 -*-

from socketIO_client import SocketIO, LoggingNamespace
import threading
import time
import os
import sys
import setproctitle
import signal
import json

setproctitle.setproctitle('volumio_addon')
displayer = None

def signal_term_handler(signal, frame):
    print("Received signal:",signal)
    if displayer is not None:
        displayer.turn_off_led()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_term_handler)
signal.signal(signal.SIGINT, signal_term_handler)

from volumio import volumio_client as vc

with SocketIO('localhost', 3000, LoggingNamespace) as socketIO:

    with open('/data/configuration/user_interface/web_configuration/config.json') as json_data:
        config = json.load(json_data)

    if config['displayer']['enabled']['value'] == True:
        from lcd import tft_simple as tft
        displayer = tft.TFT_Displayer()

    command_router = vc.CommandRouter(socketIO,displayer)

    socketIO.on("pushState", command_router.updateData)
    socketIO.emit("getState")

    socketIO.wait(1)

    if displayer is not None:
        from lcd import update_screen
        screen_updater = update_screen.ScreenUpdater(command_router)
        update_screen_thread = threading.Thread(target=screen_updater.updateScreen)
        update_screen_thread.setDaemon(True)
        update_screen_thread.start()


    if config['buttons']['enabled']['value'] == True:
        from gpio import buttons
        from gpio import rotary
        r = rotary.Rotary(command_router)
        rotary_thread = threading.Thread(target=r.loop)
        rotary_thread.setDaemon(True)
        rotary_thread.start()

        buttons.Buttons(command_router)

    if config['remote']['enabled']['value'] == True:
        from ir import ir
        ir_controller = ir.IRController(command_router)
        ir_thread = threading.Thread(target=ir_controller.listen)
        ir_thread.setDaemon(True)
        ir_thread.start()

    if config['sppob']['enabled']['value'] == True:
        from sppob import volumioSppob as spp_dev
        try:
            volumio_sppob = spp_dev.VolumioSppob(command_router,config)
            listen_thead = threading.Thread(target=volumio_sppob.listen)
            listen_thead.setDaemon(True)
            listen_thead.start()

            broadcast_info_thread = threading.Thread(target=volumio_sppob.broadcast_info)
            broadcast_info_thread.setDaemon(True)
            broadcast_info_thread.start()
        except Exception as e:
            print e

    socketIO.wait()

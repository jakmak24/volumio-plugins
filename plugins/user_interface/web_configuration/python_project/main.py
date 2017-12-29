# -*- coding: utf-8 -*-

from socketIO_client import SocketIO, LoggingNamespace
import threading
import time
import os
import sys
import setproctitle
import signal

setproctitle.setproctitle('volumio_addon')

def signal_term_handler(signal, frame):
    print("Received signal:",signal)
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_term_handler)
signal.signal(signal.SIGINT, signal_term_handler)

from gpio import buttons
from gpio import rotary
from sppob import volumioSppob as spp_dev
from volumio import volumio_client as vc
from lcd import update_screen
from lcd import tft_simple as tft
from ir import ir

with SocketIO('localhost', 3000, LoggingNamespace) as socketIO:
    displayer = tft.TFT_Displayer()
    command_router = vc.CommandRouter(socketIO,displayer)
    screen_updater = update_screen.ScreenUpdater(command_router,displayer)

    socketIO.on("pushState", command_router.updateData)
    socketIO.emit("getState")

    socketIO.wait(1)

    update_screen_thread = threading.Thread(target=screen_updater.updateScreen)
    update_screen_thread.setDaemon(True)
    update_screen_thread.start()


    r = rotary.Rotary(command_router)
    rotary_thread = threading.Thread(target=r.loop)
    rotary_thread.setDaemon(True)
    rotary_thread.start()

    buttons.Buttons(command_router)
    ir_controller = ir.IRController(command_router)
    ir_thread = threading.Thread(target=ir_controller.listen)
    ir_thread.setDaemon(True)
    ir_thread.start()

    try:
        volumio_sppob = spp_dev.VolumioSppob(command_router)
        listen_thead = threading.Thread(target=volumio_sppob.listen)
        listen_thead.setDaemon(True)
        listen_thead.start()

        broadcast_info_thread = threading.Thread(target=volumio_sppob.broadcast_info)
        broadcast_info_thread.setDaemon(True)
        broadcast_info_thread.start()
    except Exception as e:
        print e

    socketIO.wait()

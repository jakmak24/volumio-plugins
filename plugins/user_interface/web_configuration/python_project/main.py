# -*- coding: utf-8 -*-

from socketIO_client import SocketIO, LoggingNamespace
import threading
import time
import os

from ir import ir
import RPi.GPIO as GPIO
from gpio import buttons
from gpio import rotary
from sppob import volumioSppob as spp_dev
from volumio import volumio_client as vc
from lcd import update_screen
import setproctitle
import signal

setproctitle.setproctitle('volumio_addon')

lock = threading.Lock()
data = {'title':'Unknown','artist':'Unknown','album':'Unknown','status':'stop','volume':0,'duration':0,'seek':0,'mute':False}
command_router = None

def signal_term_handler(signal, frame):
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_term_handler)

def updateData (*args):
    global command_router

    lock.acquire()
    command_router.data = args[0]

    try:
        if command_router.data['title'] is None or "":
            command_router.data['title'] = "Unknown"
    except KeyError, e:
        print e
        command_router.data['title'] = "Unknown"
    try:
        if command_router.data['album'] is None or "":
            command_router.data['album'] = "Unknown"
    except KeyError, e:
        print e
        command_router.data['album'] = "Unknown"
    try:
        if command_router.data['artist'] is None or "":
            command_router.data['artist'] = "Unknown"
    except KeyError, e:
        print e
        command_router.data['artist'] = "Unknown"

    lock.release()


with SocketIO('localhost', 3000, LoggingNamespace) as socketIO:
    command_router = vc.CommandRouter(data,socketIO)
    screen_updater = update_screen.ScreenUpdater(command_router)

    socketIO.on("pushState", updateData)
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

    try:
        socketIO.wait()
    except KeyboardInterrupt:
        GPIO.cleanup()
        os._exit(0)

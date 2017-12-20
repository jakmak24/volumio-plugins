import subprocess
import time

class IRController():

    def __init__(self,command_router):
        self.command_router = command_router


    def listen(self):
        cmd = "irw"
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while True:
            line = p.stdout.readline()
            ir_command = line.split(" ")[2]
            ir_command_accurance = int(line.split(" ")[1],16)

            #HERE PERFORM ACTIONS
            print ir_command,ir_command_accurance
            if ir_command == "ch+" and ir_command_accurance % 2 == 0:
                self.command_router.seek(5)
            elif ir_command == "ch-" and ir_command_accurance % 2 == 0:
                self.command_router.seek(-5)
            elif ir_command == "ch" and ir_command_accurance == 0:
                self.command_router.toggle_led()
            elif ir_command == 'prev' and ir_command_accurance == 0:
                self.command_router.prev()
            elif ir_command == 'next' and ir_command_accurance == 0:
                self.command_router.next()
            elif ir_command == 'play/pause' and ir_command_accurance == 0:
                self.command_router.toggle_play_pause()
            elif ir_command == 'vol+' and ir_command_accurance % 2 == 0:
                self.command_router.vol_up()
            elif ir_command == 'vol-' and ir_command_accurance % 2 == 0:
                self.command_router.vol_down()
            elif ir_command == 'eq' and ir_command_accurance == 0:
                self.command_router.toggle_mute()
            elif ir_command in ["0","1","2","3","4","5","6","7","8","9"] and ir_command_accurance == 0:
                self.command_router.play_alert(chr(int(ir_command)))


            if line == '' and p.poll() != None:
                break

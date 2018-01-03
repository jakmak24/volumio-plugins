import crc8
import time
import serial

SPP_IDLE_TIMEOUT = 10
SPP_PAYLOAD_LEN = 40

PACKET_START = chr(0x7E)
# enum equivalent
SPP_STATE_IDLE, SPP_STATE_DST_ADDRESS, SPP_STATE_SRC_ADDRESS, SPP_STATE_LEN, SPP_STATE_PAYLOAD, SPP_STATE_CRC = range(6)


class Packet:
    def __init__(self, dst, src, length, payload):
        self.dst_address = dst
        self.src_address = src
        self.length = length
        self.payload = payload

    def copy(self):
        return Packet(self.dst_address, self.src_address, self.length, self.payload)


class CrcByte:

    def __init__(self):
        self.crc = 0

    def update(self, data):

        self.crc ^= ord(data)
        for i in range(8):
            if self.crc & 0x01 :
                self.crc = (self.crc >> 1) ^ 0x8C
            else:
                self.crc >>= 1
        return self.crc

    def digest(self):
        return chr(self.crc)

class InvalidException(Exception):
    pass

class SPPoB:
# GLOBAL VARIABLES

    def __init__(self):

        self.ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        self.src_address = None
        self.spp_rx_state = SPP_STATE_IDLE
        self.packetBuffer = Packet(0, 0, 0, '')
        self.mismatch = False
        self.dispatch = False
        self.payload_cnt = 0
        self.rx_crc = None

    # set CRC class implementation, must implement void:update(byte) and chr:digest()
    def set_crc(self):
        #return crc8.crc8()
        return CrcByte()

    def set_src(self,src):
        self.src_address = src


    def txwd(self,ch):
        if ch == chr(0x7E):
            self.ser.write(chr(0x7D))
            self.ser.write(chr(0x5E))
        elif ch == chr(0x7D):
            self.ser.write(chr(0x7D))
            self.ser.write(chr(0x5D))
        else:
            self.ser.write(ch)

    def is_bus_free(self):
        if self.spp_rx_state == SPP_STATE_IDLE:
            return True
        else:
            return False


    def wait_for_free_bus(self):
        timeout = 100
        while timeout > 0:
            if self.is_bus_free():
                return True
            timeout -= 1
            time.sleep(0.001)
        return False


    def check_dst_address(self,address, src_address):
        # broadcast to all instances of a class (addr[3:0]==0xF and addr[7:4] matches SPP_ADDRESS[7:4])
        address = ord(address)

        if (address & 0x0F == 0x0F) and ((address & 0xF0) == (src_address & 0xF0)):
            return True

        # broadcast to all devices in the network
        if address == 0xFF:
            return True

        # 1:1 match
        if address == src_address:
            return True
        # mismatch
        return False





    def listen_packet(self):
        self.spp_rx_state
        self.payload_cnt
        self.mismatch
        self.dispatch
        self.rx_crc

        try:

            cc = self.ser.read(1)

            if cc == PACKET_START:
                self.rx_crc = self.set_crc()
                self.spp_rx_state = SPP_STATE_DST_ADDRESS
                self.dispatch = False
                self.mismatch = False
                return None

            elif cc == chr(0x7D):
                self.dispatch = True
                return None

            elif cc == chr(0x5E):
                if self.dispatch:
                    cc = chr(0x7E)
                    self.dispatch = False

            elif cc == chr(0x5D):
                if self.dispatch:
                    cc = chr(0x7D)
                    self.dispatch = False

            if self.dispatch:
                raise InvalidException("Error while dispaching")  # invalid dispach

            if self.spp_rx_state == SPP_STATE_DST_ADDRESS:
                self.mismatch = not self.check_dst_address(cc, self.src_address)
                self.packetBuffer.dst_address = ord(cc)
                self.rx_crc.update(cc)
                self.spp_rx_state = SPP_STATE_SRC_ADDRESS
                return None

            elif self.spp_rx_state == SPP_STATE_SRC_ADDRESS:
                self.packetBuffer.src_address = ord(cc)
                self.rx_crc.update(cc)
                self.spp_rx_state = SPP_STATE_LEN
                return None

            elif self.spp_rx_state == SPP_STATE_LEN:
                if ord(cc) > SPP_PAYLOAD_LEN - 1:
                    self.mismatch = True
                self.rx_crc.update(cc)
                self.packetBuffer.length = ord(cc)
                self.packetBuffer.payload = ''
                self.payload_cnt = 0
                self.spp_rx_state = SPP_STATE_PAYLOAD
                return None

            elif self.spp_rx_state == SPP_STATE_PAYLOAD:

                if self.payload_cnt < (self.packetBuffer.length - 1):
                    self.payload_cnt += 1
                else:
                    self.spp_rx_state = SPP_STATE_CRC
                self.packetBuffer.payload += cc
                self.rx_crc.update(cc)
                return None

            elif self.spp_rx_state == SPP_STATE_CRC:
                if cc == self.rx_crc.digest():
                    self.spp_rx_state = SPP_STATE_IDLE
                    if not self.mismatch:
                        return self.packetBuffer
                    else:
                        return None
                else:
                    raise InvalidException("Crc Exception")

        except InvalidException, e:
            print e.message
            self.spp_rx_state = SPP_STATE_IDLE
            return None


    def send(self,packet):
        wait_retries_left = 3
        while (not self.is_bus_free()) and (wait_retries_left > 0):
            self.wait_for_free_bus()
            time.sleep(packet.src_address * 2 * 0.001)
            wait_retries_left -= 1

        self.ser.write(PACKET_START)
        tx_crc = self.set_crc()

        self.txwd(chr(packet.dst_address))
        tx_crc.update(chr(packet.dst_address))

        self.txwd(chr(packet.src_address))
        tx_crc.update(chr(packet.src_address))

        self.txwd(chr(packet.length))
        tx_crc.update(chr(packet.length))

        for ch in packet.payload:
            self.txwd(ch)
            tx_crc.update(ch)

        self.txwd(tx_crc.digest())

    def __destroy__(self):
        self.ser.close()

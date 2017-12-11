import crc8
import time

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


# GLOBAL VARIABLES
ser = None
src_address = None
spp_rx_state = SPP_STATE_IDLE
packetBuffer = Packet(0, 0, 0, '')
mismatch = False
dispatch = False
payload_cnt = 0
rx_crc = None


# set CRC class implementation, must implement void:update(byte) and chr:digest()
def set_crc():
    #return crc8.crc8()
    return CrcByte()


def init(serial):
    global ser
    ser = serial

def set_src(src):
    global src_address
    src_address = src


def txwd(ch):
    if ch == chr(0x7E):
        ser.write(chr(0x7D))
        ser.write(chr(0x5E))
    elif ch == chr(0x7D):
        ser.write(chr(0x7D))
        ser.write(chr(0x5D))
    else:
        ser.write(ch)


def is_bus_free():

    if spp_rx_state == SPP_STATE_IDLE:
        return True
    else:
        return False


def wait_for_free_bus():
    timeout = 100
    while timeout > 0:
        if is_bus_free():
            return True
        timeout -= 1
        time.sleep(0.001)
    return False


def check_dst_address(address, src_address):
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


class InvalidException(Exception):
    pass


def listen_packet():
    global spp_rx_state
    global payload_cnt
    global mismatch
    global dispatch
    global rx_crc

    try:

        cc = ser.read(1)

        if cc == PACKET_START:
            rx_crc = set_crc()
            spp_rx_state = SPP_STATE_DST_ADDRESS
            dispatch = False
            mismatch = False
            return None

        elif cc == chr(0x7D):
            dispatch = True
            return None

        elif cc == chr(0x5E):
            if dispatch:
                cc = chr(0x7E)
                dispatch = False

        elif cc == chr(0x5D):
            if dispatch:
                cc = chr(0x7D)
                dispatch = False

        if dispatch:
            raise InvalidException("Error while dispaching")  # invalid dispach

        if spp_rx_state == SPP_STATE_DST_ADDRESS:
            mismatch = not check_dst_address(cc, src_address)
            packetBuffer.dst_address = ord(cc)
            rx_crc.update(cc)
            spp_rx_state = SPP_STATE_SRC_ADDRESS
            return None

        elif spp_rx_state == SPP_STATE_SRC_ADDRESS:
            packetBuffer.src_address = ord(cc)
            rx_crc.update(cc)
            spp_rx_state = SPP_STATE_LEN
            return None

        elif spp_rx_state == SPP_STATE_LEN:
            if ord(cc) > SPP_PAYLOAD_LEN - 1:
                mismatch = True
            rx_crc.update(cc)
            packetBuffer.length = ord(cc)
            packetBuffer.payload = ''
            payload_cnt = 0
            spp_rx_state = SPP_STATE_PAYLOAD
            return None

        elif spp_rx_state == SPP_STATE_PAYLOAD:

            if payload_cnt < (packetBuffer.length - 1):
                payload_cnt += 1
            else:
                spp_rx_state = SPP_STATE_CRC
            packetBuffer.payload += cc
            rx_crc.update(cc)
            return None

        elif spp_rx_state == SPP_STATE_CRC:
            if cc == rx_crc.digest():
                spp_rx_state = SPP_STATE_IDLE
                if not mismatch:
                    return packetBuffer
                else:
                    return None
            else:
                raise InvalidException("Crc Exception")

    except InvalidException, e:
        print e.message
        spp_rx_state = SPP_STATE_IDLE
        return None


def send(packet):
    wait_retries_left = 3
    while (not is_bus_free()) and (wait_retries_left > 0):
        wait_for_free_bus()
        time.sleep(packet.src_address * 2 * 0.001)
        wait_retries_left -= 1

    ser.write(PACKET_START)
    tx_crc = set_crc()

    txwd(chr(packet.dst_address))
    tx_crc.update(chr(packet.dst_address))

    txwd(chr(packet.src_address))
    tx_crc.update(chr(packet.src_address))

    txwd(chr(packet.length))
    tx_crc.update(chr(packet.length))

    for ch in packet.payload:
        txwd(ch)
        tx_crc.update(ch)

    txwd(tx_crc.digest())

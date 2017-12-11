__author__ = 'Jakub'

#payload[0] commands

#global control IDs
SPP_ID_ACK =			0x00	#packet is ACK
SPP_ID_EXT =			0x01	#extended command in payload
SPP_ID_NITEMODE_ON =	0x02	#enter night mode
SPP_ID_NITEMODE_OFF =	0x03	#exit night mode
SPP_ID_ALL_ON =			0x04	#all channels ON
SPP_ID_ALL_OFF =		0x05	#all channels OFF
SPP_ID_ALL_ON_ALT =		0x06	#all channels ON (alternative)
SPP_ID_ALL_OFF_ALT =	0x07	#all channels OFF (alternative)
SPP_ID_MULTICHANNEL	= 	0x08	#selective ON/OFF/Toggle: determined by payload[3:1]
SPP_ID_TEXT	=			0x0A	#payload[1]-id, payload[2,...]-text
SPP_ID_MULTICAST =		0x0F	#reserved for multicast messages

#channel command IDs
SPP_ID_CHAN_ON	=		0x10
SPP_ID_CHAN_OFF	=		0x20
SPP_ID_CHAN_TOGGLE	=	0x30

SPP_ID_CHAN_ON_ALT	=	    0x40
SPP_ID_CHAN_OFF_ALT	=	    0x50
SPP_ID_CHAN_TOGGLE_ALT =	0x60

SPP_ID_CHAN_UP	=		0x70	#increase value for a channel
SPP_ID_CHAN_DN	=		0x80	#decrease value for a channel
SPP_ID_CHAN_VALUE =	    0x90	#set value for a channel, value in payload[1]
SPP_ID_CHAN_VALUE_ALT =	0xA0	#set value for a channel, value in payload[1]

SPP_ID_TRANSITION =		0xB0	#set default transition speed for each channel
SPP_ID_POWER_DEFAULT =	0xC0	#set power level applied with "on" and "toggle" commands

#Data IDs
SPP_ID_TIME =			0xD0	#time info
SPP_ID_CHANNEL_STATE =	0xD1	#state info for channel devices
SPP_ID_TEMPERATURE =	0xD2	#temperature
SPP_ID_PRESSURE =		0xD3	#pressure

#request-response
SPP_ID_REQ =			0xE0
SPP_ID_RESP =			0xF0
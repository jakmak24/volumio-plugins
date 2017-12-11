 #!/usr/bin/env python

from socketIO_client import SocketIO, LoggingNamespace
import sys

with SocketIO('localhost', 3000, LoggingNamespace) as socketIO:
	if len(sys.argv) == 2:
		socketIO.emit(str(sys.argv[1]))
	elif len(sys.argv) == 3:
		socketIO.emit(str(sys.argv[1]), (sys.argv[2]))
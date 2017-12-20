 #!/usr/bin/env python

from socketIO_client import SocketIO, LoggingNamespace
import sys

import json

def js_list(encoder, data):
    pairs = []
    for v in data:
        pairs.append(js_val(encoder, v))
    return "[" + ", ".join(pairs) + "]"

def js_dict(encoder, data):
    pairs = []
    for k, v in data.iteritems():
        pairs.append(k + ": " + js_val(encoder, v))
    return "{" + ", ".join(pairs) + "}"

def js_val(encoder, data):
    if isinstance(data, dict):
        val = js_dict(encoder, data)
    elif isinstance(data, list):
        val = js_list(encoder, data)
    else:
        val = encoder.encode(data)
    return val

encoder = json.JSONEncoder(ensure_ascii=False)
al = js_val(encoder, {'type':'success','title': 'tytyasd', 'message': 'some great title'})

with SocketIO('localhost', 3000, LoggingNamespace) as socketIO:
	if len(sys.argv) == 2:
		socketIO.emit(str(sys.argv[1]))
	elif len(sys.argv) == 3:
		socketIO.emit(str(sys.argv[1]), (sys.argv[2]))
	else:
		print(al)
		socketIO.emit("pushToastMessage", al)

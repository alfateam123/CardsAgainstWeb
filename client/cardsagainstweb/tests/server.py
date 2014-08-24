import socket
import json

def prepare_json(dict_):
	return bytes(json.dumps(dict_), "UTF-8")

wat_do = {
"connect": (lambda message: {
	"playerkey": message["playerkey"],
	"action": "connect",
	"value":"accepted"
	}),
"ready": (lambda message: {
	"playerkey": message["playerkey"],
	"action": "ready",
	"value": "accepted",
	"missing": [] 
	}),
"match_end": (lambda message: {
	"playerkey": message["playerkey"],
	"action":"match_end",
	"value": counter_
	})
}

HOST = ''                 # Symbolic name meaning the local host
PORT = 50007              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)
conn, addr = s.accept()
counter_ = 0
print('Connected by', addr)
while 1:
    data = conn.recv(1024)
    if not data: break
    print( data)
    #conn.send(data)
    data = json.loads(str(data, "UTF-8"))
    if not data["action"] in wat_do: data["action"]="match_end"
    w=prepare_json(wat_do[data["action"]](data))
    counter_+=1
    conn.send(w)
conn.close()
import socket 
import threading
import queue
import json

messages = queue.Queue()
clients = []
names = {}
onlyNames = []

server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
serverport = 12345
server.bind(("0.0.0.0",serverport))

def receive():
    while True:
        try:
            msg, addr = server.recvfrom(1024)
            messages.put((msg,addr))
        except:
            pass

def broadcast():

    while True:
        while not messages.empty():
            msg, addr = messages.get()
            decodedMsg = msg.decode()
            if addr not in clients:
                jsonCMD = json.loads(decodedMsg)
                try:
                    if (jsonCMD["command"] == "register") & (len(jsonCMD["name"]) > 0):
                        name = jsonCMD["name"]
                        if jsonCMD["name"] not in onlyNames:
                            clients.append(addr)
                            names[str(addr)] = name
                            onlyNames.append(name)
                            print(clients)
                            respJson = {"cmd":"register","result":"success", "name":name}
                            respJsonStr = json.dumps(respJson)
                            server.sendto(respJsonStr.encode(),addr)
                            sendUpdatedList()

                        else:
                            print("Existgs")
                            respJson = {"cmd":"register","result":"fail","name":name}
                            respJsonStr = json.dumps(respJson)
                            server.sendto(respJsonStr.encode(),addr)
                    elif jsonCMD["command"] == "/join":
                        portconf = {"cmd":"portconf"}
                        
                        portconfstr = json.dumps(portconf).encode()
                        server.sendto(portconfstr,addr)
                        print("sent proft")
                        
                except Exception as e:
                    print(e)

            sentPrivate = False
            priv = False

            for client in clients:
                try:
                    m = msg.decode()
                    print(m,"57 line")
                    jsonCMD = json.loads(m)
                    cmd =  jsonCMD["command"]
                    if cmd == "registered":
                        
                        sendJsonCMD = {}
                        sendJsonCMD["cmd"] = "joined"
                        sendJsonCMD["msg"] = f"Welcome {name}!"
                        sendJsonCMDStr = json.dumps(sendJsonCMD)
                        print("here")
                        server.sendto(sendJsonCMDStr.encode(),client)
                        print("done")
                    
                    elif cmd == "leave":
                        disconnectName = jsonCMD["name"]
                        print(disconnectName,"requested to leave")
                        # try:
                        clients.remove(addr)
                        name = names[str(addr)]
                        del names[str(addr)]
                        print(clients,"removed")
                        onlyNames.remove(name)
                        sendUpdatedList()
                        # except Exception as e:
                        #     print("Remove error: ",e)
                        # hpsod
                        
                        sendJsonCMD = {}
                        sendJsonCMD["cmd"] = "left"
                        sendJsonCMD["msg"] = f"{name} left the chat room!"
                        sendJsonCMDStr = json.dumps(sendJsonCMD)
                        # server.sendto(sendJsonCMDStr.encode(),client)
                        for c in clients:
                            server.sendto(sendJsonCMDStr.encode(),c)
                        break
                    else:
                        jsonCMD = json.loads(m)
                        cmd =  jsonCMD["command"]
                        sendJsonCMD = {}
                        if cmd == "/all":
                            f = names[str(addr)] + ": " + jsonCMD["message"]
                            if client != addr:
                                finalMsg = f + " ``bluemsg"
                            else:
                                finalMsg = f + " ``~~"
                            sendJsonCMD["cmd"] = "message"
                            sendJsonCMD["msg"] = finalMsg
                            sendJsonCMDStr = json.dumps(sendJsonCMD)
                            server.sendto(sendJsonCMDStr.encode(),client)

                        elif cmd == "/msg":
                            to = jsonCMD["handle"]
                            finalMsg = jsonCMD["message"]
                            
                            if to in onlyNames and to != names[str(addr)]:

                                if names[str(client)] == to:
                                    k = f"[FROM {names[str(addr)]}]: " + finalMsg + " ``redmsg"
                                    sendJsonCMD["cmd"] = "message"
                                    sendJsonCMD["msg"] = k
                                    sendJsonCMDStr = json.dumps(sendJsonCMD)
                                    server.sendto(sendJsonCMDStr.encode(),client)
                                    sendJsonCMD["cmd"] = "message"
                                    k = f"[To: {to}] " + finalMsg + " ``~~"
                                    sendJsonCMD["msg"] = k
                                    sendJsonCMDStr = json.dumps(sendJsonCMD)
                                    server.sendto(sendJsonCMDStr.encode(),addr)

                            elif to == names[str(addr)]:
                                sendJsonCMD["cmd"] = "error"
                                sendJsonCMD["msg"] = "You can't send a private message to yourself!"
                                sendJsonCMDStr = json.dumps(sendJsonCMD)
                                server.sendto(sendJsonCMDStr.encode(),addr)

                            else:
                                sendJsonCMD["cmd"] = "error"
                                sendJsonCMD["msg"] = "Error: Handle not found."
                                sendJsonCMDStr = json.dumps(sendJsonCMD)
                                server.sendto(sendJsonCMDStr.encode(),addr)
                except Exception as e:
                    print(e)
                    clients.remove(client)
            if priv and not sentPrivate:
                server.sendto("~~~error priv".encode(), addr)

def sendUpdatedList():
    namesListStr = " ".join(onlyNames)
    sendJsonCMD = {"cmd":"listUpdate","names" : namesListStr}
    sendJsonCMDStr = json.dumps(sendJsonCMD)
    print("hposd")
    for c in clients:
        print(c ,"cccp[ods")
        server.sendto(sendJsonCMDStr.encode(), c)

t1 = threading.Thread(target=receive)                    
t2 = threading.Thread(target=broadcast)
t1.start()
t2.start()

import socket 
import threading
import random
import json
import time


class Client:
    def __init__(self,
    # SERVER,
    name,
    chat_print,
    showinfo,
    console_print,
    list_print,
    changeName,
    clientHandle
    ):
        # self.SERVER = SERVER
        self.joined = False
        self.name = name
        self.showinfo = showinfo
        self.chat_print = chat_print
        self.console_print = console_print
        self.list_print = list_print
        self.namesList = []
        self.allow = False
        self.changeName = changeName
        self.SERVER = [0,0]
        self.clientHandle = clientHandle

    def connect(self,SERVER):
        
        self.SERVER = SERVER
        self.s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.s.bind((self.SERVER[0],random.randint(6000, 10000)))
        jsonCMD = {"command":"/join","name":self.name}
        jsonCMDStr = json.dumps(jsonCMD)
        self.run()
        self.s.sendto(jsonCMDStr.encode(), self.SERVER)
        start = time.time()
        
        while time.time() <= start + 2: pass

        if not self.allow:
            self.console_print("Error: Connection to the Message Board Server has failed! Please check IP  Address and Port Number.")
            self.clientHandle.connected = False

    def disconnect(self):
        jsonCMD = {"command":"leave","name":self.name}
        jsonCMDStr = json.dumps(jsonCMD)
        self.console_print("Connection closed. Thank You!")
        self.console_print("\n")
        self.s.sendto(jsonCMDStr.encode(), self.SERVER)
        self.s.close()
        self.allow = False
    def run(self):
        t= threading.Thread(target=self.receive)
        t.start()

    def receive(self):
        while True:
            try:
                msg, _ = self.s.recvfrom(1024)
                msg = msg.decode()



                if msg == "~~~error priv":
                    self.showinfo("Message couldn't be delivered!","No such user exists!")
                
                msgJson = json.loads(msg)
                if msgJson["cmd"] == "portconf":
                    print("recccc")
                    self.allow = True
                if msgJson["cmd"] == "message":
                    recvMsg = msgJson["msg"]
                    words = recvMsg.split(" ")
                    print(words)
                    c = words[len(words) - 1]
                    if c == "``bluemsg":
                        color = "bluemsg"
                    elif c == "``redmsg":
                        color = "redmsg"

                    del words[len(words) - 1]

                    if not c.startswith("``"):
                        words.append(c)

                    recvMsg = " ".join(words)
                    if c.startswith("``"):
                        if c == "``~~":
                            self.chat_print(recvMsg)
                        else:
                            self.chat_print(recvMsg,color)
                    else:
                        self.chat_print(recvMsg,'greenmsg')
                
                elif msgJson["cmd"] == "joined":
                    print("joined")
                    recvMsg = msgJson["msg"]
                    self.chat_print(recvMsg,'greenmsg')
                
                elif msgJson["cmd"] == "left":
                    self.chat_print(msgJson["msg"],'redmsg')
                    print("closeddd")
                    # self.s.close()
                    # break

                elif msgJson["cmd"] == "error":
                    err = msgJson["msg"]
                    self.console_print(err)
                    self.console_print("\n")
                elif msgJson["cmd"] == "listUpdate":
                    names = msgJson["names"]
                    self.namesList = names.split(" ")
                    print(self.namesList)
                    stringList = ", ".join(self.namesList)
                    stringList = stringList[0:]
                    self.list_print(stringList)
                
                elif msgJson["cmd"] == "register":
                    res = msgJson["result"]
                    namex = msgJson["name"]
                    if res == "success":
                        
                        self.changeName(namex)
                        self.name = namex
                        self.console_print("Successfully registered!")
                        self.console_print("\n")
                        replJson = {"command":"registered","name":namex}
                        self.sendMsg(json.dumps(replJson).encode())
                    else:
                        self.changeName("")
                        self.console_print(f"Registration failed. User {namex} already exists!")
                        self.console_print("\n")
                else:
                    print(msgJson)
            except Exception as e:
                print(e)
                pass
    
    def sendMsg(self,msg):
        try:
            self.s.sendto(msg,self.SERVER)
            k = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            k.bind((self.SERVER[0],random.randint(6000, 10000)))
        except:
            self.console_print("Connection error")
from tkinter import *
from tkinter import ttk
from tkinter import font
import sys
import socket
import json
import os
from client import Client
from tkinter.simpledialog import askstring
from tkinter.messagebox import showinfo
import threading

USERID = "a"
NICKNAME = "a"
name = ""
connected = False
joined = False


class ClientUIHandle:

  def __init__(self):
    self.NICKNAME = name   
    self.name = ""
    self.connected = False

  def join(self,m):
    
    if not self.connected:
      wo = m.split(" ")
      if len(wo) != 3:
        console_print("Invalid parameters! Use /join followed by server and port to connect.") 
        console_print("\n")
      else:
        try:
          
          ip = wo[1]
          port = int(wo[2])
          client.connect((ip,port))

          if client.allow:
            console_print("Connection to the Message Board Server is successful")
            console_print("\n")
            self.connected = True
            joined = True
            self.SERVER =(ip,port)
            self.SERVER_PORT = self.SERVER[1]
            self.SERVER_IP = self.SERVER[0]
            serverLBL.set(ip)
            portLBL.set(port)
        except Exception as e:
          print(e)
          console_print("Error: Connection to the Message Board Server has failed! Please check IP  Address and Port Number.")
          console_print("\n")
    else:
      console_print("Already connected to Server!")
      console_print("\n")
  
  def leave(self):
    if not self.connected:
      console_print("Error: Disconnection failed. Please connect to the server first!")
    else:
      client.disconnect()
      self.connected = False
      self.name = ""

  def do_Send(self):
    
    invalid = False
    message = get_sendmsg()
    message = message.strip("\n")
    print(message)
    cc = message.split(" ")[0]
    cc.replace(" ", "")
    qtest = message.replace(" ", "")

    if qtest != "":
      if cc not in ["/join","/leave","/msg","/?","/all","/register"] and message not in["/join","/leave","/msg","/?","/all","/register"]:
        console_print("Command not found!")
      else:
        if self.name != "":
          
          if message.startswith("/"):

            words = message.split(" ")
            jsonCMD = {"command" : words[0].strip("\n")}
            print(message,jsonCMD)
            del words[0]
            
            if cc == "/msg":
              try:
                to = words[0]
                jsonCMD["handle"] = to
                del words[0]
                m = " ".join(words)
                m = m.strip("\n")
                jsonCMD["message"] = m
              except:
                console_print("Invalid parameters")
                invalid = True
            
            elif cc == "/all":
              msg = " ".join(words)
              jsonCMD["message"] = msg.strip("\n")

            elif cc == "/join":
              self.join(message)

            elif cc == "/leave":
              if len(message.split(" ")) == 1:
                self.leave()
              else:
                console_print("Invalid parameters")


            elif cc == "/?":
              console_print("Use /join followed by server and port to connect.")
              console_print("Use /register followed by your nickname to register.")
              console_print("Use /all followed by your message to send a public message to everyone")
              console_print("Use /msg followed by handle and then the message to send a private message")
              console_print("Use /leave to leave the chat room")
              console_print("Use /? to get info about all commands")
              console_print("\n")

            if not cc == "/join":
              if not cc == "/leave":
                if not cc == "/?":
                  if not cc == "/register" or message=="/register":
                    keys = list(jsonCMD.keys())
                    if len(keys)<2 and not invalid:
                      console_print("Invalid parameters")
                      console_print("\n")
                    else:
                      try:
                        qq = jsonCMD["message"]
                        if qq == "":
                          console_print("Invalid parameters!")
                        else:
                          print("sending from else")
                          jsonStr = json.dumps(jsonCMD)
                          client.sendMsg(jsonStr.encode())
                      except:
                        pass
                  else:
                    console_print("Error: Already registered")

        else:
  # /join 192.168.29.181 9998
          if message.startswith("/?"):
            console_print("Use /join followed by server and port to connect.")
            console_print("Use /register followed by your nickname to register.")
            console_print("Use /all followed by your message to send a public message to everyone")
            console_print("Use /msg followed by handle and then the message to send a private message")
            console_print("Use /leave to leave the chat room")
            console_print("Use /? to get info about all commands")
            console_print("\n")

          else:
            if self.connected:
              if cc == "/register":
                try:
                  namex = message.split(" ")[1]
                  namex = namex.strip("\n")
                  regisJSON = {"command":"register","name":namex}
                  regisJSONStr = json.dumps(regisJSON)
                  if len(message.split(" ")) > 2:
                    console_print("Invalid parameters")
                  else: client.sendMsg(regisJSONStr.encode())
                except:
                  console_print("Invalid parameters")
              else:
                if cc == "/leave":
                  if (len(message.split(" ")) == 1):
                    console_print("Connetion closed. Thank you!")
                    self.connected = False
                  else:
                    console_print("Invalid parameters!")
                else:
                  console_print("Please register yourself first. Use /register followed by your nickname to register.")
                  console_print("\n")
            else:
              if cc == "/join":
                self.join(message)
              elif message.startswith("/leave"):
                console_print("Error: Disconnection failed. Please connect to the server first!")
              else:
                console_print("Please first connect to the server. Use /join followed by server and port to connect.")
                console_print("\n")

  def changeName(self,new_name):
    self.name = new_name
    nicknameLBL.set(self.name)
    print("bam")

def handleWindowClose():
  global win
  try:
    client.disconnect()
    win.destroy()
  finally:
    exit()

#################################################################################
#Do not make changes to the following code. They are for the UI                 #
#################################################################################

#for displaying all log or error messages to the console frame
def console_print(msg):
  console['state'] = 'normal'
  console.insert(1.0, "\n"+msg)
  console['state'] = 'disabled'

#for displaying all chat messages to the chatwin message frame
#message from this user - justify: left, color: black
#message from other user - justify: right, color: red ('redmsg')
#message from group - justify: right, color: green ('greenmsg')
#message from broadcast - justify: right, color: blue ('bluemsg')
def chat_print(msg, opt=""):
  chatWin['state'] = 'normal'
  chatWin.insert(1.0, "\n"+msg, opt)
  chatWin['state'] = 'disabled'

#for displaying the list of users to the ListDisplay frame
def list_print(msg):
  ListDisplay['state'] = 'normal'
  #delete the content before printing
  ListDisplay.delete(1.0, END)
  ListDisplay.insert(1.0, msg)
  ListDisplay['state'] = 'disabled'

#for getting the outgoing message from the "Send" input field
def get_sendmsg():
  msg = SendMsg.get(1.0, END)
  SendMsg.delete(1.0, END)
  return msg

def createClientInstance():
  global clientHandle
  global client
  clientHandle = ClientUIHandle()
  client = Client(clientHandle.name,chat_print,showinfo,console_print,list_print,clientHandle.changeName,clientHandle)

def checkForSend(e):
  clientHandle.do_Send()

createClientInstance()
#
# Set up of Basic UI
#
win = Tk()
win.title("CSNETWK: Message Board System")

#Special font settings
boldfont = font.Font(weight="bold")


nicknameLBL = StringVar(win,clientHandle.name)

serverLBL = StringVar(win,client.SERVER[0])
portLBL = StringVar(win,str(client.SERVER[1]))

win.bind("<Return>",checkForSend)

#Frame for displaying connection parameters
topframe = ttk.Frame(win, borderwidth=1)
topframe.grid(column=0,row=0,sticky="w")
ttk.Label(topframe, text="NICKNAME", padding="5" ).grid(column=0, row=0)
ttk.Label(topframe, textvariable=nicknameLBL, foreground="green", padding="5", font=boldfont).grid(column=1,row=0)

ttk.Label(topframe, text="SERVER", padding="5" ).grid(column=4, row=0)
ttk.Label(topframe, textvariable=serverLBL, foreground="green", padding="5", font=boldfont).grid(column=5,row=0)
ttk.Label(topframe, text="SERVER_PORT", padding="5" ).grid(column=6, row=0)
ttk.Label(topframe, textvariable=portLBL, foreground="green", padding="5", font=boldfont).grid(column=7,row=0)


#Frame for displaying Chat messages
msgframe = ttk.Frame(win, relief=RAISED, borderwidth=1)
msgframe.grid(column=0,row=1,sticky="ew")
msgframe.grid_columnconfigure(0,weight=1)
topscroll = ttk.Scrollbar(msgframe)
topscroll.grid(column=1,row=0,sticky="ns")
chatWin = Text(msgframe, height='15', padx=10, pady=5, insertofftime=0, state='disabled')
chatWin.grid(column=0,row=0,sticky="ew")
chatWin.config(yscrollcommand=topscroll.set)
chatWin.tag_configure('redmsg', foreground='red', justify='right')
chatWin.tag_configure('greenmsg', foreground='green', justify='right')
chatWin.tag_configure('bluemsg', foreground='blue', justify='right')
topscroll.config(command=chatWin.yview)

#Frame for buttons and input
midframe = ttk.Frame(win, relief=RAISED, borderwidth=0)
midframe.grid(column=0,row=2,sticky="ew")
QButt = Button(midframe, width='8',height='3', relief=RAISED, text="LEAVE", command=clientHandle.leave).grid(column=0,row=1,sticky="w",padx=3)
innerframe = ttk.Frame(midframe,relief=RAISED,borderwidth=0)
innerframe.grid(column=1,row=0,rowspan=2,sticky="ew")
midframe.grid_columnconfigure(1,weight=1)
innerscroll = ttk.Scrollbar(innerframe)
innerscroll.grid(column=1,row=0,sticky="ns")
#for displaying the list of users
ListDisplay = Text(innerframe, height="3", padx=5, pady=5, fg='blue',insertofftime=0, state='disabled')
ListDisplay.grid(column=0,row=0,sticky="ew")
innerframe.grid_columnconfigure(0,weight=1)
ListDisplay.config(yscrollcommand=innerscroll.set)
innerscroll.config(command=ListDisplay.yview)
SButt = Button(midframe, width='8',height='3', relief=RAISED, text="SEND", command=clientHandle.do_Send).grid(column=0,row=3,sticky="nw",padx=3)
#for user to enter the outgoing message
SendMsg = Text(midframe, height='3', padx=5, pady=5, relief=SOLID)
SendMsg.grid(column=1,row=3,sticky="ew")

#Frame for displaying console log
consoleframe = ttk.Frame(win, relief=RAISED, borderwidth=1)
consoleframe.grid(column=0,row=4,sticky="ew")
consoleframe.grid_columnconfigure(0,weight=1)
botscroll = ttk.Scrollbar(consoleframe)
botscroll.grid(column=1,row=0,sticky="ns")
console = Text(consoleframe, height='10', padx=10, pady=5, insertofftime=0, state='disabled')
console.grid(column=0,row=0,sticky="ew")
console.config(yscrollcommand=botscroll.set)
botscroll.config(command=console.yview)
win.protocol("WM_DELETE_WINDOW", handleWindowClose)
win.resizable(False, False) 
win.mainloop()

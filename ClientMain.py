# The code for changing pages was derived from: http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# License: http://creativecommons.org/licenses/by-sa/3.0/

import tkinter as tk
from tkinter import *
import socket
import threading
import time
import pickle
import ssl
import os
import argparse
import cy2 as cipher

LARGE_FONT = ("Verdana", 12)
username = "Olivia"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
list_of_connected = []
current_chats = {}

PASSWORD = "Redes"


class ChatApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PageOne):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        frame.event_generate("<<ShowFrame>>")
        #print(username)

    def create_window(self, cont):
        counter = 1
        t = tk.Toplevel()



class StartPage(tk.Frame):
#esta pagina controla la conneccion
#usuario inserta su nombre y presiona conectar para realizar la conexion con el servidor

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        #TextField(Entry) para establecer su nombre
        global username
        name = tk.Entry(self, textvariable = username)
        name.pack()


        connect_button = tk.Button(self, text="Connect",
                           command=lambda: [self.set_username(name.get()), #cambia nombre de usuario
                                            self.connect_to_server(),
                                            controller.show_frame(PageOne)
                                            ])
        connect_button.pack()


    def set_username(self, newusername):
        global username
        username = newusername
        #print(username)

    def connect_to_server(self):
        global s, username, list_of_connected

        s.connect(('', 50000))
        #sends the username that has been selected and encrypts it
        tosend = cipher.getTranslatedMessage("e", username, 10)
        s.sendall(tosend.encode("ASCII")) #send name
        #receives the list of names that are connected and decrypts it
        data = s.recv(1024)
        listreceived = cipher.getTranslatedMessage("d", data.decode("ASCII"), 10)
        string_of_connected = listreceived
        list_of_connected = string_of_connected.split(",")





class PageOne(tk.Frame):
#Page with list of connected people
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.bind("<<ShowFrame>>", self.on_show_frame)
        label = tk.Label(self, text="Page One!!!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        self.l = Listbox(self, height=10, selectmode=MULTIPLE)
        self.l.pack()

        button2 = tk.Button(self, text="Chat",
                            command=lambda: self.newChat(self.l.get(self.l.curselection())))
        button2.pack()

    def receive_from_server(self):
        #this thread handles all background package receiving from server
        global s, list_of_connected
        while True:
            data = None;
            while data is None:
                #receives the dictionary that is to be processed and shows them on the list view
                data = s.recv(1024)
                messageReceived = pickle.loads(data)
                dataholder = messageReceived["List"]
                self.l.delete(0, END)
                counter = 1
                for name in dataholder:
                    self.l.insert(counter, name)
                    counter += 1
                    #if the packet holds a message process it
                if "Message" in messageReceived:
                    messagetoprocess = messageReceived["Message"]
                    #decrypt the given message and show it in the chat screen
                    decryptedmessage = cipher.getTranslatedMessage("d", messagetoprocess["Message"], 10)
                    #if there is no already open window with said chatter open a new one
                    if not messagetoprocess["Sender"] in current_chats:
                        self.newChat(messagetoprocess["Sender"])
                    toshow = messagetoprocess["Sender"] + ": " +  decryptedmessage
                    self.MessageArea.insert(END, "\n")
                    self.MessageArea.insert(END, toshow)
                    self.MessageArea.insert(END, "\n")




    def on_show_frame(self, event):
        #this method handles when the new fram is shown for the first time
        print("I am being shown...")
        global list_of_connected, s
        #s.sendall()
        self.l.delete(0,END)
        print(list_of_connected)
        counter = 1
        for name in list_of_connected:
            self.l.insert(counter, name)
            counter += 1
        t = threading.Thread(target=self.receive_from_server)
        t.start()

    def newChat(self, receiver):
        #this methods opens a new window when called
        newChatWindow = Toplevel()

        self.MessageArea = tk.Text(newChatWindow, height = 25, width = 25, padx = 5, pady = 5)
        self.MessageArea.pack()

        messageBox = tk.Entry(newChatWindow)
        messageBox.pack()

        sendButton = tk.Button(newChatWindow, text="Send",
                            command=lambda: self.send_to_chat(messageBox.get(), receiver))
        sendButton.pack()

        current_chats[receiver] = newChatWindow



    def send_to_chat(self, message, receiver):
        #this method handles all events when the send button is pressed
        global s, username
        toshow = username + ": " + message
        self.MessageArea.insert(END, toshow)
        #create a dictionary to be sent to Server and encrypts the message and sends it
        dictionary_to_send = {}
        dictionary_to_send["Sender"] = username
        dictionary_to_send["Receiver"] = receiver
        dictionary_to_send["Message"] = cipher.getTranslatedMessage("e", message, 10)
        stosend = message
        s.sendall(pickle.dumps(dictionary_to_send))








#App start
app = ChatApp()
app.mainloop()
import select, socket, sys, queue, pickle, time
import ssl
import argparse
import cy2 as cipher

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.bind(('localhost', 50000))
server.listen(5)
inputs = [server]
names = []
connections = {}
outputs = []
message_queues = {}

while inputs:                                           #As long as there are elements in the inputs list this loop runs
    readable, writable, exceptional = select.select(    #Select obtains all sockets and places them in desired tuple
        inputs, inputs, inputs)                        #Gathers from both lists
    #print("hola")
    for s in readable:                                  #processes readable tuple first
        if s is server:                                 #checks for a new connection
            connection, client_address = s.accept()
            connection.setblocking(0)
            data = connection.recv(1024)
            #receives name and decrypts it
            receivedName = cipher.getTranslatedMessage("d",
                                                       data.decode("ASCII"),
                                                       10)
            #adds name to name conections and adds the socket to the connection dictionary
            names.append(receivedName)
            connections[receivedName] = connection


            inputs.append(connection)                   #adds new connection to input list
            message_queues[connection] = queue.Queue()  #establishes a queue for that connection to hanlde inc and out messages
            namestosend = ",".join(names)
            #encrypts the names in the list to be sent to client
            namestosend = cipher.getTranslatedMessage("e", namestosend, 10)

            connection.sendall(
                namestosend.encode("ASCII"))
        else:                                           #if its not a server socket, recv data
            data = s.recv(1024)
            pickleData = pickle.loads(data)
            #decrypts the message that has been received and adds it to the message queue of the given receiver
            Message = pickleData["Message"]
            pickleData["Message"] = cipher.getTranslatedMessage("d", Message, 10)
            message_queues[connections[pickleData["Receiver"]]].put(pickleData)


    for s in writable:
        #process sockets that are ready to write to
        time.sleep(2)
        #creates a dictionary to be sent with List and message if there exists a message
        dictionary_to_send = {}
        dictionary_to_send["List"] = names
        if(not message_queues[s].empty()):
            dictionary_to_send["Message"] = message_queues[s].get_nowait()
            #encrypt message to be sent to client
            dictionary_to_send["Message"]["Message"] = cipher.getTranslatedMessage("e", dictionary_to_send["Message"]["Message"], 10)
        #send the dictionary to client
        s.sendall(pickle.dumps(dictionary_to_send))


    for s in exceptional:                               #if socket has any exceptions remove it
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()
        del message_queues[s]
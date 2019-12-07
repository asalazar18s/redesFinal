import socket
import threading

connected_clients = {}
list_of_names = []


def deal_with_client(conn, addr):
    data = None
    text = ''

    #Initial client handler
    data = conn.recv(1024)
    name_of_connection = data.decode('ASCII')
    connected_clients[name_of_connection] = conn
    print(connected_clients)
    for name,connection in connected_clients.items():
        list_of_names.append(name)

    string_of_names = ",".join(list_of_names)
    conn.sendall(string_of_names.encode('ASCII'))
    list_of_names.clear()

    data = None

    while text != 'disconnect':
        while data is None:
            data = conn.recv(1024)

        print("Client says: " + data.decode('ASCII'))

        if data.decode('ASCII') != 'disconnect':
            data = None
        else:
            break

        text = input('Server: ')
        conn.sendall(text.encode('ASCII'))
    conn.close()


if __name__ == '__main__':

    bindsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bindsocket.bind(('', 8081))
    bindsocket.listen(5)
    fromaddr = None
    while True:
        try:
            newsocket, fromaddr = bindsocket.accept()
            t = threading.Thread(target=deal_with_client, args=(newsocket, fromaddr))
            t.start()
            print('Done with client: ' + str(fromaddr))
        except KeyboardInterrupt:
            print('Program closing...')
            break

    bindsocket.close()



import select
import socket

connections = set()

def sending(message):
    for connection in connections:
        print(">Sending: %s" % message)
        connection.send(message)

sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sckt.bind(('0.0.0.0', 9999))
sckt.listen(10)

while True:
    readable, writable, errored = select.select([sckt] + list(connections), [], [])

    for connection in readable:
        if connection == sckt:
            print(">New connection")
            connection, address = sckt.accept()
            connections.add(connection)
        else:
            message = connection.recv(1024)
            if not message:
                print(">A connection has closed")
                connections.remove(connection)
            else:
                print(">Received: %s" % message)
                sending(message)

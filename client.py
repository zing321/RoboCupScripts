import socket

def send(ip,port,data):
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.send(data)
        response = sock.recv(1024)
        print response
        sock.close()
    except:
        print "There was an unexpected error!"

'''simple echo client
import socket

def run_client(host='127.0.0.1', port=7788):
    with socket.socket() as sock:
        sock.connect((host, port))
        for _ in range(10):
            data = input(">>")
            sock.sendall(data.encode())
            if data == 'bye':
                sock.close()
                break
            res = sock.recv(1024)
            print(res.decode())

if __name__ == '__main__':
    run_client()
'''
import socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.0.3', 30002))
while 1:
    data = client_socket.recv(1024).decode()
    if ( data == 'q' or data == 'Q'):
        client_socket.close()
        break;
    elif ( data == '[[0,0,0,0]]'):
        client_socket.close()
        break;
    else:
        print (data,type(data))
        #data = input ( "SEND( TYPE q or Q to Quit):" )
        if ( data == 'q' or data == 'Q'):
            #client_socket.send(data.encode())
            client_socket.close()
            break
        #else:
        #    client_socket.send(data.encode())
        #str to array
        recv_datas=eval(data)
        print(recv_datas,type(recv_datas))
        print("datas length =",len(recv_datas))
        if len(recv_datas)>0:
            print("recv_datas[0]=",recv_datas[0])
        else:
            print("none data")
#while end
print ("\n> socket colsed... END.")

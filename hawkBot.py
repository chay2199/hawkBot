import random
import socket
import select


IP = "127.0.0.1"
PORT = 8000

# Create a socket
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_ - socket option
# SOL_ - socket option level
# Sets REUSEADDR (as a socket option) to 1 on socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind, so server informs operating system that it's going to use given IP and port
# For a server using 0.0.0.0 means to listen on all available interfaces, useful to connect locally to 127.0.0.1 and remotely to LAN interface IP
server_socket.bind((IP, PORT))

# This makes server listen to new connections
server_socket.listen()

# List of sockets for select.select()
sockets_list = [server_socket]

# List of connected clients - socket as a key, user header and name as data
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

# basic knowledge base without any use of NLP
greetings = ['hola', 'hello', 'hi', 'Hi', 'hey!', 'hey']
random_greeting = random.choice(greetings)

goodbyes = ["Bye", "See you later", "Goodbye", "bye"]
random_goodbyes = random.choice(goodbyes)

timings = ["What hours are you open?", "What are your hours?", "When are you open?"]
timings_response = ["We're open every day 9am-9pm", "Our hours are 9am-9pm every day"]
random_timings = random.choice(timings_response)

who = ["What you guys do?", "What this company is about?"]
who_response = "We give advice about financial investment"

question = ['How are you?', 'How are you doing?']
question_response = ['Okay', "I'm fine"]
random_question = random.choice(question_response)


# Handles message receiving
def receive_message(client):
    return client.recv(1024)


while True:
    # Calls Unix select() system call or Windows select() WinSock call with three parameters:
    #   - rlist - sockets to be monitored for incoming data
    #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
    #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:

            # Accept new connection
            # That gives us new socket - client socket, connected to this given client only, it's unique for that client
            # The other returned object is ip/port set
            client_socket, client_address = server_socket.accept()

            # Client should send his name right away, receive it
            user = receive_message(client_socket)

            # If False - client disconnected before he sent his name
            if user is False:
                continue

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket)

            # Also save username and username header
            clients[client_socket] = user

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address,
                                                                            user.decode('utf-8')))

        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del clients[notified_socket]

                continue

            # Get user by notified socket, so we will know who sent the message
            user = clients[notified_socket]

            print(f'Received message from {user.decode("utf-8")}: {message.decode("utf-8")}')

            # Iterate over connected clients and broadcast message
            for client_socket in clients:
                if client_socket == notified_socket:
                    print(message)
                    if message.decode() in greetings:
                        client_socket.send(random_greeting.encode())
                    elif message.decode() in goodbyes:
                        client_socket.send(random_goodbyes.encode())
                    elif message.decode() in timings:
                        client_socket.send(random_timings.encode())
                    elif message.decode() in who:
                        client_socket.send(who_response.encode())
                    elif message.decode() in question:
                        client_socket.send(random_question.encode())
                    else:
                        client_socket.send("I did not understand what you said, Please contact FinHawk "
                                           "headquarters!".encode())

    for notified_socket in exception_sockets:
        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]

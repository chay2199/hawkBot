import socket
import errno
import sys
import time

IP = "127.0.0.1"
PORT = 8000
my_username = input("Username: ")

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
client_socket.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
client_socket.setblocking(False)

# Prepare username and header and send them
# We need to encode username to bytes
username = my_username.encode('utf-8')
client_socket.send(username)
while True:

    # Wait for user to input a message
    message = input(f'{my_username} > ')
    # If message is not empty - send it
    if message:
        # Encode message to bytes
        message = message.encode('utf-8')
        client_socket.send(message)
        # Sleep so that message is received on time
        time.sleep(0.0005)

    try:
        # Now we want to loop over received messages (there might be more than one) and print them
        while True:
            recv_message = client_socket.recv(1024).decode('utf-8')
            if not len(recv_message):
                break
            print(f'HawkBot > {recv_message}')
    except IOError as e:
        # This is normal on non blocking connections - when there are no incoming data error is going to be raised
        # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
        # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
        # If we got different error code - something happened
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        continue

    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error: '.format(str(e)))
        sys.exit()

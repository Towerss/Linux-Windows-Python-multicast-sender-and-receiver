"""
    Tested working on Python 2.7, for Linux Debian 8 and Windows 10
    
    Open browser functionality only available for Windows

    MCAST_GRP is a dotted string format of the multicast group
    MCAST_PORT is an integer of the UDP port you want to receive
    if_ip is a dotted string format of the IP of the interface you will use.
    
"""
from socket import *
from subprocess import *
import subprocess
import platform
import os

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
if_ip = ""
message = ''
current_ip = ''


def determine_os():
    if os.name == "nt":
        return str(os.name)

    elif os.name == "posix":

        return str(os.name)

    else:
        return "Operative system not supported"


def receive_multicast_for_windows(if_ip):

    def join_multicast(MCAST_GRP, MCAST_PORT, if_ip):

        global message

        # create a UDP socket
        mcastsock = socket(AF_INET, SOCK_DGRAM)

        # allow other sockets to bind this port too
        mcastsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        # explicitly join the multicast group on the interface specified
        mcastsock.setsockopt(SOL_IP, IP_ADD_MEMBERSHIP, inet_aton(MCAST_GRP) + inet_aton(if_ip))

        # finally bind the socket to start getting data into your socket
        mcastsock.bind(('', MCAST_PORT))

        # Returns a live multicast socket
        return mcastsock

    print("Waiting for Messages...")

    while True:
        message = str(join_multicast(MCAST_GRP, MCAST_PORT, if_ip).recv(1024).decode('utf8'))
        process_message(message)


def receive_multicast_for_linux(if_ip):

    def join_multicast(MCAST_GRP, MCAST_PORT, if_ip):

        global message

        # create a UDP socket
        mcastsock = socket(AF_INET, SOCK_DGRAM)

        # allow other sockets to bind this port too
        mcastsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        # explicitly join the multicast group on the interface specified
        mcastsock.setsockopt(SOL_IP, IP_ADD_MEMBERSHIP, inet_aton(MCAST_GRP) + inet_aton(if_ip))

        # finally bind the socket to start getting data into your socket
        mcastsock.bind(('', MCAST_PORT))

        # Returns a live multicast socket
        return mcastsock

    print("Waiting for Messages...")

    while True:
        message = str(join_multicast(MCAST_GRP, MCAST_PORT, if_ip).recv(1024).decode('utf8'))
        process_message(message)


def get_local_wireless_ip_linux():
    import fcntl
    import struct
    import socket
    ifname = 'wlan0'
    s = socket.socket(AF_INET, SOCK_DGRAM)
    IP = (socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24]))
    return IP


def get_local_wireless_ip_windows():
  import subprocess
  arp = subprocess.check_output('arp -a')
  my_ip = []
  for line in arp.split('\n'):
    if 'Interface' in line:
      my_ip.append(line.split(':')[1].split('---')[0].strip())
  return my_ip[-1]


def process_message(message):

    global current_ip

    if determine_os() == "nt":
        # Handles incoming message
        temp_message = message.split(':')
        keys = []

        for key in temp_message:
            keys.append(key.strip(";\n"))
        if keys[0] == "NIP":
            current_ip = str(keys[1])
            open_browser()
            print("NIP received: " + keys[1])
        elif keys[0] == "CIP":
            if current_ip != str(keys[1]):
                current_ip = str(keys[1])
                open_browser()
            print("CIP received: " + keys[1])
        elif keys[0] == "UIP":
            current_ip = str(keys[1])
            open_browser()
            print("UIP received: " + keys[1])

    elif os.name == "posix":

        print(message)

    else:
        return "Operative system not supported. Message not processed"


def open_browser():

    global current_ip

    #Takes the received IP and opens it

    url = current_ip + "/api/"

    command = "cmd /c start chrome " + url + " --new-window"
    subprocess.Popen(command, shell=True)


def main():
    if determine_os() == "nt":
        receive_multicast_for_windows(get_local_wireless_ip_windows())

    elif determine_os() == "posix":
        receive_multicast_for_linux(get_local_wireless_ip_linux())


main()

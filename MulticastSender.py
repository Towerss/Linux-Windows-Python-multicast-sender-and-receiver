#!/usr/bin/env python
"""

Program to send multicast messages using the wireless interface in Linux and Windows

In Linux it is required to execute the program with SU or SUDO privileges.

Tested working with Python 2.7 in Linux Debian 8 and Windows 10!!

"""

import socket
import platform
import os
import time

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
in_use_ip = ''
current_ip = ''
temp_ip = ''
message = ''
count = 0


def determine_os():
    if os.name == "nt":
        return str(os.name)

    elif os.name == "posix":

        return str(os.name)

    else:
        return "Operative system not supported"


def get_local_wireless_ip_linux():
    import fcntl
    import struct
    import socket
    ifname = 'wlan0'
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    wlan0_ip = (socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24]))
    return wlan0_ip


def get_local_wireless_ip_windows():
    import subprocess
    arp = subprocess.check_output('arp -a')
    local_ipv4 = []
    for line in arp.split('\n'):
        if 'Interface' in line:
            local_ipv4.append(line.split(':')[1].split('---')[0].strip())
    return local_ipv4[-1]

def send_multicast_for_linux(MCAST_GRP, MCAST_PORT, if_ip):
    # create a UDP socket
    mcastsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # allow other sockets to bind this port too
    mcastsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the wireless device. Could be eth0 for LAN
    mcastsock.setsockopt(socket.SOL_SOCKET, 25, "wlan0" + '\0')

    # explicitly join the multicast group on the interface specified
    mcastsock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MCAST_GRP) + socket.inet_aton(if_ip))

    # finally bind the socket to start getting data into your socket
    mcastsock.bind((MCAST_GRP, MCAST_PORT))

    # Returns a live multicast socket
    return mcastsock

def send_multicast_for_windows(MCAST_GRP, MCAST_PORT, if_ip):

    # create a UDP socket
    mcastsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # allow other sockets to bind this port too
    mcastsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # explicitly join the multicast group on the interface specified
    mcastsock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MCAST_GRP) + socket.inet_aton(if_ip))

    # finally bind the socket to start getting data into your socket
    mcastsock.bind(('', MCAST_PORT))

    # Returns a live multicast socket
    return mcastsock


def main():

    global in_use_ip
    global temp_ip
    global message

    # time.sleep(60)

    while 1:

        #Try to discover the current Wireless associated IP when started
        if in_use_ip == '':

            if determine_os() == "nt":
                in_use_ip = get_local_wireless_ip_windows()
                message = "NIP:"
                message = message + in_use_ip
                send_multicast_for_windows(MCAST_GRP, MCAST_PORT, get_local_wireless_ip_windows()).sendto(message, (MCAST_GRP, MCAST_PORT))
                print("Multicast windows new IP sent: " + message)
                time.sleep(2)

            elif determine_os() == "posix":
                print(os.name)
                in_use_ip = get_local_wireless_ip_linux()
                message = "NIP:"
                message = message + in_use_ip
                send_multicast_for_linux(MCAST_GRP, MCAST_PORT, get_local_wireless_ip_linux()).sendto(message, (MCAST_GRP, MCAST_PORT))
                print("Multicast linux new IP sent: " + message)
                time.sleep(2)

        else:
            #Check the current associated Wireless IP address
            if determine_os() == "nt":
                temp_ip = get_local_wireless_ip_windows()

            elif determine_os() == "posix":
                temp_ip = get_local_wireless_ip_linux()

            #Check if the stored Wireless IP is the same as the current associated Wireless IP address
            if in_use_ip == temp_ip:

                if determine_os() == "nt":
                    message = "CIP:"
                    message = message + in_use_ip
                    send_multicast_for_windows(MCAST_GRP, MCAST_PORT, get_local_wireless_ip_windows()).sendto(message, (
                    MCAST_GRP, MCAST_PORT))
                    print("Multicast windows current IP sent: " + message)
                    time.sleep(2)

                elif determine_os() == "posix":
                    message = "CIP:"
                    message = message + in_use_ip
                    send_multicast_for_linux(MCAST_GRP, MCAST_PORT, get_local_wireless_ip_linux()).sendto(message, (
                    MCAST_GRP, MCAST_PORT))
                    print("Multicast linux current IP sent: " + message)
                    time.sleep(2)

            else:
                #If there is a change in the stored Wireless IP, get a new one and  multicast it.
                if determine_os() == "nt":
                    in_use_ip = get_local_wireless_ip_windows()
                    message = "UIP:"
                    message = message + in_use_ip
                    send_multicast_for_windows(MCAST_GRP, MCAST_PORT, get_local_wireless_ip_windows()).sendto(message, (MCAST_GRP, MCAST_PORT))
                    print("Multicast windows updated IP sent: " + message)
                    time.sleep(2)

                elif determine_os() == "posix":
                    in_use_ip = get_local_wireless_ip_linux()
                    message = "UIP:"
                    message = message + in_use_ip
                    send_multicast_for_linux(MCAST_GRP, MCAST_PORT, get_local_wireless_ip_linux()).sendto(message, (MCAST_GRP, MCAST_PORT))
                    print("Multicast linux updated IP sent: " + message)
                    time.sleep(2)

main()
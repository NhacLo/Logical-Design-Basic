import socket
import time

class ControlBrakeVehicle:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 5005
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # send to jetson
        self.sock_brake_host = '192.168.100.10'
        self.sock_brake_port = 5006
        self.sock_brake = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    def reset(self):
        message = 0x02
        self.sock.sendto(bytes([message]), (self.host, self.port))
        self.sock_brake.sendto(bytes([message]), (self.sock_brake_host, self.sock_brake_port))
        print("Sent RESET command")
    def brake_on(self):
        message = 0x01
        self.sock.sendto(bytes([message]), (self.host, self.port))
        self.sock_brake.sendto(bytes([message]), (self.sock_brake_host, self.sock_brake_port))
        print("Sent BRAKE_ON command")
    def brake_off(self):
        message = 0x00
        self.sock.sendto(bytes([message]), (self.host, self.port))
        self.sock_brake.sendto(bytes([message]), (self.sock_brake_host, self.sock_brake_port))
        print("Sent BRAKE_OFF command")

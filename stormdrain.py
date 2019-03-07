#!/usr/bin/env python3.7

import socket
import struct
import threading
import time
import math

class Packet:
    pack_id = 0
    def __init__(self, water, size, cust):
        self.water = water
        self.size = size
        self.cust = cust
        self.raw = list()
        self.m_water = list()
        self.m_trash = set()
        self.m_merc = set()
        Packet.pack_id += 1

    def __str__(self):
        index = 1
        my_str = "Packet: {}\nType: {}\nSize: {}\nCust: {}\n".format(
                Packet.pack_id, self.water, self.size, self.cust)
        my_str += "-----RAW-----\n"
        for molecule in self.raw:
            my_str += "{}: ".format(index)
            index += 1
            my_str += molecule.__str__()
        my_str += "----Trash----\n"
        for molecule in self.m_trash:
            my_str += "{}: ".format(index)
            index += 1
            my_str += molecule.__str__()
        my_str += "----Haz----\n"
        for molecule in self.m_merc:
            my_str += "{}: ".format(index)
            index += 1
            my_str += molecule.__str__()
        return my_str

    def hex(self, moles, payload):
        my_hex = "{:04x}{:04x}{:08x}".format(self.water, self.size, self.cust)
        if payload == "water":
            for molecule in moles:
                my_hex += "{:08x}{:04x}{:04x}".format(
                        molecule.data, molecule.left_index, molecule.right_index)
        if payload == "hazmat":
            for molecule in moles:
                my_hex += "{:08x}".format(
                        molecule.data)
        return my_hex

    def print_chain(self):
        for molecule in self.raw:
            if molecule.data != 0:
                if(molecule.left_index <= len(self.raw)):
                    print("Left id: ", self.raw[molecule.left_index])
                if(molecule.right_index <= len(self.raw)):
                    print("Right id: ", self.raw[molecule.right_index])

    def demap(self):
        for molecule in list(self.raw):
            if molecule.data != 0:
                if 0 <= molecule.left_index <= len(self.raw):
                    molecule.left_index = self.raw[molecule.left_index - 1].data
                else:
                    self.m_trash.add(molecule)
                    molecule.left_index = 0
                #print(molecule)
                if 0 <= molecule.right_index <= len(self.raw):
                    molecule.right_index = self.raw[molecule.right_index - 1].data
                else:
                    self.m_trash.add(molecule)
                    molecule.right_index = 0
                if molecule.left_index == molecule.right_index == 0:
                    self.m_merc.add(molecule)
            #print(molecule)
            if molecule.data == 0:
                self.raw.remove(molecule)
        for molecule in self.m_trash:
            print(molecule)
            for raw_mole in self.raw:
                if raw_mole.right_index == molecule.data:
                    raw_mole.right_index = 0
                if raw_mole.left_index == molecule.data:
                    raw_mole.left_index = 0
            self.raw.remove(molecule)
      #  for molecule in self.m_merc:
      #      print(molecule)
      #      for raw_mole in self.raw:
      #          if raw_mole.right_index == molecule.data:
      #              raw_mole.right_index = 0
      #          if raw_mole.left_index == molecule.data:
      #              raw_mole.left_index = 0
      #      self.raw.remove(molecule)


    def remap(self, moles):
        zero = list()
        final = list()
        for molecule in moles:
            if molecule.left_index == molecule.right_index == 0:
                zero.append(molecule)
            else:
                final.append(molecule)
        final += zero
        for mole in final:
            if mole.left_index != 0:
                for x in range(0, len(final)):
                    if final[x].data == mole.left_index:
                        mole.left_index = x + 1
            if mole.right_index != 0:
                for x in range(0, len(final)):
                    if final[x].data == mole.right_index:
                        mole.right_index = x + 1
        self.raw = final
        self.raw = self.airate(self.raw)

    def state(self):
        air = 0
        for molecule in self.raw:
            if molecule.left_index == molecule.right_index == 0:
                air += 1
        if air == len(self.raw):
            return 0

    def airate(self, moles):
        last = len(moles)
        air_to_add = math.ceil(last * .03)
        print("Air to add: ", air_to_add)
        for x in range(0, air_to_add):
            moles.append(Molecule(0, 0, last))
        return moles

    def resize(self, moles, payload):
        if payload == "water":
            self.size = (len(moles) + 1) * 8
        elif payload == "hazmat":
            self.size = (len(moles) * 4) + 8





class Molecule:
    mole_id = 1
    def __init__(self, data, left_index, right_index):
        self.data = data
        self.left_index = left_index
        self.right_index = right_index
        self.chem = self.identify()
        self.mole = Molecule.mole_id
        if data != 0:
            Molecule.mole_id += 1

    def __str__(self):
        my_str = "{} <-- Data: {} --> {}\n".format(self.left_index, self.data, self.right_index)
        return my_str

    def full_info(self):
        my_str = "Data: {} LI: {} RI: {}\n".format(self.data, self.left_index, self.right_index)
        return my_str

    def identify(self):
        if self.data == 0:   # Air
            return 0
        elif self.right_index == self.left_index:
            return 1    # Chlorine



HOST= '127.0.0.1'
TCP = socket.SOCK_STREAM
UDP = socket.SOCK_DGRAM

connections = [[1111, TCP], [1111, UDP], [3333, TCP], [3333, UDP],
        [5555, TCP], [5555, UDP], [7777, TCP], [7777,UDP]]
DSTREAM = '10.40.7.151'
PACKETS = list()

def listen(port, conn_type):
    my_sock = socket.socket(socket.AF_INET, conn_type)
    my_sock.bind(("", port))
    if conn_type is UDP:
        while True:
            data, host = my_sock.recvfrom(4096)
            if not data:
                break
            #print(bytes(data))
            w_type = int.from_bytes(data[:2], byteorder="big")
            w_size = int.from_bytes(data[2:4], byteorder="big")
            w_cust = int.from_bytes(data[4:8], byteorder="big")
            #print(f"TEST: {w_type} {w_size} {w_cust}")
            p = Packet(w_type, w_size, w_cust)
            #handle_water(my_sock, data, UDP)
            if p.water == 0:
                #print("Num of moles: {}".format((int(w_size-8) / 8)+ 1))
                index = 8
                num_p = int((w_size - 8) / 8) + 1
                water_count = 0
                trash_count = 0
                air_count = 0
                for x in range(0, num_p):
                    m_data = int.from_bytes(data[index:index + 4], byteorder="big")
                    index += 4
                    m_left_index = int.from_bytes(data[index:index + 2], byteorder="big")
                    index += 2
                    m_right_index = int.from_bytes(data[index:index + 2], byteorder="big")
                    index += 2
                    #print(f"TEST: id:{m_data} {m_left_index} {m_right_index}")
                    if(m_left_index == 0 and m_right_index == 0):
                        air_count += 1
                    if(m_left_index > num_p or m_right_index > num_p):
                        trash_count += 1
                    else:
                        water_count += 1
                    p.raw.append(Molecule(m_data, m_left_index, m_right_index))
            print("wastewater")
            p.demap()
            print(p)
            p.resize(p.raw, "water")
            p.remap(p.raw)
            print(p)
            data = bytes.fromhex(p.hex(p.raw, "water"))
            handle_water(my_sock, data, UDP, 1111)
            if p.m_trash:
                p.resize(p.m_trash, "water")
                p.remap(p.m_trash)
                p.water = 1
                data = bytes.fromhex(p.hex(p.m_trash, "water"))
                handle_water(my_sock, data, UDP, 2222)
            if p.m_merc:
                p.resize(p.m_merc, "hazmat")
                p.remap(p.m_merc)
                p.water = 4
                data = bytes.fromhex(p.hex(p.m_merc, "hazmat"))
                handle_water(my_sock, data, UDP, 8888)



    else:
        while True:
            my_sock.listen()
            c, addr = my_sock.accept()
            while True:
                data = c.recv(1024)
                if not data:
                    break
                print(data)
                w_type = int.from_bytes(data[:2], byteorder="big")
                w_size = int.from_bytes(data[2:4], byteorder="big")
                w_cust = int.from_bytes(data[4:8], byteorder="big")
                p = Packet(w_type, w_size, w_cust)
                #print(f"TEST: {w_type} {w_size} {w_cust}")
                #PACKETS.append(Packet(w_type, w_size, w_cust))
                if p.water == 0:
                    index = 8
                    num_p = int((w_size - 8) / 8) + 1
                    water_count = 0
                    trash_count = 0
                    air_count = 0
                    for x in range(0, num_p):
                        m_data = int.from_bytes(data[index:index + 4], byteorder="big")
                        index += 4
                        m_left_index = int.from_bytes(data[index:index + 2], byteorder="big")
                        index += 2
                        m_right_index = int.from_bytes(data[index:index + 2], byteorder="big")
                        index += 2
                        #print(f"TEST: id:{m_data} {m_left_index} {m_right_index}")
                        if(m_left_index == 0 and m_right_index == 0):
                            air_count += 1
                        if(m_left_index > num_p or m_right_index > num_p):
                            trash_count += 1
                        else:
                            water_count += 1
                        p.raw.append(Molecule(m_data, m_left_index, m_right_index))
                print("wastewater")
                p.demap()
                p.resize(p.raw, "water")
                p.remap(p.raw)
                print(p)
                #print(p.hex(p.raw))
                print("After")
                print(p)
                data = bytes.fromhex(p.hex(p.raw, "water"))
                handle_water(my_sock, data, TCP, 1111)
                if p.m_trash:
                    p.resize(p.m_trash, "water")
                    p.remap(p.m_trash)
                    p.water = 1
                    data = bytes.fromhex(p.hex(p.m_trash, "water"))
                    handle_water(my_sock, data, TCP, 2222)
                if p.m_merc:
                    p.resize(p.m_merc, "hazmat")
                    p.remap(p.m_merc)
                    p.water = 4
                    data = bytes.fromhex(p.hex(p.m_merc, "hazmat"))
                    handle_water(my_sock, data, TCP, 8888)
                #c.send(data)
                #handle_water(c, data, TCP)
        c.close()


def handle_water(sock, water, conn_type, port):
    if conn_type is UDP:
        sock.sendto(water, (DSTREAM, port))
    else:
        downstream = socket.socket()
        downstream.connect((DSTREAM, port))
        downstream.send(water)
        downstream.close()
        #sock.send(water)


def main():
    threads = list()
    for i, conn in enumerate(connections):
        print("Starting thread: ", conn[0], conn[1])
        threads.append(threading.Thread(target=listen, args=(conn[0], conn[1],)))
        threads[i].start()


if __name__ == "__main__":
    main()

#with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
#    s.bind((HOST, PORT))
#    while True:
#        data, port = s.recvfrom(1024)
#        if not data:
#j            break
 #       print(data, port)
        #s.sendto(data, (DSTREAM, PORT))
        #h_type, h_size, h_cust = struct.unpack('bbb', data)
        #print("Type:", h_type)
        #print("Size:", h_size)
        #print("Custom:", h_cust)

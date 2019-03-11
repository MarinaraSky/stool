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
        self.unknown = list()
        self.m_water = list()
        self.m_trash = set()
        self.m_merc = set()
        self.sludge = set()
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
        my_str += "----Sludge----\n"
        for molecule in self.sludge:
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

    def print_chain(self, moles):
        my_str = ""
        index = 1
        for molecule in moles:
            my_str += "{}: ".format(index)
            index += 1
            my_str += molecule.__str__()
        return my_str


    def demap(self):
        for molecule in list(self.raw):
            print("RAW: ", molecule)
            if molecule.data != 0:
                if molecule.chem == 4:
                    print("SLUDGE")
                    self.sludge.add(molecule)
                    continue
                if 0 <= molecule.left_index <= len(self.raw):
                    molecule.left_index = self.raw[molecule.left_index - 1].data
                else:
                    print("Trash->", molecule)
                    molecule.chem = 3
                    self.m_trash.add(molecule)
                    #self.raw.remove(molecule)
                    molecule.left_index = 0
                #print(molecule)
                if 0 <= molecule.right_index <= len(self.raw):
                    molecule.right_index = self.raw[molecule.right_index - 1].data
                else:
                    print("Trash-<", molecule)
                    molecule.chem = 3
                    self.m_trash.add(molecule)
                    #self.raw.remove(molecule)
                    molecule.right_index = 0
        self.clean()
        for molecule in self.raw:
            touched = list()
            print("Test: ", molecule.data)
            left = molecule.left_index
            right = molecule.right_index
            for mole in self.raw:
                if molecule.data != mole.data:
                    if left == mole.left_index and left != 0:
                        touched.append(left)
                    if right == mole.right_index and right != 0:
                        touched.append(right)
            if len(touched) != len(set(touched)):
                self.m_merc.union(self.raw)
                self.raw = list()

    def clean(self):
        clean = False
        while not clean:
            for molecule in list(self.raw):
                if molecule.right_index == molecule.data:
                    molecule.chem = 2
                if molecule.left_index == molecule.data:
                    molecule.chem = 2
                if molecule.data == 0:
                    self.raw.remove(molecule)
            for molecule in self.raw:
                if molecule.chem == 3: # trash
                    self.m_trash.add(molecule)
                    #self.raw.remove(molecule)
                    for raw_mole in self.raw:
                        if raw_mole.right_index == molecule.data:
                            raw_mole.right_index = 0
                        if raw_mole.left_index == molecule.data:
                            raw_mole.left_index = 0
                    #self.raw.remove(molecule)
                elif molecule.chem == 2: #haz
                    self.m_merc.add(molecule)
                    #self.raw.remove(molecule)
                    for raw_mole in self.raw:
                        if raw_mole.right_index == molecule.data:
                            raw_mole.right_index = 0
                        if raw_mole.left_index == molecule.data:
                            raw_mole.left_index = 0
                self.raw = list(set(self.raw).difference(self.m_trash))
                self.raw = list(set(self.raw).difference(self.m_merc))
                self.raw = list(set(self.raw).difference(self.sludge))
            self.print_chain(self.raw)
            touched = list()
            for molecule in self.raw:
                links = list()
                if molecule.data == 0:
                    continue
                if molecule.chem == 1:
                    continue
                if molecule.right_index != 0:
                    curr = None
                    loop = True
                    while loop == True:
                        print("right")
                        if molecule.right_index != 0:
                            index = None
                            for i, mole in enumerate(self.raw):
                                if mole.data == molecule.right_index:
                                    index = i
                            if self.raw[i] not in links:
                                links.append(self.raw[i])
                                curr = links[-1]
                            else:
                                loop = False
                        if molecule.left_index != 0:
                            index = None
                            for i, mole in enumerate(self.raw):
                                if mole.data == molecule.right_index:
                                    index = i
                            if self.raw[i] not in links:
                                links.append(self.raw[i])
                                curr = links[-1]
                            else:
                                loop = False
                        else:
                            loop = False
                if molecule.left_index != 0:
                    curr = None
                    loop = True
                    while loop == True:
                        print("left")
                        if molecule.right_index != 0:
                            index = None
                            for i, mole in enumerate(self.raw):
                                if mole.data == molecule.right_index:
                                    index = i
                            if self.raw[i] not in links:
                                links.append(self.raw[i])
                                curr = links[-1]
                            else:
                                loop = False
                        if molecule.left_index != 0:
                            index = None
                            for i, mole in enumerate(self.raw):
                                if mole.data == molecule.left_index:
                                    index = i
                            if self.raw[i] not in links:
                                links.append(self.raw[i])
                                curr = links[-1]
                            else:
                                loop = False
                        else:
                            loop = False
                print("====Chain====")
                for molecule in links:
                    print(molecule)
                if links:
                    self.m_water.append(molecule)
                else:
                    self.m_merc.add(molecule)
                touched + links
            self.m_merc.union(set(self.raw).difference(touched))
            self.raw = list(set(self.raw).difference(self.m_merc))
            clean = True


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
        for mole in self.raw:
            if mole.left_index > len(self.raw):
                mole.left_index = 0
            if mole.right_index > len(self.raw):
                mole.right_index = 0
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
            moles.append(Molecule(0, 0, last, last))
        return moles

    def resize(self, moles, payload):
        if payload == "water":
            self.size = (len(moles) + 1) * 8
        elif payload == "hazmat":
            self.size = (len(moles) * 4) + 8





class Molecule:
    mole_id = 1
    def __init__(self, data, left_index, right_index, num):
        self.data = data
        self.left_index = left_index
        self.right_index = right_index
        self.chem = self.identify(num)
        self.mole = Molecule.mole_id
        if data != 0:
            Molecule.mole_id += 1

    def __str__(self):
        my_str = "{} <-- Data: {}({}) --> {}\n".format(self.left_index, self.data, self.chem, self.right_index)
        return my_str

    def full_info(self):
        my_str = "Data: {} LI: {} RI: {}\n".format(self.data, self.left_index, self.right_index)
        return my_str

    def identify(self, num):
        if self.data == 0:   # Air
            return 0
        elif self.undulating() == True:
            return 4    #Ammonia/Feces
        elif self.right_index >= num:
            return 3    # trash
        elif self.left_index >= num:
            return 3    # trash
        elif self.right_index == self.left_index == 0:
            return 2    # Haz
        elif self.right_index == self.left_index:
            return 1    # Chlorine
        else:
            return 99

    def is_prime(self):
        num = int(self.data)
        if num == 1:
            return False
        i = 2

        while i*i <= num:
            if num % i == 0:
                return False
            i += 1
        return True

    def undulating(self):
        GLG = False
        LGL = False
        turn = False
        num_str = str(self.data)
        print("Inside: ", self.data)
        if self.is_prime() == True:
            print("prime")
            return True
        for i in range(1, len(num_str)):
            if i == 1:
                if num_str[i] > num_str[i-1]:
                    LGL = True
                elif num_str[i] < num_str[i-1]:
                    GLG = True
                else:
                    return False
            if GLG == True:
                print("GLG")
                if turn == True:
                    if num_str[i] > num_str[i-1]:
                        turn ^= 1
                    else:
                        return False
                else:
                    if num_str[i] < num_str[i-1]:
                        turn ^= 1
                    else:
                        return False
            if LGL == True:
                print("LGL")
                if turn == True:
                    print("Comparing2: ", num_str[i], "-", num_str[i-1])
                    if num_str[i] < num_str[i-1]:
                        turn ^= 1
                    else:
                        return False
                else:
                    print("Comparing3: ", num_str[i], "-", num_str[i-1])
                    if num_str[i] > num_str[i-1]:
                        turn ^= 1
                    else:
                        return False
        return True




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
            w_type = int.from_bytes(
                    data[:2], byteorder="big")
            w_size = int.from_bytes(
                    data[2:4], byteorder="big")
            w_cust = int.from_bytes(
                    data[4:8], byteorder="big")
            p = Packet(w_type, w_size, w_cust)
            if p.water == 0:
                index = 8
                num_p = int((w_size - 8) / 8) + 1
                water_count = 0
                trash_count = 0
                air_count = 0
                for x in range(0, num_p):
                    m_data = int.from_bytes(
                            data[index:index + 4],
                            byteorder="big")
                    index += 4
                    m_left_index = int.from_bytes(
                            data[index:index + 2],
                            byteorder="big")
                    index += 2
                    m_right_index = int.from_bytes(
                            data[index:index + 2],
                            byteorder="big")
                    index += 2
                    if(m_left_index == 0 and m_right_index == 0):
                        air_count += 1
                    if(m_left_index > num_p or m_right_index > num_p):
                        trash_count += 1
                    else:
                        water_count += 1
                    p.raw.append(
                            Molecule(m_data, m_left_index,
                                m_right_index, num_p))
            print("wastewater")
            p.demap()
            #print(p)
            if p.raw:
                p.remap(p.raw)
                p.resize(p.raw, "water")
                #print(p)
                print("====FRESH====")
                print(p.print_chain(p.raw))
                data = bytes.fromhex(p.hex(p.raw, "water"))
                handle_water(my_sock, data, UDP, 1111)
            if p.m_trash:
                p.remap(p.m_trash)
                p.resize(p.m_trash, "water")
                p.water = 1
                print("====TRASH====")
                print(p.print_chain(p.m_trash))
                data = bytes.fromhex(p.hex(p.m_trash, "water"))
                handle_water(my_sock, data, UDP, 2222)
            if p.m_merc:
                p.remap(p.m_merc)
                p.resize(p.m_merc, "hazmat")
                p.water = 4
                print("====HAZMAT====")
                print(p.print_chain(p.m_merc))
                data = bytes.fromhex(p.hex(p.m_merc, "hazmat"))
                handle_water(my_sock, data, UDP, 8888)
            if p.sludge:
                p.remap(p.sludge)
                p.resize(p.sludge, "water")
                p.water = 8
                print("====SLUDGE====")
                print(p.print_chain(p.sludge))
                data = bytes.fromhex(p.hex(p.sludge, "hazmat"))
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
                        m_data = int.from_bytes(
                                data[index:index + 4],
                                byteorder="big")
                        index += 4
                        m_left_index = int.from_bytes(
                                data[index:index + 2],
                                byteorder="big")
                        index += 2
                        m_right_index = int.from_bytes(
                                data[index:index + 2],
                                byteorder="big")
                        index += 2
                        if(m_left_index == 0 and m_right_index == 0):
                            air_count += 1
                        if(m_left_index > num_p or m_right_index > num_p):
                            trash_count += 1
                        else:
                            water_count += 1
                        p.raw.append(
                                Molecule(m_data, m_left_index,
                                    m_right_index, num_p))
                print("wastewater")
                p.demap()
                #print(p)
                if p.raw:
                    p.remap(p.raw)
                    p.resize(p.raw, "water")
                    #print(p)
                    print("====FRESH====")
                    print(p.print_chain(p.raw))
                    data = bytes.fromhex(p.hex(p.raw, "water"))
                    handle_water(my_sock, data, TCP, 1111)
                if p.m_trash:
                    p.remap(p.m_trash)
                    p.resize(p.m_trash, "water")
                    p.water = 1
                    print("====TRASH====")
                    print(p.print_chain(p.m_trash))
                    data = bytes.fromhex(p.hex(p.m_trash, "water"))
                    handle_water(my_sock, data, TCP, 2222)
                if p.m_merc:
                    p.remap(p.m_merc)
                    p.resize(p.m_merc, "hazmat")
                    p.water = 4
                    print("====HAZMAT====")
                    print(p.print_chain(p.m_merc))
                    data = bytes.fromhex(p.hex(p.m_merc, "hazmat"))
                    handle_water(my_sock, data, TCP, 8888)
                if p.sludge:
                    p.remap(p.sludge)
                    p.resize(p.sludge, "hazmat")
                    p.water = 8
                    print("====SLUDGE====")
                    print(p.print_chain(p.sludge))
                    data = bytes.fromhex(p.hex(p.sludge, "hazmat"))
                    downstream = socket.socket()
                    downstream.connect(("10.40.7.1", 9001))
                    downstream.send(data)
                    downstream.close()
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

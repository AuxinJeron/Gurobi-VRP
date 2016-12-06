from collections import deque
from os import path
from VRPModel import Locker
from VRPModel import Deliver
import logging

KEYWORDS = {'NAME', 'COMMENT', 'TYPE', 'DIMENSION', 'EDGE_WEIGHT_TYPE',
            'CAPACITY', 'NODE_COORD_SECTION', 'DEMAND_SECTION', 'DEPOT_SECTION',
            'LOCKER_SECTION', 'DELIVER_SECTION', 'DEMAND_SECTION'}

logger = logging.getLogger("logger")


class TsplibParser :
    def __init__(self) :
        self.file_path = ""
        # attribute for the tsp file
        self.name = ""
        self.comment = ""
        self.type = ""
        self.dimension = 0
        self.edge_weight_type = ""
        self.capacity = 10
        self.cities_coord = []
        self.lockers = []
        self.delivers = []
        self.demands = []

    def reset(self) :
        self.__init__()

    def scan_keywords(self, file) :
        # mark whether enter NODE_COORD_SECTION
        node_coord_section = False
        locker_section = False
        deliver_section = False
        demand_section = False

        for line in file :
            words = deque(line.split())
            keyword = words.popleft().strip(": ")

            # meet next keyword, exit from node_coord_section
            if node_coord_section and keyword in KEYWORDS:
                node_coord_section = False
            if locker_section and keyword in KEYWORDS:
                locker_section = False
            if deliver_section and keyword in KEYWORDS:
                deliver_section = False
            if demand_section and keyword in KEYWORDS:
                demand_section = False

            if keyword == "COMMENT":
                self.comment = " ".join(words).strip(": ")
            elif keyword == "NAME":
                self.name = " ".join(words).strip(": ")
            elif keyword == "TYPE":
                self.type = " ".join(words).strip(": ")
            elif keyword == "DIMENSION":
                self.dimension = int(" ".join(words).strip(": "))
                self.cities_coord = [[0, 0]] * (self.dimension + 1)
            elif keyword == "EDGE_WEIGHT_TYPE" :
                self.edge_weight_type = " ".join(words).strip(": ")
            elif keyword == "CAPACITY":
                self.capacity = int(" ".join(words).strip(": "))
            elif keyword == "NODE_COORD_SECTION":
                node_coord_section = True
            elif keyword == "LOCKER_SECTION":
                locker_section = True
            elif keyword == "DELIVER_SECTION":
                deliver_section = True
            elif keyword == "DEMAND_SECTION":
                demand_section = True
            else :
                if node_coord_section:
                    self.scan_city_coord(line)
                elif locker_section:
                    self.scan_locker(line)
                elif deliver_section:
                    self.scan_deliver(line)
                elif demand_section:
                    self.scan_demand(line)

    def scan_city_coord(self, line):
        words = deque(line.split(" "))
        if len(words) != 3:
            return
        index = int(words[0])
        if index >= len(self.cities_coord):
            return
        self.cities_coord[index] = [int(words[1]), int(words[2])]

    def scan_locker(self, line):
        words = deque(line.split())
        if len(words) != 2:
            return
        locker_id = int(words[0])
        locker_pos = int(words[1]) - 1
        locker = Locker(locker_id, locker_pos)
        self.lockers.append(locker)

    def scan_deliver(self, line):
        words = deque(line.split())
        if len(words) != 4:
            return
        deliver_id = int(words[0])
        pos = int(words[1]) - 1
        max_distance = int(words[2])
        #max_distance = float('inf')
        max_capacity = int(words[3])
        #max_capacity = float('inf')
        deliver = Deliver(deliver_id, pos, max_distance, max_capacity)
        self.delivers.append(deliver)

    def scan_demand(self, line):
        words = deque(line.split())
        if len(words) != 2:
            return
        self.demands.append(int(words[1]))

    def read_file(self, file_path):
        self.file_path = path.relpath(file_path)
        file = open(file_path, 'r')
        self.scan_keywords(file)
        self.cities_coord = self.cities_coord[1:]

parser = TsplibParser()
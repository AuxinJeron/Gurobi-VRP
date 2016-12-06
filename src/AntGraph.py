from math import sqrt
from math import pow
from threading import Lock
from operator import itemgetter
import logging

logger = logging.getLogger("logger")


class AntGraph:
    def __init__(self, coord_mat, delta_mat=None, tau_mat=None):
        self.lock = Lock()

        self.build_nodes_mat(coord_mat)
        self.build_cand_list()

        if tau_mat is None:
            self.build_tau_mat()
        else:
            self.tau_mat = tau_mat

    def build_nodes_mat(self, coord_mat):
        self.nodes_num = len(coord_mat)
        self.visited = [False] * self.nodes_num
        self.nodes_mat = [[0 for i in range(0, self.nodes_num)] for i in range(0, self.nodes_num)]
        for i in range(0, self.nodes_num):
            for j in range(i, self.nodes_num):
                d = sqrt(pow((coord_mat[i][0] - coord_mat[j][0]), 2) + pow((coord_mat[i][1] - coord_mat[j][1]), 2))
                self.nodes_mat[i][j], self.nodes_mat[j][i] = d, d

        # print nodes_mat
        # for i in range(0, self.nodes_num):
        #      logger.debug(self.nodes_mat[i])

    def build_tau_mat(self):
        self.tau_mat = []
        self.tau0 = 1.0 / (self.nodes_num * self.nearest_neighbour_tour())
        #self.tau0 = 1.0
        for i in range(0, self.nodes_num):
            self.tau_mat.append([self.tau0] * self.nodes_num)

    def build_cand_list(self):
        self.cl = min(20, int(0.3 * self.nodes_num))
        self.cand_list = []
        for i in range(0, self.nodes_num):
            dict = {}
            for j in range(0, self.nodes_num):
                if i == j:
                    continue
                dict[j] = self.nodes_mat[i][j]
            nearest_neighbours = sorted(dict.items(), key=itemgetter(1))
            cands = set()
            for neighbour in nearest_neighbours:
                if len(cands) >= self.cl:
                    break
                if neighbour[0] != i:
                    cands.add(neighbour[0])
            self.cand_list.append(cands)

        # for i in range(0, len(self.cand_list)):
        #     logger.info(self.cand_list[i])

    def reset_tau(self):
        self.build_tau_mat()

    def nearest_neighbour_tour(self):
        L = 0
        nodes_to_visit = {}
        path_vec = []
        start_node = 0
        curr_node = start_node
        path_vec.append(start_node)
        path_mat = [[0 for i in range(0, self.nodes_num)] for i in range(0, self.nodes_num)]
        for i in range(0, self.nodes_num):
            if i != start_node:
                nodes_to_visit[i] = i

        # calculate the tour length
        while nodes_to_visit:
            nearest_len = float('inf')
            new_node = start_node
            for node in nodes_to_visit.values():
                if self.nodes_mat[curr_node][node] < nearest_len:
                    new_node = node
                    nearest_len = self.nodes_mat[curr_node][node]
            L += nearest_len
            path_vec.append(new_node)
            path_mat[curr_node][new_node] = '*'
            del nodes_to_visit[new_node]
            curr_node = new_node

        path_mat[path_vec[-1]][start_node] = '*'
        L += self.nodes_mat[path_vec[-1]][start_node]
        # for i in range(0, len(path_mat)):
        #     print(path_mat[i])
        return L

    def delta(self, r, s):
        return self.nodes_mat[r][s]

    def tau(self, r, s):
        return self.tau_mat[r][s]

    def etha(self, r, s):
        return 1.0 / self.delta(r, s)

    def update_tau(self, r, s, val):
        self.tau_mat[r][s] = val

    def print_tau(self):
        for i in range(0, len(self.tau_mat)):
            logger.info(self.tau_mat[i])
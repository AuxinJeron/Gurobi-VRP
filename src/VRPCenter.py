from gurobipy import *
from AntGraph import AntGraph
from TspPainter import tspPainter
from graphics import *
import itertools
import logging
import random

logger = logging.getLogger("logger")


class VRPCenter:
    def __init__(self, tspparser):
        self.build_graph(tspparser)

    def build_graph(self, tspparser):
        self.antGraph = AntGraph(tspparser.cities_coord)
        self.lockers = tspparser.lockers
        self.lockers_dict = {}
        self.delivers_dict = {}
        for locker in self.lockers:
            self.lockers_dict[locker.id] = locker
        self.delivers = tspparser.delivers
        for deliver in self.delivers:
            self.delivers_dict[deliver.id] = deliver
        self.demands = tspparser.demands

        self.build_nearest_locker()

    def build_nearest_locker(self):
        for deliver in self.delivers:
            deliver.locker_id = deliver.nearest_locker(self.lockers, self.antGraph.nodes_mat)
            locker = self.lockers_dict[deliver.locker_id]
            locker.delivers.append(deliver.id)

    # def start(self):
    #     antColony = AntColony(self.antGraph, self.lockers, self.lockers_dict, self.delivers, self.delivers_dict, self.demands, 10, 250)
    #     antColony.start()
    #
    #     best_path_routes = antColony.best_path_routes
    #     best_path_cost = antColony.best_path_cost
    #     logger.info("-------------------------------------------")
    #     logger.info("Problem optimization result")
    #     logger.info("-------------------------------------------")
    #     if best_path_routes != None:
    #         logger.info("Best path routes found  is")
    #         for key in best_path_routes.keys():
    #             logger.info("Deliver {} {}".format(key, best_path_routes[key]))
    #         logger.info("Locker scheme is")
    #         for locker in self.lockers:
    #             logger.info("Locker {} scheme: {}".format(locker.id, self.locker_scheme(locker, best_path_routes)))
    #         logger.info("cost : {}".format(best_path_cost))
    #         tspPainter.drawRoutes(best_path_routes)
    #     else:
    #         logger.info("Failed to path routes")
    #
    #     input("Press Enter to quit...")

    # Euclidean distance between two points

    def distance(self, i, j):
        return self.antGraph.delta(i, j)


    def start(self):
        model = Model("TSP")
        n = len(self.antGraph.nodes_mat)
        delivers_num = len(self.delivers)
        tspPainter.drawDeliver(self.delivers[0:delivers_num])
        # Create variables

        x = {}
        for i in range(n):
            for j in range(i+1):
                for k in range(delivers_num):
                    x[i, j, k] = model.addVar(vtype=GRB.BINARY, name='e' + str(i) + '_' + str(j) + '_' + str(k))
                    x[j, i, k] = x[i, j, k]
        model.update()

        obj = quicksum( self.distance(i,j) / 2 * x[i, j, k] for i in range(n) for j in range(n) for k in range(delivers_num) if i != j)
        model.setObjective(obj)

        # Add degree-2 constraint, and forbid loops

        degree = {}
        for k in range(delivers_num):
            for i in range(n):
                degree[i, k] = model.addVar(vtype=GRB.INTEGER, name='degree_' + str(i) + '_' + str(k), lb=0, ub=1)
        model.update()

        for i in range(n):
            for k in range(delivers_num):
                model.addConstr(quicksum(x[i, j, k] for j in range(n)) == 2 * degree[i,k])
                x[i, i, k].ub = 0
            model.addConstr(quicksum(degree[i, k] for k in range(delivers_num)) >= 1)
        # Callback - use lazy constraints to eliminate sub-tours

        def subtourelim(model, where):
            if where == GRB.callback.MIPSOL:
                # make a list of edges selected in the solution
                for k in range(delivers_num):
                    selected = []
                    visited = set()
                    for i in range(n):
                        sol = model.cbGetSolution([x[i, j, k] for j in range(n)])
                        new_selected = [(i, j) for j in range(n) if sol[j] > 0.5]
                        selected += new_selected

                        if new_selected:
                            visited.add(i)

                    # find the shortest cycle in the selected edge list
                    print str(k) + ' selected ' + str(len(selected)) + ' ' + repr(selected)
                    print str(k) + ' len visited ' + str(len(visited)) + ' ' + repr(visited)
                    tour = subtour(selected, visited)
                    print str(k) + ' len tour ' + str(len(tour)) + ' ' + repr(tour)

                    if len(tour) < len(visited):
                        # add a subtour elimination constraint
                        expr = quicksum(x[i, j, k] for i,j in itertools.combinations(tour, 2))
                        model.cbLazy(expr <= len(tour) - 1)

                    # must contain the start point
                    start_point = self.delivers[k].pos
                    if not start_point in visited:
                        model.cbLazy(degree[start_point, k] >= 1)

        # Given a list of edges, finds the shortest subtour

        # def subtour(edges):
        #     visited = [False] * n
        #     cycles = []
        #     lengths = []
        #     selected = [[] for i in range(n)]
        #     for x, y in edges:
        #         selected[x].append(y)
        #     while True:
        #         current = visited.index(False)
        #         thiscycle = [current]
        #         while True:
        #             visited[current] = True
        #             neighbors = [x for x in selected[current] if not visited[x]]
        #             if len(neighbors) == 0:
        #                 break
        #             current = neighbors[0]
        #             thiscycle.append(current)
        #         cycles.append(thiscycle)
        #         lengths.append(len(thiscycle))
        #         if sum(lengths) == n:
        #             break
        #     return cycles[lengths.index(min(lengths))]

        def subtour(edges, visited):
            unvisited = list(visited)
            cycle = range(len(visited) + 1)
            selected = {}
            for x,y in edges:
                selected[x] = []
            for x, y in edges:
                selected[x].append(y)
            print selected
            while unvisited:
                thiscycle = []
                neighbors = unvisited
                while neighbors:
                    current = neighbors[0]
                    thiscycle.append(current)
                    unvisited.remove(current)
                    print thiscycle
                    neighbors = [j for j in selected[current] if j in unvisited]
                if len(cycle) > len(thiscycle):
                    cycle = thiscycle
            return cycle

        # Optimize model

        model.params.LazyConstraints = 1
        model.optimize(subtourelim)

        solution = model.getAttr('x', x)
        sum_tour = 0
        # for k in range(0, delivers_num):
        #     selected = [(i, j) for i in range(n) for j in range(n) if solution[i, j, k] > 0.5]
        #     sum_tour += len(subtour(selected))
        # assert sum_tour == n

        for k in range(delivers_num):
            for i in range(n):
                for j in range(i + 1):
                    if x[i, j, k].X == 1:
                        print("{} {} {}".format(k, i, j))
        for k in range(delivers_num):
            color = color_rgb(random.randrange(255), random.randrange(255), random.randrange(255))
            tspPainter.drawPathX(x, n, k, color)

        for i in range(n):
            print quicksum(degree[i, k].X for k in range(delivers_num))

        node_mat = [[[0 for i in range(n)] for i in range(n)] for i in range(delivers_num)]
        for k in range(delivers_num):
            for i in range(n):
                for j in range(n):
                    node_mat[k][i][j] = x[i, j, k]
        #print node_mat[0]

    def locker_scheme(self, locker, path_routes):
        capacity = 0
        for deliver_id in locker.delivers:
            if deliver_id in path_routes.keys():
                path = path_routes[deliver_id]
                for pack in path:
                    capacity += pack.capacity
        capacity += self.demands[locker.pos]
        return capacity
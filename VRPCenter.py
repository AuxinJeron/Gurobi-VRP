from gurobipy import *
from AntGraph import AntGraph
from TspPainter import tspPainter
from graphics import *
import itertools
import logging
import random
import networkx

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
        delivers_num = 2

        def vrp_callback(model, where):
            """vrp_callback: add constraint to eliminate infeasible solutions
            Parameters: gurobi standard:
                - model: current model
                - where: indicator for location in the search
            If solution is infeasible, adds a cut using cbLazy
            """
            # remember to set     model.params.DualReductions = 0     before using!


            if where != GRB.callback.MIPSOL:
                return
            edges = []
            for k in range(delivers_num):
                for i in range(n):
                    if model.cbGetSolution(x[i, j, k]) > .5:
                        if i != V[k] and j != V[k]:
                            edges.append((i, j))
            G = networkx.Graph()
            G.add_edges_from(edges)
            Components = networkx.connected_components(G)
            for S in Components:
                S_card = len(S)
                q_sum = sum(q[i] for i in S)
                NS = int(math.ceil(float(q_sum) / Q))
                S_edges = [(i, j) for i in S for j in S if i < j and (i, j) in edges]
                if S_card >= 3 and (len(S_edges) >= S_card or NS > 1):
                    model.cbLazy(quicksum(x[i, j] for i in S for j in S if j > i) <= S_card - NS)
                    print "adding cut for", S_edges
            return

        model = Model("TSP")
        n = len(self.antGraph.nodes_mat)
        # Create variables

        x = {}
        for i in range(n):
            for j in range(i+1):
                for k in range(delivers_num):
                    x[i, j, k] = model.addVar(obj=self.distance(i, j), vtype='I',
                                                  name='e' + str(i) + '_' + str(j) + '_' + str(k))
        degree = {}
        for k in range(delivers_num):
            for i in range(n):
                degree[i, k] = model.addVar(vtype=GRB.BINARY, name='degree_' + str(i) + '_' + str(k), lb=0, ub=1)
        model.update()

        for i in range(n):
            for k in range(delivers_num):
                model.addConstr(quicksum(x[i, j, k] for j in range(n)) == 2 * degree[i, k])
                x[i, i, k].ub = 0
            model.addConstr(quicksum(x[i, j, k] for j in range(n) for k in range(delivers_num)) >= 2)
        model.setObjective(quicksum(self.distance(i, j) * x[i, j, k] for i in range(n) for j in range(i+1) for k in range(delivers_num)), GRB.MINIMIZE)

        model.update()
        model.__data = x

        model.params.DualReductions = 0
        model.optimize(vrp_callback)


        # Add degree-2 constraint, and forbid loops

        # degree = {}
        # for k in range(delivers_num):
        #     for i in range(n):
        #         degree[i, k] = model.addVar(vtype=GRB.BINARY, name='degree_' + str(i) + '_' + str(k), lb=0, ub=1)
        # model.update()
        #
        # for i in range(n):
        #     for k in range(delivers_num):
        #         model.addConstr(quicksum(x[i, j, k] for j in range(n)) == 2 * degree[i,k])
        #         x[i, i, k].ub = 0
        #     model.addConstr(quicksum(x[i, j, k] for j in range(n) for k in range(delivers_num)) >= 2)
        # # Callback - use lazy constraints to eliminate sub-tours
        #
        # def subtourelim(model, where):
        #     if where == GRB.callback.MIPSOL:
        #         # make a list of edges selected in the solution
        #         for k in range(delivers_num):
        #             selected = []
        #             visited = set()
        #             for i in range(n):
        #                 sol = model.cbGetSolution([model._vars[i, j, k] for j in range(n)])
        #                 selected += [(i, j) for j in range(n) if sol[j] > 0.5]
        #                 if selected:
        #                     visited.add(i)
        #             # find the shortest cycle in the selected edge list
        #             tour = subtour(selected)
        #             if len(tour) < len(visited):
        #                 # add a subtour elimination constraint
        #                 print 'tour ' + repr(tour)
        #                 print 'len visited ' + str(len(visited)) + ' ' + repr(visited)
        #                 expr = quicksum(model._vars[i, j, k] for i,j in itertools.combinations(tour, 2))
        #                 # for i in range(len(tour)):
        #                 #     expr += quicksum(model._vars[tour[i], tour[j], k] for j in range(i + 1, len(tour)))
        #                 model.cbLazy(expr <= len(tour) - 1)
        #
        #             # must contain the start point
        #             start_point = self.delivers[k].pos
        #             if not start_point in visited:
        #                 model.cbLazy(quicksum(x[start_point, j, k] for j in range(n)) == 2)
        #
        # # Given a list of edges, finds the shortest subtour
        #
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

        # Optimize model



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


    def locker_scheme(self, locker, path_routes):
        capacity = 0
        for deliver_id in locker.delivers:
            if deliver_id in path_routes.keys():
                path = path_routes[deliver_id]
                for pack in path:
                    capacity += pack.capacity
        capacity += self.demands[locker.pos]
        return capacity
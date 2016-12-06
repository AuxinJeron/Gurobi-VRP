from graphics import *
import random

class TspPainter:
    def __init__(self):
        self.win = GraphWin('TSP', 500, 500)
        self.win.setCoords(0, 0, 80, 80)
        self.win.width = 100
        self.coord_mat = None
        self.nodes = []
        self.lockers = []
        self.paths = []

    def reset(self):
        for pt in self.nodes:
            self.win.delete(pt)
        self.nodes = []
        for locker in self.lockers:
            self.win.delete(locker)
        self.lockers = []
        for path in self.paths:
            self.win.delete(path)
        self.paths = []

    def drawMap(self):
        self.reset()
        coord_mat = self.coord_mat
        for coord in coord_mat:
            pt = Point(coord[0], coord[1])
            cir = Circle(pt, 0.5)
            cir.setFill("black")
            cir.setOutline("black")
            cir.draw(self.win)
            self.nodes.append(cir)

    def drawLockers(self, lockers):
        for locker in lockers:
            pt = Point(self.coord_mat[locker.pos][0], self.coord_mat[locker.pos][1])
            cir = Circle(pt, 0.5)
            cir.setFill("red")
            cir.setOutline("red")
            cir.draw(self.win)
            self.lockers.append(cir)

    def drawDeliver(self, delivers):
        for deliver in delivers:
            pt = Point(self.coord_mat[deliver.pos][0], self.coord_mat[deliver.pos][1])
            cir = Circle(pt, 0.5)
            cir.setFill("green")
            cir.setOutline("green")
            cir.draw(self.win)
            self.lockers.append(cir)

    def drawRoutes(self, routes):
        for key in routes:
            color = color_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.drawPath(routes[key], color)

    def drawPath(self, path, color):
        for i in range(0, len(path) ):
            i1 = i % len(path)
            i2 = (i + 1) % len(path)
            pack1 = path[i1]
            pack2 = path[i2]
            pt1 = Point(self.coord_mat[pack1.pos][0], self.coord_mat[pack1.pos][1])
            pt2 = Point(self.coord_mat[pack2.pos][0], self.coord_mat[pack2.pos][1])
            line = Line(pt1, pt2)
            line.setFill(color)
            line.setOutline(color)
            line.draw(self.win)
            self.paths.append(line)

    def drawPathX(self, x, n, k, color):
        for i in range(n):
            for j in range(i + 1):
                if x[i, j, k].X > 0.5:
                    pt1 = Point(self.coord_mat[i][0], self.coord_mat[i][1])
                    pt2 = Point(self.coord_mat[j][0], self.coord_mat[j][1])
                    line = Line(pt1, pt2)
                    line.setFill(color)
                    line.setOutline(color)
                    line.draw(self.win)
                    self.paths.append(line)

tspPainter = TspPainter()

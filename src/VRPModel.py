

class Locker:
    def __init__(self, locker_id, pos):
        self.id = locker_id
        self.pos = pos
        self.orders = []
        self.delivers = []

    def __str__(self):
        return "[id:{}, pos:{}, delivers:{}]".format(self.id, self.pos, self.delivers)


class Deliver:
    def __init__(self, deliver_id, pos, max_distance, max_capacity):
        self.id = deliver_id
        self.pos = pos
        self.locker_id = None
        self.max_distance = max_distance
        self.max_capacity = max_capacity

    def __str__(self):
        return "[id:{}, pos:{}, locker_id:{}, max_distance:{}, max_capacity:{}]".format(self.id, self.pos, self.locker_id, self.max_distance, self.max_capacity)

    def __repr__(self):
        return "{}".format(self.pos)

    def nearest_locker(self, lockers, nodes_mat):
        min_d = float('inf')
        for locker in lockers:
            if nodes_mat[locker.pos][self.pos] < min_d:
                self.locker_id = locker.id
                min_d = nodes_mat[locker.pos][self.pos]
        return self.locker_id

class Package:
    def __init__(self, pos, capacity, deliver, index):
        self.pos = pos
        self.capacity = capacity
        self.deliver = deliver
        self.index = index

    def __str__(self):
        return "[pos:{}, capacity:{}, deliver:{}, index:{}]".format(self.pos, self.capacity, self.deliver, self.index)

    def __repr__(self):
        return "[pos:{}, capacity:{}, deliver:{}, index:{}]".format(self.pos, self.capacity, self.deliver, self.index)
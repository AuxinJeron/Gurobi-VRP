# ACS-VRP-Gurobi
This is a project using Gurobi to vehicle routing problem.

## How to run

### Construction requirment

python 3.5, graphics.py Gurobi 6.5.2

### Input

Command line `python src/vrpmain.py *.graph`, where `*.graph` is the graph file identify the necessary information for the problem, the example file could be found at `data/eil51.graph`.

###Graph file format

The graph file format is based on the TSPLIB sample data file, and add some additional attributes like `DELIVER_SECTION` and `LOCKER_SECTION`.

## Output
The output for each problem is the optimal delivery assignments for all the delivers, the capacity assignment for each locker and a optiaml solution graph. 

Below is the optimal solution for the sample data `data/eil51.graph`.

![sample](/resources/optimal_solution.png)

<img src="/resources/optimal_graph.png" width="400"/>


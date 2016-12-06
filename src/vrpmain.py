from TsplibParser import parser as tspparser
from ArgParser import parser as argparser
from VRPCenter import VRPCenter
from TspPainter import tspPainter
import logging

# construct the logger
logger = logging.getLogger("logger")
logger.setLevel(logging.INFO)
logFormatter = logging.Formatter("%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)s")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

def run(tspparser):
    center = VRPCenter(tspparser)
    logger.info("Nodes: ")
    for i in range(1, len(tspparser.cities_coord)):
        logger.info("Node " + str(i) + " coordinate is " + str(tspparser.cities_coord[i][0]) + ", " + str(tspparser.cities_coord[i][1]))
    tspPainter.coord_mat = tspparser.cities_coord
    tspPainter.drawMap()

    logger.info("Lockers: ")
    for i in range(0, len(tspparser.lockers)):
        logger.info(tspparser.lockers[i])
    tspPainter.drawLockers(tspparser.lockers)

    logger.info("Delivers: ")
    for i in range(0, len(tspparser.delivers)):
        logger.info(tspparser.delivers[i])
    logger.info("Demands: ")
    demands = 0
    for i in range(0, len(tspparser.demands)):
        demands += tspparser.demands[i]
        logger.info("Node {} {}".format(i, tspparser.demands[i]))
    logger.info("Total demands is: {}".format(demands))

    center.start()
    raw_input("Press Enter to quit...")

def main():
    args = argparser.parse_args()
    tspparser.read_file(args.tsp_file[0])

    logger.info("-------------------------------------------")
    logger.info("Problem formulation information")
    logger.info("-------------------------------------------")
    logger.info("Name: " + tspparser.name)
    logger.info("Comment: " + tspparser.comment)
    logger.info("Type: " + tspparser.type)
    # run vrp center
    run(tspparser)

if __name__ == "__main__":
    main()
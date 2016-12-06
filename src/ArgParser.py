import argparse

parser = argparse.ArgumentParser(
    description = "Parser TSP files and calculate the optimization solution using Ant Colony System"
    )

parser.add_argument (
      "tsp_file"
    , nargs   = "+"
    , metavar = "PATH"
    , help    = "Path to directory or .tsp or .vrp file."
    )
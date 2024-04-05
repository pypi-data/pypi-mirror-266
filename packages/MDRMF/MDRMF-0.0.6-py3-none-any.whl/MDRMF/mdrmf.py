import argparse
from . import Experimenter, Dataset  # Dataset must be imported for pickle

def main():
    # Initialize parser
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("--experiments", help="Experiments configuration file in YAML format")

    # Read arguments from command line
    args = parser.parse_args()

    if args.experiments:
        experimenter = Experimenter(args.experiments)
        experimenter.conduct_all_experiments()

if __name__ == "__main__":
    main()
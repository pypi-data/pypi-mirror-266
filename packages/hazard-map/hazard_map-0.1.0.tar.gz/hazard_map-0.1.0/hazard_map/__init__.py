import argparse
from hazard_map import HazardMap

def main():
    arguments = parse_arguments()

    hazard_log = HazardLog(arguments.input_sheet)

    graph = gpit_log.create_graph()

    gpit_log.summarize_degrees(5)

    gpit_log.save_graph()
    gpit_log.show_graph()

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='hazard-map',
        description='Build and analyze a network model of hazards, causes, and controls',
    )

    parser.add_argument(
        'input_sheet',
        help='The hazard mapping excel file to evaluate',
    )

    parser.add_argument(
        '-o', '--output-sheet',
        help='Set a custom file name/location for the hazard log output',
        default=None,
        type=str,
    )

    return parser.parse_args()

if __name__ == '__main__':
    main()

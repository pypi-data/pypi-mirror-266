import argparse
from .sq_base import SQSimSetupGen

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate simulation setup.')
    parser.add_argument('--json_file', type=str, required=True, help='Path to the input JSON file.')
    parser.add_argument('--output_folder', type=str, required=True, help='Path to the output folder.')
    args = parser.parse_args()
    sim = SQSimSetupGen(json_file=args.json_file)
    sim.generate(output_folder=args.output_folder)
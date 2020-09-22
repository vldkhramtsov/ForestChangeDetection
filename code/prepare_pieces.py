import argparse
from preprocess.prepare_pieces import PreparePieces


def parse_args():
    parser = argparse.ArgumentParser(
        description='Script for creating binary mask from geojson.'
    )
    parser.add_argument(
        '--tiff_file', '-tf', dest='tiff_file',
        required=True, help='Name of the directory with source tiff folders'
    )
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    pp = PreparePieces()
    pp.process(args.tiff_file)
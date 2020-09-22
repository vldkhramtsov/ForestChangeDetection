import os
import settings

# from preprocess.prepare_pieces import PreparePieces
from preprocess.image_diff import ImageDifference
from preprocess.preprocess import download_and_process
from preparation.sentinel_download import SentinelDownload


def prepare_dataset():

    download_and_process()

    for filename in os.listdir(settings.MODEL_TIFFS_DIR):
        os.system(f'python3 prepare_pieces.py --tiff_file={filename}')

    imd = ImageDifference()
    imd.get_diff_and_split()


if __name__ == '__main__':
    # s2_download = SentinelDownload()
    # s2_download.download()
    prepare_dataset()

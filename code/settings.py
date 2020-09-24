import os

def path_exists_or_create(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

CONFIG_FILE = 'sentinel.config'
PARENT_URL = 'gs://gcp-public-data-sentinel-2'
LEVEL_C_GCP_FOLDER = '/tiles'
LEVEL_A_GCP_FOLDER = '/L2/tiles'
STOP_SUFFIX = '_$folder$'
BAND_RESOLUTIONS = {'TCI': '10m',
                    'B01': '60m',
                    'B02': '10m',
                    'B03': '10m',
                    'B04': '10m',
                    'B05': '20m',
                    'B06': '20m',
                    'B07': '20m',
                    'B08': '10m',
                    'B8A': '20m',
                    'B09': '60m',
                    'B10': '60m',
                    'B11': '20m',
                    'B12': '20m'}

MAXIMUM_DATES_REVIEWED_FOR_TILE = 220
MAXIMUM_DATES_STORE_FOR_TILE = 2
MAXIMUM_EMPTY_PIXEL_PERCENTAGE = 0.05
MAXIMUM_CLOUD_PERCENTAGE_ALLOWED = 50
SENTINEL_DELTA_DAYS = 5
MAXIMUM_DELTA_DAYS = 350

STANDARD_CRS = 'EPSG:32637'

PIECE_WIDTH = 56
PIECE_HEIGHT = 56
NEIGHBOURS = 6
TRAIN_SIZE, TEST_SIZE, VALID_SIZE = 0.7, 0.15, 0.15

# /sentinel
HERE_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
# /sentinel
BASE_DIR_PATH = HERE_DIR_PATH.split('/')[1]
# /sentinel/data/
DATA_PATH = path_exists_or_create(f'/{BASE_DIR_PATH}/data')

GLOBAL_TILE_DATE_INFOFILE = f'{DATA_PATH}/date_tile_info.csv'
POLYS_PATH = f'{DATA_PATH}/polygons/'
DOWNLOADED_IMAGES_DIR = f'{DATA_PATH}/input'
# DOWNLOADED_IMAGES_DIR = path_exists_or_create(f'{DATA_PATH}/tmp')

POLYS_BUFFERED_PATH = path_exists_or_create(f'{DATA_PATH}/polygons_time_limiting')

MODEL_TIFFS_DIR = path_exists_or_create(f'{DATA_PATH}/images')
PIECES_DIR = path_exists_or_create(f'{DATA_PATH}/results')
DIFF_PATH = path_exists_or_create(f'{DATA_PATH}/diff')
# DIFF_PATH = path_exists_or_create(f'{DATA_PATH}/tmp')

SENTINEL_NUM_BANDS = 3
SCENE_PREFIX = '.jp2'

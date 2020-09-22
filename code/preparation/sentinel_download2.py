import requests
import pandas as pd
import geopandas as gpd
import settings
import subprocess

PARENT_URL = "https://storage.googleapis.com"
CHANNEL = 'TCI'
GRANULE_ID_COLUMN = 'GRANULE_ID'
TILE_ID_COLUNM = 'MGRS_TILE'
URL_COLUMN = 'BASE_URL'
URL_POSITION_START = 5 # drop 'gs://'
DATE_POSITION_IN_URL = 6
LEVEL_C_GCP_FOLDER = '/tiles/'
LEVEL_A_GCP_FOLDER = '/L2/tiles/'
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

def get_tile_url(granule_id, granule_url, tile_id, channels=[CHANNEL]):
    # https://cloud.google.com/storage/docs/access-control/signing-urls-manually
    # T36UXA
    tile_id = f"T{tile_id}"
    # gcp-public-data-sentinel-2/tiles/04/M/ES/S2B_MSIL1C_20180321T205629_N0206_R114_T04MES_20180321T222117.SAFE
    url = granule_url[URL_POSITION_START:]
    url = url.replace(LEVEL_C_GCP_FOLDER, LEVEL_A_GCP_FOLDER)
    date = url.split('/')[DATE_POSITION_IN_URL].split('_')[2]

    complete_urls = {}
    for band in channels:
        resolution = BAND_RESOLUTIONS.get(band)
        if resolution is not None:
            # complete_urls[band] = f"{PARENT_URL}/{url}/GRANULE/{granule_id}/IMG_DATA/R{resolution}/{tile_id}_{date}_{band}_{resolution}.jp2"
            complete_urls[band] = f"gs://{url}/GRANULE/{granule_id}/IMG_DATA/R{resolution}/{tile_id}_{date}_{band}_{resolution}.jp2"
            complete_urls[band] = complete_urls[band].replace('L1C', 'L2A')
    print(complete_urls)
    return complete_urls


def download(link, filename):
    request = requests.get(link)
    open(filename, 'wb').write(request.content)



def task():
    granule_id = 'L1C_T03UXV_A019903_20190414T215531'
    granule_url = 'gs://gcp-public-data-sentinel-2/tiles/03/U/XV/S2A_MSIL1C_20190414T215531_N0207_R029_T03UXV_20190415T012959.SAFE'
    tile_id = '03UXV'
    print(granule_id)
    urls = get_tile_url(granule_id, granule_url, tile_id)

    for channel in urls.keys():
        link = urls[channel]
        # download(url, f"{settings.DOWNLOADED_IMAGES_DIR}/{granule_id}_{channel}.jp2")
        # download(url, f"{granule_id}_{channel}.jp2")
        links = subprocess.run(["gsutil", "ls", "gs://gcp-public-data-sentinel-2/"],
                               universal_newlines = True,
                               stdout=subprocess.PIPE)
        print(links.stdout.splitlines())

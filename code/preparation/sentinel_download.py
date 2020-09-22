import os
import subprocess
import configparser

import pandas as pd
import geopandas as gpd

from settings import (BAND_RESOLUTIONS, PARENT_URL, STOP_SUFFIX,
                      LEVEL_C_GCP_FOLDER, LEVEL_A_GCP_FOLDER,
                      CONFIG_FILE, GLOBAL_TILE_DATE_INFOFILE,
                      DOWNLOADED_IMAGES_DIR)


class SentinelDownload:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        self.product_level = config['GCP']['LEVEL']
        self.channels = config['GCP']['BANDS'].split(' ')

        self.parent_url = PARENT_URL
        self.tiles_dates_list = pd.read_csv(GLOBAL_TILE_DATE_INFOFILE)
        self.tile_directories = {}
        if self.product_level == 'L2A':
            self.parent_url += LEVEL_A_GCP_FOLDER
        elif self.product_level == 'L1C':
            self.parent_url += LEVEL_C_GCP_FOLDER
        else:
            raise ValueError(f'Incorrect product level: {self.product_level}. '
                             'Required one of `L2A` or `L1C`.')

    def _filter_folders(self, buckets):
        return [bucket for bucket in buckets if not bucket.endswith(STOP_SUFFIX)]


    def _get_files(self, url):
        buckets = subprocess.run(["gsutil", "ls", url],
                                 universal_newlines=True,
                                 stdout=subprocess.PIPE)
        buckets = buckets.stdout.splitlines()
        return self._filter_folders(buckets)


    def _retrieve_tile_info(self, tileID):
        if self.tile_directories.get(tileID) is None:
            url = f"{self.parent_url}/{tileID[:2]}/{tileID[2]}/{tileID[3:]}"
            self.tile_directories[tileID] = self._get_files(url)


    def _get_tile_path(self, tileID, img_date):
        self._retrieve_tile_info(tileID)
        for directory in self.tile_directories.get(tileID):
            if img_date in directory:
                return directory
        return None


    def _images_links(self, tileID, img_date, channels):
        link = self._get_tile_path(tileID, img_date)
        try:
            link += 'GRANULE'
            links = self._get_files(link)
        except TypeError:
            return {}

        if len(links) == 0 or len(links) > 1:
            return {}
        else:
            link = links[0]
            link += 'IMG_DATA/'
            image_links = {}
            for band in channels:
                if self.product_level == 'L2A' and band != 'CLD':
                    resolution = BAND_RESOLUTIONS.get(band)
                    tmp_link = link + f'R{resolution}'
                    image_list = self._get_files(tmp_link)
                if self.product_level == 'L1C' and band != 'CLD':
                    image_list = self._get_files(link)
                if self.product_level == 'L2A' and band == 'CLD':
                    cloud_link = link.replace('IMG_DATA', 'QI_DATA')
                    image_list = [cloud_link + 'MSK_CLDPRB_20m.jp2']
                image_links[band] = [image for image in image_list if band in image]
            return image_links


    def _retrieve_images(self, links, img_date, tileID):
        if links is not None:
            print(links)
            for band in links.keys():
                if len(links[band]) == 1:
                    link = links[band][0]
                    # save_path = f"{DOWNLOADED_IMAGES_DIR}/{self.product_level}_{img_date}_{tileID}_{band}.jp2"
                    save_path = f"{DOWNLOADED_IMAGES_DIR}/{img_date}_{tileID}_{band}.jp2"
                    if not os.path.exists(save_path):
                        subprocess.run(["gsutil", "cp", link, save_path])
            return True
        return False


    def download(self, img_date=None, tileID=None):
        success_count = 0
        for idx, tile in self.tiles_dates_list.iterrows():
            tileID = tile['tileID']
            img_date = str(tile['img_date'])
            print(idx, tileID, img_date)
            links = self._images_links(tileID, img_date, self.channels)
            if self._retrieve_images(links, img_date, tileID):
                success_count += 1
            # else:
            #     for date_bias in range(-2, 3, 1):
            #         img_date = int(img_date)
            #         img_date_biased = str(int(img_date + 1))
            #         links = self._images_links(tileID, img_date_biased, self.channels)
            #         if self._retrieve_images(links, img_date, tileID):
            #             success_count += 1
            #             break
            print(f'Downloaded: {success_count}/{len(self.tiles_dates_list)}.\n\n\n')

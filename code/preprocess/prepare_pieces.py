import warnings
warnings.filterwarnings('ignore')

import os
import re
import csv
import cv2
import imageio
import datetime
import argparse
import rasterio

import numpy as np
import pandas as pd
import geopandas as gp
import rasterio.mask as rm

from rasterio import features
from geopandas import GeoSeries
from skimage import img_as_ubyte
from shapely.geometry import Polygon
from rasterio.windows import Window
from rasterio.plot import reshape_as_image

from utils import date_limit, image_non_zero, img_date_to_datetime
from settings import path_exists_or_create
from settings import MODEL_TIFFS_DIR, PIECES_DIR, POLYS_PATH, POLYS_BUFFERED_PATH, DOWNLOADED_IMAGES_DIR
from settings import PIECE_WIDTH, PIECE_HEIGHT, STANDARD_CRS, MAXIMUM_CLOUD_PERCENTAGE_ALLOWED


class PreparePieces:
    def __init__(self):
        self.tiff_path = MODEL_TIFFS_DIR
        self.polys_path = POLYS_PATH
        self.width = PIECE_WIDTH
        self.height = PIECE_HEIGHT
        self.image_width = None
        self.image_height = None

    def poly2mask(self, filename, image_path, data_path, filter_by_date=True):
        def match_clearcuts(row, buffered_sample):
            return buffered_sample[buffered_sample['geometry'].intersects(row['geometry'])][['img_date_min', 'img_date_max']]

        date = filename.split('_')[0][:8]
        date = datetime.datetime.strptime(date, '%Y%m%d')

        markup = pd.DataFrame()
        for file in os.listdir(POLYS_PATH):
            shp = gp.read_file(os.path.join(POLYS_PATH, file)).to_crs(STANDARD_CRS)
            buffered_sample = gp.read_file(os.path.join(POLYS_BUFFERED_PATH, file)).to_crs(STANDARD_CRS)
            shp['is_date_valid'] = shp.apply(lambda shape: img_date_to_datetime(shape), axis=1)
            shp = shp[shp['is_date_valid']]
            shp = shp[~shp['geometry'].isnull()]
            shp['img_date'] = shp['img_date'].apply(
                    lambda x: datetime.datetime.strptime(x, '%Y%m%d'))
            # shp[['img_date_min', 'img_date_max']] = shp.apply(lambda row: match_clearcuts(row, buffered_sample), axis=1, result_type="expand")
            for _, clearcut in shp.iterrows():
                intersecting = buffered_sample[buffered_sample['geometry'].intersects(clearcut['geometry'])]
                img_date_min, img_date_max = intersecting['img_date_min'].iloc[0], intersecting['img_date_max'].iloc[0]
                img_date_min = datetime.datetime.strptime(img_date_min[:10], '%Y-%m-%d')
                img_date_max = datetime.datetime.strptime(img_date_max[:10], '%Y-%m-%d')
                clearcut = clearcut.to_dict()
                clearcut['date_min'] = img_date_min
                clearcut['date_max'] = img_date_max
                if date >= img_date_min and date <= img_date_max:
                    markup = markup.append(clearcut, ignore_index=True)

        markup = gp.GeoDataFrame(markup, crs=STANDARD_CRS)
        print(f"Markup interval: \
                {markup['img_date'].min()} - {markup['img_date'].max()}")
        # if filter_by_date:
        #     date += datetime.timedelta(days=1)
        #     polys = markup[markup['img_date'] <= date].loc[:, 'geometry']
        # else:
        #     polys = markup.loc[:, 'geometry']

        polys = markup.loc[:, 'geometry']
        with rasterio.open(image_path) as image:
            polys = polys.to_crs(image.crs)
            mask = features.rasterize(shapes=polys,
                                      out_shape=(image.height, image.width),
                                      transform=image.transform,
                                      default_value=255)

            filename = f'{data_path}/full_mask.png'
            imageio.imwrite(filename, mask)

        date += datetime.timedelta(days=1)
        polys = markup[markup['img_date'] <= date].loc[:, 'geometry']
        with rasterio.open(image_path) as image:
            polys = polys.to_crs(image.crs)
            mask = features.rasterize(shapes=polys,
                                      out_shape=(image.height, image.width),
                                      transform=image.transform,
                                      default_value=255)

            filename = '{}/{}.png'.format(
                data_path,
                re.split(r'[/.]', image_path)[-2]
            )
            imageio.imwrite(filename, mask)
        return filename, markup

    def divide_into_pieces(self, filename, image_path, cloud_path, data_path):
        def get_cloud_part(cld, src, poly):
            cld_raster, cld_transform = rm.mask(cld, [poly], crop=True)
            out_meta = src.meta
            out_meta.update({"driver": "GTiff",
                            "height": cld_raster.shape[1],
                            "width": cld_raster.shape[2],
                            "transform": cld_transform})
            return cld_raster, out_meta


        os.makedirs(f'{data_path}/images', exist_ok=True)
        os.makedirs(f'{data_path}/geojson_polygons', exist_ok=True)

        full_mask = imageio.imread(f'{data_path}/full_mask.png')

        with rasterio.open(image_path) as src, open(f'{data_path}/image_pieces.csv', 'w') as csvFile,\
             rasterio.open(cloud_path) as cld:
            writer = csv.writer(csvFile)
            writer.writerow([
                'original_image', 'piece_image', 'piece_geojson',
                'start_x', 'start_y', 'width', 'height'
            ])

            for j in range(0, src.height // self.height):
                for i in range(0, src.width // self.width):
                    window = Window(i * self.width, j * self.height, self.width, self.height)
                    raster_window = src.read(window=window)
                    image_array = reshape_as_image(raster_window)[:, :, :3]

                    is_mask = full_mask[j * self.height: j * self.height + self.height,
                                        i * self.width:  i * self.width  + self.width].sum() > 0

                    if image_non_zero(image_array) and is_mask:
                        image_format = 'tiff'
                        piece_name = f'{filename}_{j}_{i}.{image_format}'

                        poly = Polygon([
                            src.xy(j * self.height, i * self.width),
                            src.xy(j * self.height, (i + 1) * self.width),
                            src.xy((j + 1) * self.height, (i + 1) * self.width),
                            src.xy((j + 1) * self.height, i * self.width),
                            src.xy(j * self.height, i * self.width)
                        ])
                        cld_raster, cld_meta = get_cloud_part(cld, src, poly)
                        gs = GeoSeries([poly])
                        gs.crs = src.crs
                        piece_geojson_name = f'{filename}_{j}_{i}.geojson'
                        gs.to_file(
                            f'{data_path}/geojson_polygons/{piece_geojson_name}',
                            driver='GeoJSON'
                        )
                        if cld_raster.sum() / cld_raster.size > MAXIMUM_CLOUD_PERCENTAGE_ALLOWED:
                            image_array = reshape_as_image(raster_window)
                            meta = src.meta
                            meta['height'] = image_array.shape[0]
                            meta['width'] = image_array.shape[1]
                            meta['transform'] = rasterio.windows.transform(window, src.transform)
                            with rasterio.open(f'{data_path}/images/{piece_name}', 'w', **meta) as dst:
                                for ix in range(image_array.shape[2]):
                                    dst.write(image_array[:, :, ix], ix + 1)

                            writer.writerow([filename, piece_name, piece_geojson_name,
                                            i * self.width, j * self.height,
                                            self.width, self.height])

    def split_mask(self, mask_path, save_mask_path, image_pieces_path):
        pieces_info = pd.read_csv(
            image_pieces_path, dtype={
                'start_x': np.int64, 'start_y': np.int64,
                'width': np.int64, 'height': np.int64
            }
        )
        mask = imageio.imread(mask_path)
        self.image_width, self.image_height = mask.shape[0], mask.shape[1]
        for i in range(pieces_info.shape[0]):
            piece = pieces_info.loc[i]
            piece_mask = mask[
                piece['start_y']: piece['start_y'] + piece['height'],
                piece['start_x']: piece['start_x'] + piece['width']
            ]
            filename_mask = '{}/{}.png'.format(
                save_mask_path,
                re.split(r'[/.]', piece['piece_image'])[-2]
            )
            imageio.imwrite(filename_mask, piece_mask)


    def process(self, filename):
        print(filename)
        cloud_name = "_".join(filename.split('_')[:-1])
        cloud_path = os.path.join(DOWNLOADED_IMAGES_DIR, f"{cloud_name}_CLD.jp2")
        print(cloud_path)

        data_path = path_exists_or_create(os.path.join(PIECES_DIR, filename))
        image_path = os.path.join(self.tiff_path, filename, f"{filename}_merged.tiff")
        mask_path, _ = self.poly2mask(filename, image_path, data_path)
        self.divide_into_pieces(filename, image_path, cloud_path, data_path)
        pieces_info = os.path.join(data_path, 'image_pieces.csv')

        save_mask_path = path_exists_or_create(os.path.join(data_path, 'masks'))
        self.split_mask(mask_path, save_mask_path, pieces_info)

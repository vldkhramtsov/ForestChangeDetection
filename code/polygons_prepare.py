import warnings
warnings.filterwarnings('ignore')
# from preparation.sentinel_download import SentinelDownload
import os
import datetime

import numpy as np
import pandas as pd
import geopandas as gp

from settings import POLYS_PATH, POLYS_BUFFERED_PATH, STANDARD_CRS
from utils import img_date_to_datetime


def polygons_time_limiting(filter_by_date=True):
    for file in os.listdir(POLYS_PATH):
        shp = gp.read_file(os.path.join(POLYS_PATH, file)).to_crs(STANDARD_CRS)
        shp['is_date_valid'] = shp.apply(lambda shape: img_date_to_datetime(shape), axis=1)
        shp = shp[shp['is_date_valid']]
        shp = shp[~shp['geometry'].isnull()]
        shp['img_date'] = shp['img_date'].apply(
                lambda x: datetime.datetime.strptime(x, '%Y%m%d'))
        shp['geometry'] = shp['geometry'].buffer(10)
        res_union = shp.geometry.unary_union
        from shapely.ops import polygonize
        res_union = [geom for geom in polygonize(res_union)]
        result = {'geometry': res_union}
        result['img_date_min'] = []
        result['img_date_max'] = []
        for markup in result['geometry']:
            polys = shp[shp['geometry'].intersects(markup)]['img_date']
            result['img_date_min'] += [np.min(polys)]
            result['img_date_max'] += [np.max(polys)]
        result = gp.GeoDataFrame(result, crs=STANDARD_CRS)
        print(result)
        result.to_file(f'{POLYS_BUFFERED_PATH}/{file}', driver='GeoJSON')

def poly2mask(filename='20190407_36UYA_TCI', filter_by_date=True):
    def match_clearcuts(row, buffered_sample):
        return buffered_sample[buffered_sample['geometry'].intersects(row['geometry'])][['img_date_min', 'img_date_max']]

    # markups = [gp.read_file(os.path.join(POLYS_PATH, file)).to_crs(STANDARD_CRS) for file in os.listdir(self.polys_path)]

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
        if len(markup) > 0:
            print(date, markup[['img_date', 'date_min', 'date_max']])

# polygons_time_limiting()
# poly2mask()

from preparation.get_tiles_from_labeling import *

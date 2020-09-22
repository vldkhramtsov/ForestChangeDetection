import rasterio
import numpy as np
import os

from settings import path_exists_or_create
from settings import (MODEL_TIFFS_DIR,
                      DOWNLOADED_IMAGES_DIR,
                      SCENE_PREFIX,
                      SENTINEL_NUM_BANDS)

import shutil

def ndvi_command(src, dst):
    return f'gdal_calc.py ' \
                f'-A {src} --A_band=3 ' \
                f'-B {src} --B_band=4 ' \
                f'--outfile={dst} --calc="(B-A)/(A+B+0.001)" ' \
                f'--type=Float32 --NoDataValue=0'


def translate_command(src, dst, band_index, min_value=0, max_value=255, output_type='Byte'):
    with rasterio.open(src, nodata=0) as src_img:
        img = src_img.read(band_index, masked=True)
        img = np.nan_to_num(img)
        mean_ = img.mean()
        std_ = img.std()
        min_ = max(img.min(), mean_ - 2 * std_)
        max_ = min(img.max(), mean_ + 2 * std_)

        return f'gdal_translate -ot {output_type} -b {band_index}\
            -scale {min_} {max_} {min_value} {max_value} \
            {src} {dst}'


def merge_command(srcs, dst):
    return f'gdal_merge.py -separate -o ' \
           f'{dst} ' \
           f'{" ".join(srcs)}'


def download(tile_id):
    src = os.path.join(DOWNLOADED_IMAGES_DIR, f"{tile_id}{SCENE_PREFIX}")
    dst_dir = path_exists_or_create(f"{MODEL_TIFFS_DIR}/{tile_id}")

    bands = []

    bnds_temp_dir = os.path.join(dst_dir, tile_id)
    path_exists_or_create(dst_dir)
    path_exists_or_create(bnds_temp_dir)

    for band in range(1, SENTINEL_NUM_BANDS+1):
        band_dst = os.path.join(bnds_temp_dir, f'B0{band}.tiff')
        cmd = translate_command(src, band_dst, band)
        bands.append(band_dst)
        os.system(cmd)

    # ndvi_band_dst = os.path.join(bnds_temp_dir, f'ndvi.tiff')
    # cmd_ndvi = ndvi_command(src, ndvi_band_dst)
    # os.system(cmd_ndvi)

    # ndvi_band_byte_dst = os.path.join(bnds_temp_dir, f'ndvi_byte.tiff')
    # cmd_ndvi_tranform = translate_command(ndvi_band_dst, ndvi_band_byte_dst, 1)
    # os.system(cmd_ndvi_tranform)
    # bands.append(ndvi_band_byte_dst)

    result_tiff_name = f'{tile_id}_merged.tiff'
    merge_cmd = merge_command(bands, dst=os.path.join(dst_dir, result_tiff_name))
    os.system(merge_cmd)

    shutil.rmtree(bnds_temp_dir)


def download_and_process():
    for filename in os.listdir(DOWNLOADED_IMAGES_DIR):
        if 'CLD' not in filename:
            scene_name = filename.split(SCENE_PREFIX)[0]
            download(scene_name)

import os
import geopandas as gpd
import pandas as pd
import settings

def tiledate_to_imgdate(row):
    td = row['TileDate'].split('_')[-1]
    return f"{td[:4]}{td[4:6]}{td[6:]}"


def pl2sen(row):
    planetID = row['tileID']
    sentinel_tile = planet_sentinel_info[planet_sentinel_info['image_id'] == planetID]
    sentinel_tile = sentinel_tile['sentinel_id'].iloc[0]
    return sentinel_tile.split('_')[1][1:]

def tileid_to_normal(row):
    tileid = row['tileID']
    if tileid.startswith('20'):
        tileid = tileid.split('_')[-1]
    else:
        tileid = tileid.split('_')[-2][1:]
    if tileid == '37UCR':
        tileid = '36UYA'
    return tileid

# file = '36UYA_36UXA_baseline.geojson'
# df = gpd.read_file(f"{settings.DATA_PATH}/polygons_raw/{file}")
# df['tileID'] = df.apply(lambda row: tileid_to_normal(row), axis=1)
# df['img_date'] = df['img_date'].str.replace('-','')
# df[['img_date', 'tileID', 'geometry']].to_file(f"{settings.DATA_PATH}/polygons/{file}", driver='GeoJSON')

# file = '36UXA_time-dependent.geojson'
# df = gpd.read_file(f"{settings.DATA_PATH}/polygons_raw/{file}")
# df['tileID'] = '36UXA'
# df['img_date'] = df['img_date'].str.replace('-','')
# df[['img_date', 'tileID', 'geometry']].to_file(f"{settings.DATA_PATH}/polygons/{file}", driver='GeoJSON')

# file = '36UYA_Spring_time-dependent.geojson'
# df = gpd.read_file(f"{settings.DATA_PATH}/polygons_raw/{file}")
# df['tileID'] = '36UYA'
# df['img_date'] = df['img_date'].str.replace('-','')
# df[['img_date', 'tileID', 'geometry']].to_file(f"{settings.DATA_PATH}/polygons/{file}", driver='GeoJSON')

# file = '36UYA_Summer_time-dependent.geojson'
# df = gpd.read_file(f"{settings.DATA_PATH}/polygons_raw/{file}")
# df['tileID'] = '36UYA'
# df['img_date'] = df['img_date'].str.replace('-','')
# df[['img_date', 'tileID', 'geometry']].to_file(f"{settings.DATA_PATH}/polygons/{file}", driver='GeoJSON')

# file = 'Planet_clearcuts.geojson'
# df = gpd.read_file(f"{settings.DATA_PATH}/polygons_raw/{file}")
# planet_sentinel_info = gpd.read_file(f"{settings.DATA_PATH}/polygons_raw/aux/label_pairs.geojson")
# df['tileID'] = df.apply(lambda row: pl2sen(row), axis=1)
# df = df[df['tileID']!='36UYV']
# df = df[df['tileID']!='37UCR']
# df['img_date'] = df['img_date'].str.replace('-','')
# df[['img_date', 'tileID', 'geometry']].to_file(f"{settings.DATA_PATH}/polygons/{file}", driver='GeoJSON')

# file = 'Clearcuts_37UDQ_20160827_20190916_EachImage.geojson'
# df = gpd.read_file(f"{settings.DATA_PATH}/polygons_raw/{file}")
# df['tileID'] = '37UDQ'
# df['img_date'] = df['Date'].str.replace('-','')
# #df.loc[df['img_date'] == '2109-05-05'] = '2019-05-05'
# df = df[df['img_date'] != '20010612']
# df = df[df['img_date'] != '21090505']
# df[['img_date', 'tileID', 'geometry']].to_file(f"{settings.DATA_PATH}/polygons/{file}", driver='GeoJSON')

# file = '36UYV_20150826_20191019_Each_Image.geojson'
# df = gpd.read_file(f"{settings.DATA_PATH}/polygons_raw/{file}")
# df['tileID'] = '36UYV'
# df['img_date'] = df.apply(lambda row: tiledate_to_imgdate(row), axis=1)
# df = df[df['img_date']!='201501005']
# df['img_date'] = df['img_date'].str.replace('-','')
# del df['TileDate']
# df[['img_date', 'tileID', 'geometry']].to_file(f"{settings.DATA_PATH}/polygons/{file}", driver='GeoJSON')

file = 'Clearcuts_36UWA_20150809_20170813_EachImage.geojson'
df = gpd.read_file(f"{settings.DATA_PATH}/polygons_raw/{file}")
df['tileID'] = '36UWA'
df['img_date'] = df['TileDate']
df['img_date'] = df['img_date'].str.replace('-','')
df[['img_date', 'tileID', 'geometry']].to_file(f"{settings.DATA_PATH}/polygons/{file}", driver='GeoJSON')

file = 'Clearcuts_36UWA_20170813_20180823_EachImage.geojson'
df = gpd.read_file(f"{settings.DATA_PATH}/polygons_raw/{file}")
df['tileID'] = '36UWA'
df['img_date'] = df['TileDate']
df['img_date'] = df['img_date'].str.replace('-','')
df[['img_date', 'tileID', 'geometry']].to_file(f"{settings.DATA_PATH}/polygons/{file}", driver='GeoJSON')

file = 'Clearcuts_36UWA_20180823_20190614_EachImage.geojson'
df = gpd.read_file(f"{settings.DATA_PATH}/polygons_raw/{file}")
df['tileID'] = '36UWA'
df['img_date'] = df['TileDate']
df['img_date'] = df['img_date'].str.replace('-','')
df[['img_date', 'tileID', 'geometry']].to_file(f"{settings.DATA_PATH}/polygons/{file}", driver='GeoJSON')

global_df = pd.DataFrame()
files = os.listdir(f"{settings.DATA_PATH}/polygons")
for file in files:
    print(file)
    df = gpd.read_file(f"{settings.DATA_PATH}/polygons/{file}")
    # df['img_date'] = df['img_date'].str.replace('-','')
    df['img_date'] = df['img_date'].str[:8]
    print(df.head())

    global_df = global_df.append(df[['img_date', 'tileID']], ignore_index=True)
global_df = global_df.drop_duplicates()
global_df.to_csv(f"{settings.DATA_PATH}/date_tile_info.csv", index=None)


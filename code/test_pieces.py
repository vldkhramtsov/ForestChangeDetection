import rasterio
import pandas as pd
import geopandas as gpd
import imageio
# import settings
import matplotlib.pyplot as plt
from rasterio.plot import reshape_as_image as rsimg

def readtiff(filename):
    src = rasterio.open(filename)
    return rsimg(src.read())


# df = pd.read_csv('../data/diff/data_info.csv')
df = pd.read_csv('../data/predictions/S2L/S2L/predictionstest_results.csv')
df = df[df['dice_score'] < 0.1]

for _, row in df.iterrows():
    img_file = f"{row['dataset_folder']}/images/{row['name']}.tiff"
    mask_file = f"{row['dataset_folder']}/masks/{row['name']}.png"
    pred_file = f"/sentinel/data/predictions/S2L/S2L/predictions/{row['name']}.png"

    image = readtiff(img_file)
    mask = imageio.imread(mask_file)
    prediction = imageio.imread(pred_file)
    plt.figure(figsize=(25, 10))
    plt.subplot(1, 5, 1)
    plt.imshow(image[:, :, 0:3])
    plt.subplot(1, 5, 2)
    plt.imshow(image[:, :, 3:6])
    plt.subplot(1, 5, 3)
    plt.imshow(image[:, :, 6:])
    plt.subplot(1, 5, 4)
    plt.imshow(mask)
    plt.subplot(1, 5, 5)
    plt.imshow(prediction)
    plt.savefig(f"./tmp/{row['name']}.png")
    plt.close()

# Forest Change Detection: Planet

## Project structure info
 * `data_prepare` - scripts for data download and preparation
 * `segmentation` - investigation about model approach, model training and model evaluation of clearcut detection


## Model Development Guide
### Data downloading

Ask developers to access the datasets (images and polygons). After retrieving the data, the structure of `data` folder should be as follows:
```
data
├── polygons
│   └── markup.geojson
├── input
│   ├── image0.tif
    └── image1.tif
```

### Data preparation
1) Create folder where the following data are stored:
   * Source subfolder stores raw data that has to be preprocess (`source`)
   * Input subfolder stores data that is used in training and evaluation (`input`)
   * Polygons subfolder stores markup (`polygons`)
   * Subfolder containing cloud maps for each image tile and land cover classification map (`auxiliary`)

2) The source folder contains folders for each image that you downloaded. In that folder you have to store TIFF images of channels (in our case, 'rgb', 'b8', 'ndvi' channels) named as f”{image_folder}\_{channel}.tif”.

3) If you have already merged bands to a single TIFF, you can just move it to `input` folder. But you have to create the folder (it may be empty) for these images in the source folder.

4) The polygons folder contains markup that you apply to all images in input folder. Polygons have to be as a single file.

#### Example of data folder structure:
```
data
├── auxiliary
│   ├── land_cover.tiff
│   ├── image0_clouds.tiff
│   └── image1_clouds.tiff
├── input
│   ├── image0.tif
│   └── image1.tif
├── polygons
│   └── markup.geojson
└── source
    ├── image0
    │   ├── image0_ndvi.tif
    │   ├── image0_b8.tif
    │   └── image0_rgb.tif
    └── image1
        ├── iamge1_ndvi.tif
        ├── image1_b8.tif
        └── image1_rgb.tif
```
5) Run preprocessing on this data. You can specify other params if it necessary (**add --no_merge if you have already merged channels with prepare_tif.py script**).
```
python preprocessing.py \
 --polys_path ../data/polygons/markup.geojson \
 --tiff_path ../data/source
 --save_path ../data/input
 --land_path ../data/auxiliary
 --clouds_path ../data/auxiliary 
```
The output of this scipt are subfolders in the `input` path, which contain divided tile images \ tile masks into the small pieces, with specified `--width` and `--height`.

#### Example of input folder structure after preprocessing:
```
input
├── image0
│   ├── geojson_polygons
│   ├── image0.png
│   ├── image_pieces.csv
│   ├── images
│   ├── masks
│   ├── clouds
│   └── landcover
├── image0.tif
├── image1
│   ├── geojson_polygons
│   ├── image1.png
│   ├── image_pieces.csv
│   ├── images
│   ├── masks
│   ├── clouds
│   └── landcover
└── image1.tif
```
6) Run data division script with specified split_function (default=’geo_split’, which divides the data with geospatial split and removes empty masks) to create train/test/val datasets.
```
python generate_data.py --markup_path ../data/polygons/markup.geojson
```

### Model training and evaluation
1) If it necessary specify augmentation in pytorch/dataset.py

2) Specify hyperparams in pytorch/train.py

3) Run training, prediction, and evaluation. Example:
```
#! /bin/bash

name=example
echo "$name"
mkdir ../data/predictions/$name
python train.py --lr 1e-3 --network unet50 --name $name --dataset_path ../data/input/ --train_df ../data/train_df.csv --val_df ../data/val_df.csv

python prediction.py --data_path ../data/input --model_weights_path ../logs/$name/checkpoints/best.pth --test_df ../data/train_df.csv --save_path ../data/predictions/$name --network unet50
python evaluation.py --datasets_path ../data/input --prediction_path ../data/predictions/$name/predictions --test_df_path ../data/train_df.csv --output_name $name'_train'


python prediction.py --data_path ../data/input --model_weights_path ../logs/$name/checkpoints/best.pth --test_df ../data/val_df.csv --save_path ../data/predictions/$name --network unet50
python evaluation.py --datasets_path ../data/input --prediction_path ../data/predictions/$name/predictions --test_df_path ../data/val_df.csv --output_name $name'_val'


python prediction.py --data_path ../data/input --model_weights_path ../logs/$name/checkpoints/best.pth --test_df ../data/test_df.csv --save_path ../data/predictions/$name --network unet50
python evaluation.py --datasets_path ../data/input --prediction_path ../data/predictions/$name/predictions --test_df_path ../data/test_df.csv --output_name $name'_test'
```

# Forest Change Detection

## Description
This is a source code repository for DEEP LEARNING FOR HIGH-FREQUENCY CHANGE DETECTION IN UKRAINIAN FOREST ECOSYSTEM WITH SENTINEL-2 (Kostiantyn Isaienkov, Michael Yushchuk, Vladislav Khramtsov, Oleg Seliverstov), 2020.

* Paper ([arXiv](https://arxiv.org/herewillbeourpaper), [Journal](https://arxiv.org/herewillbeourpaper))
* [Data](https://arxiv.org/herewillbeourdata)
* [Deforestation monitoring system](http://bit.ly/clearcutq) (for more details, see [this blog post](https://www.quantumobile.com/company/rd-blog/clearcut-segmentation-on-satellite-images-using-deep-learning/))

## Repository structure info
 * `baseline` - scripts for deforestation masks predictions with baseline models
 * `time-dependent` - scripts for forest change segmentation with time-dependent models, including Siamese, UNet-LSTM, UNet-diff, UNet3D models

## Setup
All dependencies are given in requirements.txt. Main setup configuration:
* python 3.6
* pytorch==1.4.0
* [catalyst](https://github.com/catalyst-team/catalyst)==19.05
* [segmentation_models](https://github.com/catalyst-team/catalyst)==0.1.0

Tested with Ubuntu + Nvidia GTX1080ti with Cuda==10.1. 
CPU mode also should work, but not tested.

## Dataset
You can download our datasets directly from Google drive for the baseline and time-dependent models. The image tiles from Sentinel-2, which were used for our research, are listed in [this folder](https://storage.googleapis.comdataset).

The data include *.geojson polygons:
* [baseline](https://storage.googleapis.comdataset): 2318 polygons, **36UYA** and **36UXA**, **2016-2019** years;
* [time-dependent](https://storage.googleapis.comdataset): **36UYA** (two sets of separated annotations, 278 and 123 polygons -- for spring and summer seasons respectively, **2019** year) and **36UXA** (1404 polygons, **2017-2018** years).
The files contain the following columns: `tileID` (ID of a tile, which was annotated), `img_date` (the date, at which the tile was observed), and `geometry` (polygons of deforestation regions). 

Also, we provide the set of images and masks prepared for training segmentation models as the [Kaggle dataset](https://kaggledataset).

## Training
### Reproduce results
To reproduce the results, presented in our paper, run the pipeline (download data, prepare images, train the models), as described in README files in`baseline` and `time-dependent` folders. We used the [following](https://storage.googleapis.comdataset) image tiles.
### Training with new data
To train the models with the new data, you have to create train/valid/test*csv files with specified location of images and masks, and make a minor changes in `Dataset` classes (for more information about location of these classes, see README files in `baseline` and `time-dependent` folders).

## Citation
If you use our code and/or dataset for your research, please cite our [paper](https://arxiv.org/herewillbeourpaper):

K. Isaienkov, M. Yushchuk, V. Khramtsov, O. Seliverstov, Deep learning for high-frequence change detection in Ukrainian forest ecosystem with Sentinel-2, 2020

## Questions
If you have questions after reading README, please email to [niceguy@quantumobile.com](mailto:niceguy@quantumobile.com).

data_path=/mnt/storage/cal/data/planet_forest_change_detection/sentinel_fast/diff
image_size=56
neighbours=3
epochs=200
lr=1e-2
image_size=56

network=unet18
loss=bce_dice
optimizer=Adam

head=True

name="diff_"$network"_"$optimizer"_"$loss"_"$lr"_"$head

LOGDIR="/mnt/storage/cal/artifacts/planet_forest_change_detection/models"
mkdir -p $LOGDIR

# python train.py --epochs $epochs \
#                 --image_size $image_size \
#                 --lr $lr \
#                 --network $network \
#                 --optimizer $optimizer \
#                 --loss $loss \
#                 --name $name \
#                 --dataset_path $data_path/ \
#                 --train_df $data_path/train_df.csv \
#                 --val_df $data_path/valid_df.csv \
#                 --logdir $LOGDIR \
#                 --channels rgb b8 b8a b11 b12 ndvi ndmi \
#                 --neighbours $neighbours \
#                 --classification_head $head

PRED_PATH="/mnt/storage/cal/artifacts/planet_forest_change_detection/predictions/${name}"

mkdir -p SAVE_PATH


echo "Train"
python prediction.py --classification_head $head --neighbours 3 --channels rgb b8 b8a b11 b12 ndvi ndmi --data_path $data_path --model_weights_path "${LOGDIR}/${name}/checkpoints/best.pth" --test_df "${data_path}/train_df.csv" --save_path "${PRED_PATH}/${name}" --network $network --size $image_size

echo "Valid"
python prediction.py --classification_head $head --neighbours 3 --channels rgb b8 b8a b11 b12 ndvi ndmi --data_path $data_path --model_weights_path "${LOGDIR}/${name}/checkpoints/best.pth" --test_df "${data_path}/valid_df.csv" --save_path "${PRED_PATH}/${name}" --network $network --size $image_size

echo "Test"
python prediction.py --classification_head $head --neighbours 3 --channels rgb b8 b8a b11 b12 ndvi ndmi --data_path $data_path --model_weights_path "${LOGDIR}/${name}/checkpoints/best.pth" --test_df "${data_path}/train_df.csv" --save_path "${PRED_PATH}/${name}" --network $network --size $image_size


cut=0.4
echo "Train"
python evaluation.py --datasets_path $data_path --prediction_path "${PRED_PATH}/${name}/predictions" --test_df_path $data_path/train_df.csv --output_name 'train'  --threshold $cut

echo "Test"
python evaluation.py --datasets_path $data_path --prediction_path "${PRED_PATH}/${name}/predictions" --test_df_path $data_path/test_df.csv --output_name 'test' --threshold $cut

echo "Valid"
python evaluation.py --datasets_path $data_path --prediction_path "${PRED_PATH}/${name}/predictions" --test_df_path $data_path/valid_df.csv --output_name 'val'  --threshold $cut

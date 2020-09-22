data_path="../../../data/diff"
neighbours=3
epochs=150
lr=1e-2
image_size=56

network=unet18
loss=bce_dice
optimizer=Adam

head=True

name="S2L"

LOGDIR="./LOGS"
mkdir -p "${LOGDIR}/${name}/checkpoints"


python3 train.py --epochs $epochs \
                --image_size $image_size \
                --lr $lr \
                --network $network \
                --optimizer $optimizer \
                --loss $loss \
                --name $name \
                --dataset_path $data_path/ \
                --train_df $data_path/train_df.csv \
                --val_df $data_path/valid_df.csv \
                --logdir $LOGDIR \
                --channels rgb \
                --neighbours $neighbours \
                --classification_head $head


# name="BEST"
PRED_PATH="./predictions/${name}"
mkdir -p PRED_PATH
rm -r $PRED_PATH/*

# name=BEST
echo "Train"
python3 prediction.py --classification_head $head --neighbours 3 --channels rgb --data_path $data_path --model_weights_path "${LOGDIR}/${name}/checkpoints/best.pth" --test_df "${data_path}/train_df.csv" --save_path "${PRED_PATH}/${name}" --network $network --size $image_size

echo "Valid"
python3 prediction.py --classification_head $head --neighbours 3 --channels rgb --data_path $data_path --model_weights_path "${LOGDIR}/${name}/checkpoints/best.pth" --test_df "${data_path}/valid_df.csv" --save_path "${PRED_PATH}/${name}" --network $network --size $image_size

echo "Test"
python3 prediction.py --classification_head $head --neighbours 3 --channels rgb --data_path $data_path --model_weights_path "${LOGDIR}/${name}/checkpoints/best.pth" --test_df "${data_path}/test_df.csv" --save_path "${PRED_PATH}/${name}" --network $network --size $image_size


cut=0.4
echo "Train"
python3 evaluation.py --datasets_path $data_path --prediction_path "${PRED_PATH}/${name}/predictions" --test_df_path $data_path/train_df.csv --output_name 'train'  --threshold $cut

echo "Test"
python3 evaluation.py --datasets_path $data_path --prediction_path "${PRED_PATH}/${name}/predictions" --test_df_path $data_path/test_df.csv --output_name 'test' --threshold $cut

echo "Valid"
python3 evaluation.py --datasets_path $data_path --prediction_path "${PRED_PATH}/${name}/predictions" --test_df_path $data_path/valid_df.csv --output_name 'val'  --threshold $cut

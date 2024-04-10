# Segmentation Pipeline

This package implements a machine learning pipeline for semantic segmentation on medical images. The package is a wrapper on monai and supports training and inference for UNETR and Swin-UNETR on arbitrary dataset. Development focused on BTCV(abdomen), MSD, and BRaTs datasets.

## Set up
1. Install segmentation pipeline package using 
    ```
    pip install 2404-segmentation-pipeline
    ```
2. Install pytorch.
   - If on windows
    ```
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    ```
   - If on Linux
    ```
    pip3 install torch torchvision torchaudio
    ```
3. (Optional) When working with BtCV dataset, the Swin-UNETR architecture offers self-supervised pretrained model on the dataset. When using pre-trained model before training, it allows the model to converge faster. Download the pretrained self-supervised model [here](https://github.com/Project-MONAI/MONAI-extra-test-data/releases/download/0.8.1/model_swinvit.pt)


## Documentation
Documention is provided [here](https://raw.githack.com/2404-Organ-Segmentation/segmentation-pipeline/main/docs/html/pipeline.html#pipeline.Pipeline)

## Examples
```
from pipeline Import Pipeline
from monai.transforms import (
    AsDiscrete,
    EnsureChannelFirstd,
    Compose,
    CropForegroundd,
    LoadImaged,
    Orientationd,
    RandFlipd,
    RandCropByPosNegLabeld,
    RandShiftIntensityd,
    ScaleIntensityRanged,
    Spacingd,
    RandRotate90d,
    ResizeWithPadOrCropd,
    )

# Initialize Pipeline object. Below code works for BtCV but parameters need to be changed for other datasets.
pipeline = Pipeline(model_type="UNETR", modality=1, num_of_labels=14,
                       model_path="", debug=True)

# Transformations applied on training images
train_transforms = Compose(
    [
        LoadImaged(keys=["image", "label"]),
        EnsureChannelFirstd(keys=["image", "label"]),
        Orientationd(keys=["image", "label"], axcodes="RAS"),
        Spacingd(
            keys=["image", "label"],
            pixdim=(1.5, 1.5, 2.0),
            mode=("bilinear", "nearest"),
        ),
        ScaleIntensityRanged(
            keys=["image"],
            a_min=-175,
            a_max=250,
            b_min=0.0,
            b_max=1.0,
            clip=True,
        ),
        CropForegroundd(keys=["image", "label"], source_key="image"),
        RandCropByPosNegLabeld(
            keys=["image", "label"],
            label_key="label",
            # This here needs to be negative
            spatial_size=(96, 96, -1),
            pos=1,
            neg=1,
            num_samples=4,
            image_key="image",
            image_threshold=0,
        ),
        ResizeWithPadOrCropd(keys=["image", "label"],
            spatial_size=(96, 96, 96),
            mode='constant'
        ),
        RandFlipd(
            keys=["image", "label"],
            spatial_axis=[0],
            prob=0.10,
        ),
        RandFlipd(
            keys=["image", "label"],
            spatial_axis=[1],
            prob=0.10,
        ),
        RandFlipd(
            keys=["image", "label"],
            spatial_axis=[2],
            prob=0.10,
        ),
        RandRotate90d(
            keys=["image", "label"],
            prob=0.10,
            max_k=3,
        ),
        RandShiftIntensityd(
            keys=["image"],
            offsets=0.10,
            prob=0.50,
        ),
    ]
)

# Transformation applied on validation images
val_transforms = Compose(
    [
        LoadImaged(keys=["image", "label"]),
        EnsureChannelFirstd(keys=["image", "label"]),
        Orientationd(keys=["image", "label"], axcodes="RAS"),
        Spacingd(
            keys=["image", "label"],
            pixdim=(1.5, 1.5, 2.0),
            mode=("bilinear", "nearest"),
        ),
        ScaleIntensityRanged(keys=["image"], a_min=-175, a_max=250, b_min=0.0, b_max=1.0, clip=True),
        CropForegroundd(keys=["image", "label"], source_key="image"),
    ]
)

# Initialize training
trainer.train(150,10)

# Transformations applied on images for inferencing. Transformation should be similar to val_transform
inf_transforms = Compose(
    [
        LoadImaged(keys=["image"]),
        EnsureChannelFirstd(keys=["image"]),
        Orientationd(keys=["image"], axcodes="RAS"),
        Spacingd(
            keys=["image"],
            pixdim=(1.5, 1.5, 2.0),
            mode="bilinear",
        ),
        ScaleIntensityRanged(keys=["image"], a_min=-175, a_max=250, b_min=0.0, b_max=1.0, clip=True),
        CropForegroundd(keys=["image"], source_key="image"),
    ]
)

# Inference
trainer.inference(data_folder = 'path/to/inference/data/folder', output_folder="path/to/output/folder", transforms=inf_transforms)
```


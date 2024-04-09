from monai.networks.nets import SwinUNETR, UNETR
from monai.data import load_decathlon_datalist, CacheDataset, set_track_meta, ThreadDataLoader, \
    decollate_batch, DataLoader
from monai.transforms import (
    AsDiscrete,
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
    EnsureTyped,
    EnsureChannelFirstd,
    Activationsd,
    Invertd,
    AsDiscreted,
    SaveImaged,
    KeepLargestConnectedComponentd,
    Affined,
)
from monai.config import print_config
from monai.metrics import DiceMetric
from monai.losses import DiceCELoss
from monai.inferers import sliding_window_inference
import torch
import re
import nibabel as nib
import os
import matplotlib.pyplot as plt
from tqdm import tqdm
import json
import scipy.ndimage as ndimage
from torch.utils.tensorboard import SummaryWriter
from datetime import datetime
import math
import numpy as np
from monai import data

UNETR_transforms = Compose(
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


# TODO: Add transforms that were used for swinunetr model training


class Pipeline:

    def __init__(self, model_type: str, modality: int, num_of_labels: int, model_path: str = None,
                 data_folder: str = None, debug: bool = False, training: bool = False):
        """! Parent constructor for model prediction. Defines the model type that is used as well as the paths for
        loading the pretrained model, loading and saving the data

        @:param model: The model that is going to be used for predictions. Should be monai UNETR or SwinUNETR.
        @:param model_path: The path to the pretrained model as a string. Should include the model .pth file.
        @:param data_folder: The folder where the data is located as string. All files in this folder should be medical
        images.
        @:param debug: Boolean that enables debug messages. Defaults to false to disable messages.
        @:return None
        """
        os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if training is False and data_folder is not None and model_path is not None:
            self.val_loader = None
            self.debug_mode = debug

            self.file_dicts = []
            self.files = []
            self.__load_inference_dataset(data_folder)
            self.create_model(model_type=model_type, modality=modality, num_of_labels=num_of_labels,
                              model_path=model_path)
            self.model.eval()

    def create_model(self, model_type: str, modality: int, num_of_labels: int, model_path: str = ""):
        """
        Creates a new model for the pipeline

        Args:
            model_type (str): Type of model the pipeline uses, takes value "UNETR" or "SWINUNETR"
                              for their respective model types.
            modality (int): Modality of the dataset. Determines the input dimension of the model.
            num_of_labels (int): Number of labels to the dataset.
            model_path (str): File path to the saved model of the same type as model_type.
        """

        self.model_type = model_type
        if model_type == "UNETR":
            self.model = UNETR(
                in_channels=modality,
                out_channels=num_of_labels,
                img_size=(96, 96, 96),
                feature_size=16,
                hidden_size=768,
                mlp_dim=3072,
                num_heads=12,
                pos_embed="perceptron",
                norm_name="instance",
                res_block=True,
                dropout_rate=0.0
            ).to(self.device)
        elif model_type == "SWINUNETR":
            self.model = SwinUNETR(
                img_size=(96, 96, 96),
                in_channels=modality,
                out_channels=num_of_labels,
                feature_size=48,
                use_checkpoint=True,
            ).to(self.device)
            self.model.load_from(torch.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                         "model_swinvit.pt")))
        else:
            raise Exception("Unexpected model type given")

        if model_path != "":
            self.model.load_state_dict(torch.load(model_path))

    def load_model(self, model_path: str):
        """
        Load the saved model.

        Args:
            model_path (str): File path to the saved model of the same type as model_type.
        """
        self.model.load_state_dict(torch.load(model_path))

    def load_data(self, dataset_path: str, train_transforms, val_transforms, cache_num_train: int = 24,
                  train_batch_size: int = 1, cache_num_val: int = 6, val_batch_size: int = 1, workers: int = 4):
        """
        Load the training and validation data from the json file for the dataset.

        Args:
            dataset_path (str): File path to the json file of the dataset.
            train_transforms: Transformation done on the dataset during training.
            val_transforms: Transformation done on the dataset during validation.
            cache_num_train (int): Number of cached data for training dataset.
            train_batch_size (int): Batch size for training.
            cache_num_val (int): Number of cached data for validation dataset.
            val_batch_size (int): Batch size for validation.
            workers (int): Number of workers working in parallel.
        """
        datalist = load_decathlon_datalist(dataset_path, True, "training")
        val_files = load_decathlon_datalist(dataset_path, True, "validation")
        train_ds = CacheDataset(
            data=datalist,
            transform=train_transforms,
            cache_num=cache_num_train,
            cache_rate=1.0,
            num_workers=workers,
        )
        train_loader = DataLoader(train_ds, batch_size=train_batch_size, shuffle=True, num_workers=workers,
                                  pin_memory=True)
        val_ds = CacheDataset(data=val_files, transform=val_transforms, cache_num=cache_num_val, cache_rate=1.0,
                              num_workers=workers)
        val_loader = DataLoader(val_ds, batch_size=val_batch_size, shuffle=False, num_workers=workers, pin_memory=True)

        f = open(dataset_path)
        json_data = json.load(f)

        self.modality = len(json_data['modality'])
        self.num_of_labels = len(json_data['labels'])
        self.dataset_name = json_data['name']

        self.num_train_images = len(train_ds)
        self.num_val_images = len(val_ds)

        self.train_batch_size = train_batch_size

        self.val_loader = val_loader
        self.train_loader = train_loader

    def train(self, max_epoch: int, epoch_val: int, learning_rate: float = 1e-4, weight_decay: float = 1e-5):
        torch.backends.cudnn.benchmark = True
        loss_function = DiceCELoss(to_onehot_y=True, softmax=True)
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate, weight_decay=weight_decay)
        scaler = torch.cuda.amp.GradScaler()

        max_iterations = math.ceil(max_epoch * self.num_train_images / self.train_batch_size)
        eval_num = math.ceil(epoch_val * self.num_train_images / self.train_batch_size)
        post_label = AsDiscrete(to_onehot=self.num_of_labels)
        post_pred = AsDiscrete(argmax=True, to_onehot=self.num_of_labels)

        dice_metric = DiceMetric(include_background=True, reduction="mean", get_not_nans=False)

        save_folder = self.model_type + self.dataset_name + str(datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        os.makedirs(save_folder)
        os.makedirs(save_folder + "/logs")
        writer = SummaryWriter(save_folder + '/logs/{}'.format(datetime.now().strftime("%Y_%m_%d")))

        global_step = 0
        dice_val_best = 0.0
        global_step_best = 0
        epoch_loss_values = []
        metric_values = []

        def __validation(epoch_iterator_val):
            self.model.eval()
            with torch.no_grad():
                for batch in epoch_iterator_val:
                    val_inputs, val_labels = (batch["image"].cuda(), batch["label"].cuda())
                    with torch.cuda.amp.autocast():
                        val_outputs = sliding_window_inference(val_inputs, (96, 96, 96), 4, self.model)
                    val_labels_list = decollate_batch(val_labels)
                    val_labels_convert = [post_label(val_label_tensor) for val_label_tensor in val_labels_list]
                    val_outputs_list = decollate_batch(val_outputs)
                    val_output_convert = [post_pred(val_pred_tensor) for val_pred_tensor in val_outputs_list]

                    # Calculate metrics
                    dice_metric(y_pred=val_output_convert, y=val_labels_convert)

                    epoch_iterator_val.set_description(
                        "Validate (%d / %d Steps)" % (global_step, max_iterations))  # noqa: B038
                mean_dice_val = dice_metric.aggregate().item()

                dice_metric.reset()

            return mean_dice_val

        def __train(global_step, train_loader, dice_val_best, global_step_best):
            self.model.train()
            epoch_loss = 0
            step = 0
            epoch_iterator = tqdm(train_loader, desc="Training (X / X Steps) (loss=X.X)", dynamic_ncols=True)
            for step, batch in enumerate(epoch_iterator):
                step += 1
                x, y = (batch["image"].cuda(), batch["label"].cuda())
                with torch.cuda.amp.autocast():
                    logit_map = self.model(x)
                    loss = loss_function(logit_map, y)
                scaler.scale(loss).backward()
                epoch_loss += loss.item()
                scaler.unscale_(optimizer)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad()
                epoch_iterator.set_description(  # noqa: B038
                    f"Training ({global_step} / {max_iterations} Steps) (loss={loss:2.5f})"
                )

                if (global_step % eval_num == 0 and global_step != 0) or global_step == max_iterations:
                    epoch_iterator_val = tqdm(self.val_loader, desc="Validate (X / X Steps) (dice=X.X)",
                                              dynamic_ncols=True)
                    dice_val = __validation(epoch_iterator_val)
                    epoch_loss /= step
                    epoch_loss_values.append(epoch_loss)
                    metric_values.append(dice_val)
                    if dice_val > dice_val_best:
                        dice_val_best = dice_val
                        global_step_best = global_step

                    torch.save(self.model.state_dict(),
                               os.path.join(save_folder,
                                            self.model_type + self.dataset_name + str(global_step) + ".pth"))
                    print(
                        "Model Was Saved ! Current Best Avg. Dice: {} Current Avg. Dice: {}".format(dice_val_best,
                                                                                                    dice_val)
                    )
                    # Record metric with tensorboard
                    writer.add_scalar("Dice Val", dice_val, global_step=global_step)
                    writer.add_scalar("Dice Cross Entropy Loss", epoch_loss, global_step=global_step)
                global_step += 1
            return global_step, dice_val_best, global_step_best

        while global_step < max_iterations:
            global_step, dice_val_best, global_step_best = __train(global_step, self.train_loader, dice_val_best,
                                                                   global_step_best)

        writer.close()

    def inference(self, output_folder) -> None:
        """! Runs the prediction on the files located under self.data_folder, will save the files as Nifti (.nii.gz)
        format under output_folder. If output_folder is not specified, then it will be saved to the folder where the
        data was originally taken from.

        @:param output_folder: The folder path to save the nifti images as a string. If None, then it will save to the
        folder where the data files are located. (self.data_folder)
        @:return None
        """

        counter = 0
        with torch.no_grad():
            for i, test_data in enumerate(self.val_loader):
                # Make prediction
                img = test_data["image"].to(self.device)
                test_data["pred"] = sliding_window_inference(img, (96, 96, 96), 4, self.model, overlap=0.8)

                # Post-processing transforms
                # Source: https://github.com/MASILab/3DUX-Net/tree/14ea46b7b4c4980b46aba066aaaa24b1d9c1bb0d
                post_transforms = Compose([
                    EnsureTyped(keys="pred"),
                    Activationsd(keys="pred", softmax=True),
                    Invertd(
                        keys="pred",  # invert the `pred` data field, also support multiple fields
                        transform=UNETR_transforms,
                        orig_keys="image",
                        # get the previously applied pre_transforms information on the `img` data field,
                        # then invert `pred` based on this information. we can use same info
                        # for multiple fields, also support different orig_keys for different fields
                        meta_keys="pred_meta_dict",  # key field to save inverted meta data, every item maps to `keys`
                        orig_meta_keys="image_meta_dict",
                        # get the meta data from `img_meta_dict` field when inverting,
                        # for example, may need the `affine` to invert `Spacingd` transform,
                        # multiple fields can use the same meta data to invert
                        meta_key_postfix="meta_dict",
                        # if `meta_keys=None`, use "{keys}_{meta_key_postfix}" as the meta key,
                        # if `orig_meta_keys=None`, use "{orig_keys}_{meta_key_postfix}",
                        # otherwise, no need this arg during inverting
                        nearest_interp=False,
                        # don't change the interpolation mode to "nearest" when inverting transforms
                        # to ensure a smooth output, then execute `AsDiscreted` transform
                        to_tensor=True,  # convert to PyTorch Tensor after inverting
                    ),
                    AsDiscreted(keys="pred", argmax=True),
                    KeepLargestConnectedComponentd(keys='pred', applied_labels=[1, 3]),
                    SaveImaged(keys="pred", meta_keys="pred_meta_dict", output_dir=output_folder,
                               output_postfix="temp", output_ext=".nii.gz", resample=True, separate_folder=False),
                ])
                test_data = [post_transforms(j) for j in decollate_batch(test_data)]

                # Small modification to affine matrix
                self.__load_and_translate(output_folder=output_folder, file_name=self.files[counter])
                counter += 1

    def __load_inference_dataset(self, data_folder: str) -> None:
        """! Loads and preprocesses the data specified in under data_folder. Will save the data as a Monai
        Dataloader and apply the relevant transforms that were used for training.

        @:param data_folder: Path as a string to the folder where the medical images to be segmented are located.
        @:return None
        """

        self.__load_files_from_folder(data_folder)
        test_dataset = data.Dataset(data=self.file_dicts, transform=UNETR_transforms)
        self.val_loader = data.DataLoader(
            test_dataset,
            batch_size=1,
            shuffle=False,
            num_workers=4,
            pin_memory=True,
        )

    def __load_files_from_folder(self, data_folder: str) -> None:
        """! Loads the files into a list of dictionaries to be read by Monai's built in dataset. This needs to be
        formatted in this specific way so the transforms can be properly applied (the transforms are expecting specific
        keys). The files that are loaded are all the files in the folder specified by data_folder. This is a mock
        of Monai's load_decathlon_datalist().

        @:param data_folder: Path as a string to the folder where the medical images to be segmented are located.
        @:return None
        """
        self.file_dicts.clear()
        self.files.clear()

        for root, dirs, files in os.walk(data_folder):
            for file in files:
                file_path = os.path.join(root, file)
                image_dict = {
                    "image": file_path,
                }
                self.files.append(file)
                self.file_dicts.append(image_dict)

    def __debug(self, message: str) -> None:
        """! Debug print statements, allows debug messages to be sent if self.debug_mode is True.

        @:param message: The message that is sent
        @:return None
        """
        if self.debug_mode:
            print(message)
        return None

    def __load_and_translate(self, output_folder, file_name) -> None:
        """! Helper function that loads the saved file from monai and applies the necessary affine matrix modifications
        to it, then deletes the temporary monai file and saves as the proper nifti file.

        @:param output_folder: The path to the folder that contains the temporary monai saved file.
        @:param file_name: The name of the file that was being analyzed.
        @:return None
        """
        temp_name = re.sub(r"\.nii\.gz$", "_temp.nii.gz", file_name)
        temp_file_path = os.path.join(output_folder, temp_name)
        seg_img = nib.load(temp_file_path)
        self.__debug(f"segm affine is {seg_img.affine}")
        self.__debug(f"segm shape is {seg_img.shape}")

        new_affine = seg_img.affine
        new_affine[:3, 3] = [0, 0, 0]
        new_affine[1, 1] = -1 * new_affine[1, 1]
        self.__debug(f"New affine is {new_affine}")

        new_name = re.sub(r"\.nii\.gz$", "-segmented.nii.gz", file_name)

        nib.save(
            nib.Nifti1Image(seg_img.get_fdata(), affine=new_affine),
            os.path.join(output_folder, new_name)
        )

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            self.__debug(f"File '{temp_file_path}' deleted successfully")
        else:
            self.__debug(f"File '{temp_file_path}' does not exist")


if __name__ == "__main__":
    # Only run this file directly for debugging
    trainer = Pipeline(model_type="UNETR", modality=1, num_of_labels=14,
                       model_path="./pretrained_models/best_metric_model_3dUNETR52200.pth", data_folder="./testing",
                       debug=True)
    trainer.inference(output_folder="./testing")


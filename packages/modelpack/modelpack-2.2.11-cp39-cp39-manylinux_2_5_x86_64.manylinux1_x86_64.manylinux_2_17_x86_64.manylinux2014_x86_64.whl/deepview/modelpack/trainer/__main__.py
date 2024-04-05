# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from enum_actions import enum_action
from deepview.modelpack.callbacks import ModelPackTrainingCallback
import numpy as np
from deepview.modelpack.losses import ModelPackLoss
from deepview.modelpack.models import UpsampleMethod
from deepview.modelpack.schedulers import WarmUpCosineDecay
from deepview.modelpack.models import ModelPackDetector
from deepview.validator.runners.keras import InferenceKerasModel
from deepview.validator.evaluators import DetectionEval
from deepview.modelpack.callbacks.tensorboard import TensorBoard
from deepview.modelpack.datasets import get_detection_dataset
from deepview.modelpack.trainer.detection import DetectionTrainer
from deepview.modelpack import version as modelpack_version
from yaml import safe_load as load_yaml, safe_dump as save_yaml
import tensorflow as tf
import argparse
import os.path
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Avoid TF messages on the terminal


def validate_task(
        task: str = None
):
    """
    Validates task name

    Parameters
    ----------
    task: str, default None
        Name of the task

    Returns
    -------
        task: str

    Raises
    -------
    ValueError
        If task is different to ``detection``,  ``segmentation`` or ``multitask``

    """
    tasks = [
        'detection',
        'detect',
        'segmentation',
        'segment',
        "attitude",
        "head-pose",
        'detect-and-segment',
        'segment-and-detect',

    ]

    task = task.lower()
    if task is None or task not in tasks:
        raise ValueError(
            "Invalid ``task`` was provided: {} is not a valid ``task``. Use either of {}".format(
                task, tasks
            )
        )
    return task


def validate_weights(
        weights: str = None
):
    """
    Validates the initialization weights parameter value

    Parameters
    ----------
    weights: str, default None
        This parameter can be either, ``coco`` or path to the keras file

    Returns
    -------
    weights: str

    Raises
    ----------
    ValueError
        In case weights file does not exist or weights is different to ``coco``
    """
    if weights is None:
        weights = 'coco'

    if weights != 'coco' and not os.path.exists(weights):
        raise ValueError("Invalid ``weights``, file does not exist at: {}".format(
            weights
        ))

    return weights


def validate_shape(
        shape: list = None
):
    """
    This function validates the shape is in a correct way.
    Valid shapes are the following: ``[x,3] -> [x, x, 3]``,
    ``[h,w] -> [h, w, 3]`` and ``[h, w, 3] -> [h, w, 3]``

    Parameters
    ----------
    shape: list = None

    Returns
    -------
    shape: List

    Raises
    -------
    ValueError if shape is unsupported
    """
    if shape is None or len(shape) == 0:
        raise ValueError(
            "A valid shape should be different than ``None`` and without 0-length")

    if len(shape) == 2 and shape[1] == 3:
        shape = [shape[0], shape[1], 3]

    if len(shape) == 2 and shape[1] != 3:
        shape = [shape[0], shape[1], 3]

    if shape[2] != 3:
        raise ValueError(
            "ModelPack trainer only accepts RGB images with 3 channels")

    for val in shape:
        if val <= 0:
            raise ValueError(
                "A valid shape must have all the dimensions larger than 0")

    return shape


def validate_epochs(
        epochs: int = 0
):
    """
    This function validates the number of epochs is correct. It should be a positive number larger than 0

    Parameters
    ----------
    epochs: int, default 0
        Number of epochs to train the model

    Returns
    -------
    epochs: int

    Raises
    -------
    ValueError if epochs is <= 0
    """

    if epochs > 0:
        return epochs

    raise ValueError("Invalid number of epochs was provided. Model can't be trained during {} epochs".format(
        epochs
    ))


def validate_batch_size(
        bsize: int = 0
):
    """
    This function validates the number of instances per batch is correctly set. It should be a positive
    number larger than 0

    Parameters
    ----------
    bsize: int, default 0
        Number of elements per batch

    Returns
    -------
    bsize: int


    Raises
    -------
    ValueError if bsize is <= 0
    """

    if bsize and bsize > 0:
        return bsize

    raise ValueError("Invalid batch size was provided. Instances can't be batched when batch-size is ``{}``".format(
        bsize
    ))


def validate_optimizer_params(
        opt_params: dict = None
):
    """
    This function validates all the configurations for optimizers were correct. If one parameter is not ser
    it will take the default value

    Parameters
    ----------
    opt_params: dict, default None
        Python dictionary that describes the optimizer configuration and parameters

    Returns
    -------
    opt_params: dict
        A valid parameters for optimizers

    Raises
    -------
        ValueError if the parameters are incorrectly set.

    """
    return opt_params


def validate_metric(
        metric: str = None
):
    """
    This function validate the metric name used to save checkpoints is correct

    Parameters
    ----------
    metric: str
    Name of the metric. Either of ``acc``, ``map`` or ``recall``

    Returns
    -------
    metric: str

    Raises
    -------
    ValueError
    This function raises a ValueError exception if the metric does not exist
    """
    if metric.lower() in ["acc", "map", "recall"]:
        return metric.lower()

    raise ValueError("Invalid metric was provided at: {}".format(
        metric
    ))


def validate_loss_weights_for_detection(
        loss_weights: dict = None
):
    """
    This function validates the weights for each loss. In case the loss weights are missing, we are going
    to use 1.0 by default

    Parameters
    ----------
    loss_weights: dict, default None
        Dictionary describing the weights for each loss function. Default dictionary for weights is:
        ``{'w_obj': 1.0,'w_cls': 1.0,'w_loc': 1.0}``. If one of the keys is not present, 1.0 will be
        taken in its place

    Returns
    -------
    loss_weights: dict
        Dictionary containing the weights for the losses

    """

    w_obj = loss_weights.get('w_obj', 1.0)
    w_cls = loss_weights.get('w_cls', 1.0)
    w_loc = loss_weights.get('w_loc', 1.0)

    return {
        'w_obj': w_obj,
        'w_cls': w_cls,
        'w_loc': w_loc
    }


def validate_thresholds(
        iou_threshold: float = 0.45,
        score_threshold: float = 0.35
):
    """
    This function validates the thresholds used during validation. They will only affect validation results.
    If either of the values are not in the range between 0..1, defaults values will be set to:
    ``iou_threshold = 0.45, score_threshold = 0.35``

    Parameters
    ----------
    iou_threshold: float, defaults 0.45
        IoU threshold used for NMS
    score_threshold: float, default 0.35
        score_threshold used for NMS

    Returns
    -------
    (iou_threshold, score_threshold): Tuple
        The thresholds

    """

    if 0 < iou_threshold < 1 and 0 < score_threshold < 1:
        return iou_threshold, score_threshold
    else:
        return 0.45, 0.35


def validate_display(
        display: int = 10
):
    """
    This function validates the number of samples to be shown in TensorBoard during training the model

    Parameters
    ----------
    display: int, default 10
        Number of samples to be display

    Returns
    -------
        display: int

    """
    if display < 0:
        return -1
    else:
        return display


def validate_augmentation(
        augmentation: dict = None
):
    """
    This function validates the augmentation techniques are properly scored with probabilities in the 0..1 range

    Parameters
    ----------
    augmentation: dict, default None

    Returns
    -------
    augmentation: dict

    """

    return augmentation


def validate_dataset(
        dataset: str = None
):
    """
    This funciton validates the path to the yaml file exists

    Parameters
    ----------
    dataset: str, default None

    Returns
    -------
    dataset: str
        Path to the dataset

    Raises
    -------
    FileNotFoundError
        this function will raise an exception if the dataset description file is not found in the given location

    """
    if dataset and os.path.exists(dataset):
        return dataset
    else:
        raise FileNotFoundError("The dataset file was not found in the given location: ``{}``".format(
            dataset
        ))


def get_optimizer(
        optimizer_config: dict = None,
        steps: int = 0,
        epochs: int = 0
):
    """
    This function builds the optimizer from the configuration dictionary.
    The optimizer is built from the following dictionary

    ``{
            "method": "adam",
            "learning-rate": args.initial_lr,
            "strategy": {
                "name": "exponential" if args.exponential_decay > 0 else "warmup",
                "parameters": {
                    "decay": args.exponential_decay,
                    "warmup-learning-rate": args.warmup_lr,
                    "warmup-epochs": 0 if args.warmup_epochs < 1 else args.warmup_epochs
                }
            }
    ``}

    Parameters
    ----------
    optimizer_config: dict, default None
        Configuration that defines the optimizer
    steps: int, default 0
        Number of steps per epoch
    epochs: int, default 0
        Number of epochs

    Returns
    -------
    optimizer: tf.keras.optimizers.Optimizer

    Raises
    ------
    ValueError if ``method != adam``
    """

    method = optimizer_config.get("method", None)
    if method is None or method != 'adam':
        raise ValueError("Provided optimizer is not supported: ``{}`` was provided".format(
            method
        ))

    scheduler_strategy = optimizer_config.get("strategy").get("name")
    if scheduler_strategy not in ['warmup', 'exponential']:
        raise ValueError("Unsupported scheduler was provided: ``{}`` is not supported".format(
            scheduler_strategy
        ))

    num_steps = epochs * steps
    warmup_epoch = optimizer_config.get("strategy").get(
        "parameters").get("warmup-epochs")
    warmup_lr = optimizer_config.get("strategy").get(
        "parameters").get("warmup-learning-rate")
    warmup_steps = int(warmup_epoch * steps)
    initial_lr = optimizer_config.get("learning-rate")

    if scheduler_strategy == 'warmup':
        scheduler = WarmUpCosineDecay(
            start_lr=warmup_lr,
            target_lr=initial_lr,
            warmup_steps=warmup_steps,
            total_steps=num_steps,
            hold=warmup_steps
        )
    else:
        decay = optimizer_config.get("strategy").get("parameters").get("decay")
        scheduler = tf.keras.optimizers.schedules.ExponentialDecay(
            initial_lr,
            decay_steps=int(decay * steps),
            decay_rate=0.96,
            staircase=True
        )
    optimizer = tf.keras.optimizers.Adam(learning_rate=scheduler)
    return optimizer


def register_parameter(key, value):
    try:
        import mlflow
        if mlflow.active_run():
            mlflow.log_param(key=key, value=value)
    except ImportError:
        pass

def train_detection(
    from_config: dict = None,
    dvclive_output=None,
    callbacks=None
):
    """
    This function trains a detection model using ModelPack API

    Parameters
    ----------
    from_config: dict, default None

    Returns
    -------
    None

    """

    """
    Reading the weights parameters and validate them. In case the weights are not ``coco`` or a valid path,
    a ValueError will be risen by ``validate_weights`` function
    """

    weights = from_config.get("weights", None)
    weights = validate_weights(
        weights=weights
    )

    register_parameter("weights", weights)

    """
    Reads the shape values and validates they are correct. Otherwise a ValueError will be raise by ``validate_shape``
    function. Shape values must be positive, and returned as a python list. Nuber of channels must be 3
    and width and height different than 0

    """
    shape = from_config.get("shape", None)
    shape = validate_shape(
        shape=shape
    )
    register_parameter("shape", shape)

    """
    Reading the epochs from the configuration object. In case the epochs is 0 or any negative number,
    the function ``validate_epochs`` will raise a ValueError exception
    """
    epochs = from_config.get("epochs", None)
    epochs = validate_epochs(
        epochs=epochs
    )
    register_parameter("epochs", epochs)

    """
    Reading the batch size from the configuration object. In case the batch size is 0 or any negative number,
    the function ``validate_batch_size`` will raise a ValueError exception
    """
    bsize = from_config.get("batch-size", None)
    bsize = validate_batch_size(
        bsize=bsize
    )
    register_parameter("batch-size", bsize)

    """
    Inspect optimizer parameters.
    """
    opt_params = from_config.get("optimizer", None)
    opt_params = validate_optimizer_params(
        opt_params=opt_params
    )
    register_parameter("opt_params", opt_params)

    """
    Inspect the metric name used for evaluation exists. The name should be either of
    map, acc or recall. Otherwise the function  ``validate_metric`` will raise
    a ValueError exception
    """
    metric = from_config.get("metric", None)
    metric = validate_metric(
        metric=metric.lower()
    )
    register_parameter("validation-metric", metric)

    """
    Here the weights used to penalty the three different losses are validated and parsed
    (classification loss, objectness loss and localization loss)
    """
    loss_weights = from_config.get('loss_weights', None)
    loss_weights = validate_loss_weights_for_detection(
        loss_weights=loss_weights
    )
    register_parameter("loss_weights", loss_weights)

    """
    Before start validating the model, we need to configure preprocessing parameters.
    This section reads the NMS parameters from the global configuration object.
    IoU threshold and Score threshold
    """
    iou_threshold = from_config.get('validation').get('iou', None)
    score_threshold = from_config.get('validation').get('score', None)
    iou_threshold, score_threshold = validate_thresholds(
        iou_threshold=iou_threshold,
        score_threshold=score_threshold
    )
    register_parameter("iou_threshold", iou_threshold)
    register_parameter("score_threshold", score_threshold)

    """
    This parameter is used to limit the number of sample images we are going to send to TensorBoard
    after each epoch is validated.
    """
    display = from_config.get('display', 10)
    display = validate_display(
        display=display
    )
    register_parameter("display", display)

    """
    In this section the occurrence frequency is parsed from the global configuration object.
    ``augmentation`` key contains a dictionary to index technique name and frequency, a value
    from 0..1.
    """
    augmentation = from_config.get('augmentation', None)
    augmentation = validate_augmentation(
        augmentation=augmentation
    )
    register_parameter("augmentation", augmentation)

    """
    In order to reduce the number of False Positives when training the model, sometimes is beneficial to
    fake the background without annotations. To do this, we need to insert a new class with index 0 into
    our problem.
    """
    use_fake_background_class = from_config.get('use_fake_background', True)
    register_parameter("add-background-class", use_fake_background_class)

    """
    With this parameter ModelPack will pay more attention on objects depending on the size.
    Anchors will be more adjusted to the size of the objects and the average will be weighted
    towards the parameter direction. For example, if our dataset is prune to have small objects,
    large objects can be seen like outliers and they can be relaxed in some extent. This means the
    anchors will be computed using weights to be more accurate when detecting small objects.
    """
    objects_size = from_config.get('objects-size', 'large')
    register_parameter("objects-size", objects_size)

    """
    When encoding the ground truth boxes, it is needed to specify the IoU value
    to make the right match between anchors and bounding boxes.
    By default the model is using 0.3.
    For some datasets, an small IoU could make our model predicts a lot of duplicated boxes,
    On the other hand, a higher IoU could make our model has a poor detection rate.
    """

    encoding_iou = from_config.get("encoding_iou", 0.3)
    register_parameter("encoding-iou", encoding_iou)

    """
    Reading the path to the dataset. In this case we are reading the path to the *.yaml file
    """
    dataset = from_config.get("dataset", None)
    dataset = validate_dataset(
        dataset=dataset
    )
    register_parameter("dataset", dataset)

    """
    Defining the ModelPack detector handler. This instance will be able to perform all the operations
    needed to configure the model at a given input resolution (anchors, strides, etc.)
    """
    model_handler = ModelPackDetector()
    model_handler.encoding_iou = encoding_iou

    """
    Read the decoder we are going to use for our model: Exponential or Power
    """
    use_power_decoder = from_config.get('use_power_decoder', False)

    register_parameter(
        "decoder",
        "power" if use_power_decoder else "exponential"
    )

    if use_power_decoder:
        model_handler.use_power_decoder()

    """
    Getting the dataset iterators
    """

    train_ds, validation_ds, [
        num_train_samples,
        num_validation_samples,
        classes
    ], ds_handler = get_detection_dataset(
        dataset=dataset,
        shape=shape,
        batch_size=bsize,
        letterbox=False,
        add_bkg_class=use_fake_background_class,
        aug_cfg=augmentation,
        new_aug_pipeline=None,
    )
    # background class is included if use_fake_background_class is se tto True
    num_classes = len(classes)

    register_parameter("classes", classes)
    register_parameter("num-classes", num_classes)
    register_parameter("num-train-samples", num_train_samples)
    register_parameter("num-val-samples", num_validation_samples)

    """
    In this section of the code, we deactivate the augmentation techniques in order to compute anchors
    over the real dataset and not over the synthetic one generated by augmentation techniques.
    Anchors are automatically set as a class attribute and augmentation is enable again in order to
    use them while training the model
    """

    compute_anchors = from_config.get("compute-anchors", False)
    anchors_file = from_config.get("anchors", None)
    save_anchors = from_config.get("save-anchors", None)

    anchors = None

    if compute_anchors:
        ds_handler.augment = False
        model_handler.precompute_anchors(train_ds, objects_size)
        ds_handler.augment = True
        anchors = model_handler.get_specific_anchors()

        if save_anchors and not os.path.exists(save_anchors):
            is_yaml = os.path.splitext(save_anchors)[1] == ".yaml"
            if is_yaml:
                import yaml

                # read yaml file content
                with open(anchors_file) as fp:
                    content = yaml.safe_load(fp)

                # append new anchors
                content['anchors'] = anchors.flatten().tolist()

                # save anchors
                with open(save_anchors, 'w') as fp:
                    yaml.safe_dump(
                        anchors,
                        fp,
                        allow_unicode=True,
                        encoding='utf-8'
                    )
            else:
                with open(save_anchors, 'w') as fp:
                    str_anchors = " ".join(str(item)
                                           for item in anchors.flatten())
                    fp.write(str_anchors)

    if anchors_file and os.path.exists(anchors_file):
        if save_anchors and anchors is None:
            raise RuntimeError(
                "\t - [ERROR] To compute anchors utilize --compute-anchors option"
            )

        is_yaml = os.path.splitext(anchors_file)[1] == ".yaml"
        if is_yaml:
            import yaml

            with open(anchors_file) as fp:
                content = yaml.safe_load(fp)
                anchors = content.get("anchors", None)
        else:
            anchors = [float(x) for x in open(
                anchors_file, 'r').readline().rstrip().split(' ')]

        if anchors:
            anchors = np.asarray(anchors).reshape(2, 3, 2)

    if anchors is None:
        if os.path.exists("params.yaml"):
            import yaml
            with open(anchors_file) as fp:
                content = yaml.safe_load(fp)
                anchors = content.get("anchors", None)
            if anchors:
                anchors = np.asarray(anchors).reshape(2, 3, 2)
            else:
                ds_handler.augment = False
                model_handler.precompute_anchors(train_ds, objects_size)
                ds_handler.augment = True
                ds_handler.store_anchors(
                    anchors=model_handler.get_specific_anchors())
                anchors = model_handler.get_specific_anchors()
    else:
        model_handler.set_specific_anchors(anchors=anchors)

    """
    Enable the focus input layer optimization
    """
    focus = from_config.get("focus", "False")

    """
    This section of the code uses all the precomputed attributes for the
    current dataset and builds a keras model. The resulting model, is used for
    the Trainer for running the trining sessions
    """
    freeze_bn = from_config.get("freeze-bn", False)
    decay = from_config.get("weight-decay", 1e-5)
    freeze_backbone = from_config.get("freeze-backbone", False)
    upsample = from_config.get("upsample", UpsampleMethod.RESIZE)

    trainable_model = model_handler.get_detection_model(
        input_shape=shape,
        num_classes=num_classes,
        weights=weights,
        named_params={
            'objects_size': objects_size,
            "focus": focus,
            "batch-norm": "frozen" if freeze_bn else "trainable",
            "weight-decay": decay,
            "freeze-backbone": str(freeze_backbone).lower(),
            "upsample": upsample
        },
        upsample=upsample
    )

    """
    Loss function needs to be created by calling its own handler.
    After calling the constructor of the class, the next step we must do is to make a late initialization of the loss
    function with the custom configuration of the trainable_model. For that we need to call the
    ``model_handler.get_loss_named_params()`` function and pass the result as input of ``loss.set_named_params()``
    Finally, the loss function needs to know how to weight each loss during the computation of total-loss
    """

    loss = ModelPackLoss()
    loss.set_named_params(model_handler.get_loss_named_params())
    loss.set_weights(loss_weights)
    
    if use_power_decoder:
        """
        Loss function must have the same decoder than model.
        """
        loss.use_power_decoder()

    evaluator = None
    validation_initial_config = {}

    """
    Just in case our validation samples is not empty
    """
    if num_validation_samples > 0:
        """
        Create the configuration parameters for the Evaluator.
        validation-iou is the one used for validator to compute COCO metrics. mAP@0.5, mAP0.75 and mAP@0.5..0.95
        ``normalization`` is another important parameter that specifies the normalization used during validation.
        Notice that ModelPack is unsigned. If the user decides to change the normalization to be ``signed`` or ``raw``,
        please, make sure you also update these parameters as well. Resulting parameters are global parameters not needed
        while training the model.

        """
        label_offset = 1 if use_fake_background_class else 0  # add background class to the labels

        validation_initial_config = {
            "validation-iou": 0.5,
            "detection-iou": iou_threshold,
            "validation-threshold": score_threshold,
            "detection-threshold": score_threshold,
            "normalization": "unsigned",
            "maximum_detections": 300,
            "label_offset": 0,
            "metric": "iou",
            "plots": True
        }

        try:
            import mlflow
            if mlflow.active_run():
                mlflow.log_params(validation_initial_config)
        except ImportError:
            pass

        """
        This instance will be able to run trainable_model on all the validation images, postprocess them and
        return the scores, boxes, and classes objects
        """

        runner = InferenceKerasModel(
            model=trainable_model,
            labels=classes,
            detection_iou_threshold=validation_initial_config.get(
                "detection-iou"),
            detection_score_threshold=validation_initial_config.get(
                "detection-threshold"),
            norm=validation_initial_config.get("normalization"),
            label_offset=validation_initial_config.get("label_offset"),
            max_detections=300
        )

        """
        The evaluator is in charge of reading the outputs produced by ``runner`` instance and compute the metrics
        """
        evaluator = DetectionEval(
            runner=runner,
            parameters=validation_initial_config
        )

    """
    Intermediate results from validation and training process are shown in TensorBoard.
    In order to execute that operation, it is needed to specify initialize the logger as an instance of TensorBoard.
    The constructor will expect two parameters:

        - Resulting folder to write the logs
        - list of metrics names to show.

    The resulting path is trivial while the list of metrics could be a bit complicated at first sight.
    Validation process produces a lot of values and metrics that are not relevant during training the model. For
    that reason we filter them by name from this list. For the case of the losses, they need to be included into
    this list as well.

    For example:
    If we create a custom loss function that computes two different losses, based on the resolution of the objects,
    we need to assign two different names to them and append their names into the ``metric_names`` list.

    def loss(y_true, y_pred):
        # compute loss
        l1 = loss1
        l2 = loss2
        total_loss = l1 + l2
        return {
            "total-loss: total_loss,
            "small-objects-loss": l1,
            "large-objects-loss": l2,
        }


    Then our logger object should be defined in the following way:

    logger = TensorBoard(
        storage=from_config.get("logs", None),
        metric_names=[
            'total-loss',
            "small-objects-loss",
            "large-objects-loss"
        ]
    )
    """

    logger = TensorBoard(
        storage=from_config.get("logs", None),
        metric_names=[
            'total-loss',
            'mAP@0.5',
            'mAP@0.75',
            'mAP@0.5:0.95',
            'mACC@0.5',
            'mACC@0.75',
            'mACC@0.5:0.95',
            'mAR@0.5',
            'mAR@0.75',
            'mAR@0.5:0.95',
            'Overall-ACC',
            'Overall-AP',
            'Overall-AR',
            'localization-loss',
            'classification-loss',
            'objectness-loss',
            'step-time (seconds)',
            'learning-rate',
            "L2-loss",
        ]
    )

    """
    In this section we build the optimizer according to the parameters set into the configuration object.
    The function ``get_optimizer`` is pretty simple and be used as a reference: See
    ``deepview.modelpac.trainer.__main__.py``

    """
    steps_per_epoch = num_train_samples // bsize
    optimizer = get_optimizer(
        optimizer_config=opt_params,
        epochs=epochs,
        steps=steps_per_epoch
    )

    """
    This section clones the global configuration object and update it with the
    ModelPack version number and the model's pre-computed strides and anchors.
    This information is saved as a json file into the checkpoints folder, along
    with other model artifacts.
    """
    info = from_config.copy()
    info.update({
        'version': modelpack_version(),
        'anchors': model_handler._anchors.tolist(),
        'strides': model_handler._strides.tolist()
    })

    """
    Instance of the trainer object.
    This object will get the model, the optimizer and the loss function to run during all the epochs.
    During the process, intermediate results will be send to TensorBoard (losses, metrics, images, etc.)
    and two checkpoints will be saved into the destination folder>

        - the best evaluated checkpoint attending to the ``metric`` parameter
        - the last epoch trained.

    In that way we always will have the best evaluated checkpoint (float model) which not necessarily will produce
    the best quantized results and the last trained epoch for finetuning and restoring purposes.

    """
    ds_handler.encoder = model_handler.gt_encoder # embedding target generation into the dataset iterator 
    train_ds = ds_handler.build_train_iterator(
        batch_size=bsize
    )
    
    trainer = DetectionTrainer(
        model=trainable_model,
        dataset=train_ds,
        optimizer=optimizer,
        loss=loss,
        logger=logger,
        checkpoint=from_config.get("checkpoints", None),
        info=info,
        metric=metric,
        iou=iou_threshold,
        classes=classes,
        display=display,
        dvclive_output=dvclive_output,
        skip_validation_steps=from_config.get('skip-validation', 1),
        skip_initial_validation=from_config.get(
            'skip-initial-validation', False)
    )

    trainer.NCHW = from_config.get("nchw", False)
    """
    Once everything is configured, we just need to call the ``trainer.train()`` function
    and let it to run until the process ends. The training process will be done by using
    a tf.GradientTape strategy instead of model.fit()

    """
    trainer.train(
        epochs=epochs,
        train_ds=train_ds,
        val_ds=validation_ds,
        evaluator=evaluator,
        callback_handler=callbacks
    )


def train_segmentation(
        from_config: dict = None,
        dvclive_output=None,
        callbacks=None
):
    """
    This function wraps the training configuration for ModelPack segmentation

    Parameters
    ----------
    from_config: dict, default None
        This parameter is used to specify all the configurations needed
        by the model to be trained

    dvclive_output: str, default None
        Path to DVC folder. This parameter will be only activated if the product is licensed

    Returns
    -------
    None

    """
    """
        Reading the weights parameters and validate them. In case the weights are not ``coco`` or a valid path,
        a ValueError will be risen by ``validate_weights`` function
        """

    weights = from_config.get("weights", None)
    weights = validate_weights(
        weights=weights
    )

    """
    Reads the shape values and validates they are correct. Otherwise a ValueError will be raise by ``validate_shape``
    function. Shape values must be positive, and returned as a python list. Nuber of channels must be 3
    and width and height different than 0

    """
    shape = from_config.get("shape", None)
    shape = validate_shape(
        shape=shape
    )

    """
    Reading the epochs from the configuration object. In case the epochs is 0 or any negative number,
    the function ``validate_epochs`` will raise a ValueError exception
    """
    epochs = from_config.get("epochs", None)
    epochs = validate_epochs(
        epochs=epochs
    )

    """
    Reading the batch size from the configuration object. In case the batch size is 0 or any negative number,
    the function ``validate_batch_size`` will raise a ValueError exception
    """
    bsize = from_config.get("batch-size", None)
    bsize = validate_batch_size(
        bsize=bsize
    )

    """
    Inspect optimizer parameters.
    """
    opt_params = from_config.get("optimizer", None)
    opt_params = validate_optimizer_params(
        opt_params=opt_params
    )

    """
    Inspect the metric name used for evaluation exists. The name should be either of
    map, acc or recall. Otherwise the function  ``validate_metric`` will raise
    a ValueError exception
    """
    metric = from_config.get("metric", None)
    metric = validate_metric(
        metric=metric.lower()
    )

    from deepview.modelpack.datasets import SegmentationDatasetYaml
    ds_builder = SegmentationDatasetYaml(
        info_file=from_config.get("dataset", None),
        shape=shape,
        letter_box=from_config.get("letterbox", False),
        num_points=300,
        add_bkg_class=from_config.get('use_fake_background', True),
        tasks=["segment"]
    )

    """
    In this section we build the optimizer according to the parameters set into the configuration object.
    The function ``get_optimizer`` is pretty simple and be used as a reference: See
    ``deepview.modelpack.trainer.__main__.py``

    """

    steps_per_epoch = ds_builder.get_num_train_samples() // bsize
    optimizer = get_optimizer(
        optimizer_config=opt_params,
        epochs=epochs,
        steps=steps_per_epoch
    )

    train_ds = ds_builder.build_train_iterator(
        batch_size=bsize,
        prefetch=10
    )

    validation_ds = ds_builder.build_val_iterator(
        prefetch=10
    )

    """
    Enable the focus input layer optimization
    """
    focus = from_config.get("focus", "False")

    """
    This section of the code uses all the precomputed attributes for the current dataset and builds a keras model.
    The resulting model, is used for the Trainer for running the trining sessions
    """
    freeze_bn = from_config.get("freeze-bn", False)
    decay = from_config.get("weight-decay", 1e-5)
    freeze_backbone = from_config.get("freeze-backbone", False)
    upsample = from_config.get("upsample", UpsampleMethod.RESIZE)

    mpk_handler = ModelPackDetector()
    trainable_model = mpk_handler.get_segmentation_model(
        input_shape=shape,
        num_classes=ds_builder.get_num_segmentation_classes(),
        weights=weights,
        named_params={
            "focus": focus,
            "batch-norm": "frozen" if freeze_bn else "trainable",
            "weight-decay": decay,
            "freeze-backbone": str(freeze_backbone).lower(),
            "upsample": upsample
        },
        upsample=upsample
    )

    """
    This instance will be able to run trainable_model on all the validation images, postprocess them and
    return the segmentation mask of the image
    """

    from deepview.validator.runners import SegmentationKerasRunner
    runner = SegmentationKerasRunner(
        model=trainable_model,
    )

    """
    The evaluator is in charge of reading the outputs produced by
    ``runner`` instance and compute the metrics
    """
    logger = TensorBoard(
        storage=from_config.get("logs", None),
        metric_names=[
            'total-loss',
            'mAP',
            'mACC',
            'mAR',
            'Overall-ACC',
            'Overall-AP',
            'Overall-AR',
            'step-time (seconds)',
            'learning-rate',
            "L2-loss",
        ]
    )

    from deepview.validator.evaluators import SegmentationEval
    evaluator = SegmentationEval(
        runner=runner,
    )

    from deepview.modelpack.losses import SegmentationLoss
    loss = SegmentationLoss(
        num_classes=ds_builder.get_num_segmentation_classes(),
        use_dynamic_class_weights=True,
        weights=[1.0, 10.0]
    )

    display = from_config.get('display', 10)
    display = validate_display(
        display=display
    )
    register_parameter("display", display)

    from deepview.modelpack.trainer.segmentation import SegmentationTrainer
    trainer = SegmentationTrainer(
        model=trainable_model,
        dataset=train_ds,
        optimizer=optimizer,
        loss=loss,
        logger=logger,
        checkpoint=from_config.get("checkpoints", None),
        info=from_config,
        metric=metric,
        iou=0.5,
        classes=['background'] + ds_builder.labels,
        display=display,
        skip_validation_steps=from_config.get('skip-validation', 1),
        skip_initial_validation=from_config.get(
            'skip-initial-validation', False),
        dvclive_output=dvclive_output
    )

    trainer.NCHW = from_config.get("nchw", False)

    trainer.train(
        epochs=epochs,
        train_ds=train_ds,
        val_ds=validation_ds,
        evaluator=evaluator,
        callback_handler=callbacks
    )


def train_attitude(
    from_config=None,
    dvclive_output=None,
    callbacks=None
):
    """
    This function will be used to train ModelPack for attitude regression

    Parameters
    ----------
    from_config: dict, default None
        Initial configuration used to train the model
    dvclive_output: str, default None
        Path to folder to save DVC status
    Returns
    -------
    None

    Reading the weights parameters and validate them. In case the weights are not ``coco`` or a valid path,
    a ValueError will be risen by ``validate_weights`` function
    """
    weights = from_config.get("weights", None)
    weights = validate_weights(
        weights=weights
    )
    register_parameter("weights", weights)

    """
    Reads the shape values and validates they are correct. Otherwise a ValueError will be raise by ``validate_shape``
    function. Shape values must be positive, and returned as a python list. Nuber of channels must be 3
    and width and height different than 0

    """
    shape = from_config.get("shape", None)
    shape = validate_shape(
        shape=shape
    )
    register_parameter("shape", shape)

    """
    Reading the epochs from the configuration object. In case the epochs is 0 or any negative number,
    the function ``validate_epochs`` will raise a ValueError exception
    """
    epochs = from_config.get("epochs", None)
    epochs = validate_epochs(
        epochs=epochs
    )
    register_parameter("epochs", epochs)

    """
    Reading the batch size from the configuration object. In case the batch size is 0 or any negative number,
    the function ``validate_batch_size`` will raise a ValueError exception
    """
    bsize = from_config.get("batch-size", None)
    bsize = validate_batch_size(
        bsize=bsize
    )
    register_parameter("batch-size", bsize)

    """
    Inspect optimizer parameters.
    """
    opt_params = from_config.get("optimizer", None)
    opt_params = validate_optimizer_params(
        opt_params=opt_params
    )
    register_parameter("opt_params", opt_params)

    from deepview.modelpack.datasets import AttitudeDatasetJsonYaml
    num_bins = 3
    register_parameter("num-angles", num_bins)

    ds_builder = AttitudeDatasetJsonYaml(
        info_file=from_config.get("dataset", None),
        shape=shape
    )

    """
    Set Mean Square Error as validation metric
    """
    register_parameter("validation-metric", "mse")

    """
    Here the weights used to penalty the three different losses are validated and parsed
    (yaw, pitch and roll)
    """
    loss_weights = from_config.get('loss_weights', None)
    loss_weights = {
        "y_weight": loss_weights.get("weighted-yaw", 1.0),
        "p_weight": loss_weights.get("weighted-pitch", 1.0),
        "r_weight": loss_weights.get("weighted-roll", 1.0),
    }
    register_parameter("loss_weights", loss_weights)

    """
    In this section we build the optimizer according to the parameters set into the configuration object.
    The function ``get_optimizer`` is pretty simple and be used as a reference: See
    ``deepview.modelpack.trainer.__main__.py``
    """

    steps_per_epoch = ds_builder.get_num_train_samples() // bsize
    optimizer = get_optimizer(
        optimizer_config=opt_params,
        epochs=epochs,
        steps=steps_per_epoch
    )

    train_ds = ds_builder.build_train_iterator(
        batch_size=bsize,
        prefetch=10
    )

    val_ds = ds_builder.build_val_iterator(
        batch_size=1,
        prefetch=1
    )
    """
    Enable the focus input layer optimization
    """
    focus = from_config.get("focus", "False")

    """
    This section of the code uses all the precomputed attributes for the current dataset and builds a keras model.
    The resulting model, is used for the Trainer for running the trining sessions
    """
    freeze_bn = from_config.get("freeze-bn", False)
    decay = from_config.get("weight-decay", 1e-5)
    freeze_backbone = from_config.get("freeze-backbone", False)
    upsample = from_config.get("upsample", UpsampleMethod.RESIZE)

    mpk_handler = ModelPackDetector()
    named_params = {
        'objects_size': "large",
        "focus": focus,
        "batch-norm": "frozen" if freeze_bn else "trainable",
        "weight-decay": decay,
        "freeze-backbone": str(freeze_backbone).lower(),
        upsample: upsample
    }
    register_parameter("named_params", named_params)

    trainable_model = mpk_handler.get_attitude_model(
        input_shape=shape,
        num_classes=num_bins,
        weights=weights,
        named_params=named_params,
        upsample=upsample
    )

    """
    Loss function needs to be created by calling its own handler.
    After calling the constructor of the class, the next step we must do is to make a late initialization of the loss
    function with the custom configuration of the trainable_model. For that we need to call the
    ``model_handler.get_loss_named_params()`` function and pass the result as input of ``loss.set_named_params()``
    Finally, the loss function needs to know how to weight each loss during the computation of total-loss
    """
    from deepview.modelpack.losses import AttitudeLoss
    attitude_loss = AttitudeLoss()
    attitude_loss.set_named_params(mpk_handler.get_loss_named_params())
    attitude_loss.set_weights(loss_weights)

    logger = TensorBoard(
        storage=from_config.get("logs", None),
        metric_names=[
            'total-loss',
            'step-time (seconds)',
            'learning-rate',
            "yaw-loss",
            "pitch-loss",
            "roll-loss",
            "L2-loss"
        ]
    )

    display = from_config.get('display', 10)
    display = validate_display(
        display=display
    )
    register_parameter("display", display)

    from deepview.modelpack.trainer.attitude import AttitudeTrainer
    trainer = AttitudeTrainer(
        model=trainable_model,
        dataset=train_ds,
        optimizer=optimizer,
        loss=attitude_loss,
        # current order of angles within the dataset
        classes=["roll", "pitch", "yaw"],
        logger=logger,
        checkpoint=from_config.get("checkpoints", None),
        info=from_config,
        display=display,
        dvclive_output=dvclive_output,
        skip_validation_steps=from_config.get('skip-validation', 1),
        skip_initial_validation=from_config.get(
            'skip-initial-validation', False)
    )
    trainer.NCHW = from_config.get("nchw", False)

    from deepview.validator.evaluators import PoseEval
    evaluator = PoseEval()

    trainer.train(
        epochs=epochs,
        train_ds=train_ds,
        evaluator=evaluator,
        val_ds=val_ds,
        callback_handler=callbacks
    )


def train_detect_and_segment(
    from_config=None,
    dvclive_output=None,
    callbacks=None
):
    """
    This function will be used to train ModelPack for multi-task model(detect and segment)

    Parameters
    ----------
    from_config: dict, default None
        Initial configuration used to train the model
    dvclive_output: str, default None
        Path to folder to save DVC status
    Returns
    -------
    None

    Reading the weights parameters and validate them. In case the weights are not ``coco`` or a valid path,
    a ValueError will be risen by ``validate_weights`` function
    """
    """
            Reading the weights parameters and validate them. In case the weights are not ``coco`` or a valid path,
            a ValueError will be risen by ``validate_weights`` function
            """

    weights = from_config.get("weights", None)
    weights = validate_weights(
        weights=weights
    )
    register_parameter("weights", weights)

    """
    Reads the shape values and validates they are correct. Otherwise a ValueError will be raise by ``validate_shape``
    function. Shape values must be positive, and returned as a python list. Nuber of channels must be 3
    and width and height different than 0

    """
    shape = from_config.get("shape", None)
    shape = validate_shape(
        shape=shape
    )
    register_parameter("shape", shape)

    """
    Reading the epochs from the configuration object. In case the epochs is 0 or any negative number,
    the function ``validate_epochs`` will raise a ValueError exception
    """
    epochs = from_config.get("epochs", None)
    epochs = validate_epochs(
        epochs=epochs
    )
    register_parameter("epochs", epochs)

    """
    Reading the batch size from the configuration object. In case the batch size is 0 or any negative number,
    the function ``validate_batch_size`` will raise a ValueError exception
    """
    bsize = from_config.get("batch-size", None)
    bsize = validate_batch_size(
        bsize=bsize
    )
    register_parameter("batch-size", bsize)

    """
    Inspect optimizer parameters.
    """
    opt_params = from_config.get("optimizer", None)
    opt_params = validate_optimizer_params(
        opt_params=opt_params
    )
    register_parameter("opt_params", opt_params)

    """
    Inspect the metric name used for evaluation exists. The name should be either of
    map, acc or recall. Otherwise the function  ``validate_metric`` will raise
    a ValueError exception
    """
    metric = from_config.get("metric", None)
    metric = validate_metric(
        metric=metric.lower()
    )
    register_parameter("validation-metric", metric)

    """
    Here the weights used to penalty the three different losses are validated and parsed
    (classification loss, objectness loss and localization loss)
    """
    loss_weights = from_config.get('loss_weights', None)
    loss_weights = validate_loss_weights_for_detection(
        loss_weights=loss_weights
    )
    register_parameter("loss_weights", loss_weights)

    """
    Before start validating the model, we need to configure preprocessing parameters.
    This section reads the NMS parameters from the global configuration object.
    IoU threshold and Score threshold
    """
    iou_threshold = from_config.get('validation').get('iou', None)
    score_threshold = from_config.get('validation').get('score', None)
    iou_threshold, score_threshold = validate_thresholds(
        iou_threshold=iou_threshold,
        score_threshold=score_threshold
    )
    register_parameter("iou_threshold", iou_threshold)
    register_parameter("score_threshold", score_threshold)

    """
    This parameter is used to limit the number of sample images we are going to send to TensorBoard
    after each epoch is validated.
    """
    display = from_config.get('display', 10)
    display = validate_display(
        display=display
    )
    register_parameter("display", display)

    """
    With this parameter ModelPack will pay more attention on objects depending on the size.
    Anchors will be more adjusted to the size of the objects and the average will be weighted
    towards the parameter direction. For example, if our dataset is prune to have small objects,
    large objects can be seen like outliers and they can be relaxed in some extent. This means the
    anchors will be computed using weights to be more accurate when detecting small objects.
    """
    objects_size = from_config.get('objects-size', 'large')
    register_parameter("objects-size", objects_size)

    """
    When encoding the ground truth boxes, it is needed to specify the IoU value
    to make the right match between anchors and bounding boxes.
    By default the model is using 0.3.
    For some datasets, an small IoU could make our model predicts a lot of duplicated boxes,
    On the other hand, a higher IoU could make our model has a poor detection rate.
    """

    encoding_iou = from_config.get("encoding_iou", 0.3)
    register_parameter("encoding-iou", encoding_iou)

    """
    Reading the path to the dataset. In this case we are reading the path to the *.yaml file
    """
    dataset = from_config.get("dataset", None)
    dataset = validate_dataset(
        dataset=dataset
    )
    register_parameter("dataset", dataset)

    """
    Defining the ModelPack detector handler. This instance will be able to perform all the operations
    needed to configure the model at a given input resolution (anchors, strides, etc.)
    """
    model_handler = ModelPackDetector()
    model_handler.encoding_iou = encoding_iou

    """
    Read the decoder we are going to use for our model: Exponential or Power
    """
    use_power_decoder = from_config.get('use_power_decoder', False)

    register_parameter(
        "decoder",
        "power" if use_power_decoder else "exponential"
    )

    if use_power_decoder:
        model_handler.use_power_decoder()

    from deepview.modelpack.datasets import DetectAndSegmentDatasetYaml
    ds_builder = DetectAndSegmentDatasetYaml(
        info_file=from_config.get("dataset", None),
        shape=shape,
        letter_box=False,
        num_points=300
    )

    num_classes = len(ds_builder.labels)

    register_parameter("classes", ds_builder.labels)
    register_parameter("num-classes", num_classes)
    register_parameter("num-train-samples", ds_builder.num_training_samples)
    register_parameter("num-val-samples", ds_builder.num_validation_samples)

    train_ds = ds_builder.build_train_iterator(
        batch_size=bsize,
        prefetch=10
    )
    val_ds = ds_builder.build_val_iterator()

    compute_anchors = from_config.get("compute-anchors", False)
    anchors_file = from_config.get("anchors", None)
    save_anchors = from_config.get("save-anchors", None)

    anchors = None

    if compute_anchors:
        ds_builder.augment = False
        model_handler.precompute_anchors(train_ds, objects_size)
        ds_builder.augment = True
        anchors = model_handler.get_specific_anchors()

        if save_anchors and not os.path.exists(save_anchors):
            is_yaml = os.path.splitext(save_anchors)[1] == ".yaml"
            if is_yaml:
                import yaml

                # read yaml file content
                with open(anchors_file) as fp:
                    content = yaml.safe_load(fp)

                # append new anchors
                content['anchors'] = anchors.flatten().tolist()

                # save anchors
                with open(save_anchors, 'w') as fp:
                    yaml.safe_dump(
                        anchors,
                        fp,
                        allow_unicode=True,
                        encoding='utf-8'
                    )
            else:
                with open(save_anchors, 'w') as fp:
                    str_anchors = " ".join(str(item)
                                           for item in anchors.flatten())
                    fp.write(str_anchors)

    if anchors_file and os.path.exists(anchors_file):
        if save_anchors and anchors is None:
            raise RuntimeError(
                "\t - [ERROR] To compute anchors utilize --compute-anchors option"
            )

        is_yaml = os.path.splitext(anchors_file)[1] == ".yaml"
        if is_yaml:
            import yaml

            with open(anchors_file) as fp:
                content = yaml.safe_load(fp)
                anchors = content.get("anchors", None)
        else:
            anchors = [float(x) for x in open(
                anchors_file, 'r').readline().rstrip().split(' ')]

        if anchors:
            anchors = np.asarray(anchors).reshape(2, 3, 2)

    if anchors is None:
        if os.path.exists("params.yaml"):
            import yaml
            with open(anchors_file) as fp:
                content = yaml.safe_load(fp)
                anchors = content.get("anchors", None)
            if anchors:
                anchors = np.asarray(anchors).reshape(2, 3, 2)
            else:
                ds_builder.augment = False
                model_handler.precompute_anchors(train_ds, objects_size)
                ds_builder.augment = True
                ds_builder.store_anchors(
                    anchors=model_handler.get_specific_anchors())
                anchors = model_handler.get_specific_anchors()
    else:
        model_handler.set_specific_anchors(anchors=anchors)

    """
    In this section we build the optimizer according to the parameters set into the configuration object.
    The function ``get_optimizer`` is pretty simple and be used as a reference: See
    ``deepview.modelpack.trainer.__main__.py``
    """

    steps_per_epoch = ds_builder.get_num_train_samples() // bsize
    optimizer = get_optimizer(
        optimizer_config=opt_params,
        epochs=epochs,
        steps=steps_per_epoch
    )

    """
    Enable the focus input layer optimization
    """
    focus = from_config.get("focus", "False")
    """
    This section of the code uses all the precomputed attributes for the
    current dataset and builds a keras model. The resulting model, is used for
    the Trainer for running the trining sessions
    """
    freeze_bn = from_config.get("freeze-bn", False)
    decay = from_config.get("weight-decay", 1e-5)
    freeze_backbone = from_config.get("freeze-backbone", False)
    upsample = from_config.get("upsample", UpsampleMethod.RESIZE)

    trainable_model = model_handler.get_detect_and_segment_model(
        input_shape=shape,
        num_classes=num_classes,
        weights=weights,
        named_params={
            "activation": "relu6",
            "focus": focus,
            "batch-norm": "frozen" if freeze_bn else "trainable",
            "weight-decay": decay,
            "freeze-backbone": str(freeze_backbone).lower(),
            "upsample": upsample
        },
        upsample=upsample
    )

    detection_loss = ModelPackLoss()
    detection_loss.set_named_params(model_handler.get_loss_named_params())
    detection_loss.set_weights(loss_weights)

    from deepview.modelpack.losses import SegmentationLoss
    segmentation_loss = SegmentationLoss(
        num_classes=num_classes,
        use_dynamic_class_weights=True,
        weights=[1.0, 10.0]
    )

    logger = TensorBoard(
        storage=from_config.get("logs", None),
        metric_names=[
            "L2-loss",
            'total-loss',
            'step-time (seconds)',
            'learning-rate',
            'detection-mAP@0.5',
            'detection-mAP@0.75',
            'detection-mAP@0.5:0.95',
            'detection-mACC@0.5',
            'detection-mACC@0.75',
            'detection-mACC@0.5:0.95',
            'detection-mAR@0.5',
            'detection-mAR@0.75',
            'detection-mAR@0.5:0.95',
            'detection-Overall-ACC',
            'detection-Overall-AP',
            'detection-Overall-AR',
            'detection-localization-loss',
            'detection-classification-loss',
            'detection-objectness-loss',
            "detection-total-loss"
            "segmentation-total-loss"
            "segmentation-localization-loss",
            "segmentation-classification-loss",
            "segmentation-negative-loss",
            'segmentation-mAP',
            'segmentation-mACC',
            'segmentation-mAR',
            'segmentation-Overall-ACC',
            'segmentation-Overall-AP',
            'segmentation-Overall-AR',
        ]
    )

    from deepview.modelpack.trainer.multitask import SegmentAndDetectTrainer

    info = from_config.copy()
    info.update({
        'version': modelpack_version(),
        'anchors': model_handler._anchors.tolist(),
        'strides': model_handler._strides.tolist()
    })
    display = from_config.get("display", 10)

    validation_initial_config = {
        "validation-iou": 0.5,
        "detection-iou": iou_threshold,
        "validation-threshold": score_threshold,
        "detection-threshold": score_threshold,
        "normalization": "unsigned",
        "maximum_detections": 300,
        "label_offset": 0,
        "metric": "iou",
        "plots": True
    }

    from deepview.validator.evaluators import CombinedEvaluator
    from deepview.validator.evaluators import SegmentationEval
    from deepview.validator.evaluators import DetectionEval

    segmentationevaluator = SegmentationEval()
    detectionevaluator = DetectionEval(
        parameters=validation_initial_config
    )

    evaluator = CombinedEvaluator(
        detectionevaluator=detectionevaluator,
        segmentationevaluator=segmentationevaluator,
    )

    trainer = SegmentAndDetectTrainer(
        model=trainable_model,
        optimizer=optimizer,
        losses=[detection_loss, segmentation_loss],
        classes=ds_builder.labels,
        logger=logger,
        checkpoint=from_config.get("checkpoints", None),
        info=info,
        iou=iou_threshold,
        display=display,
        dvclive_output=dvclive_output,
        skip_validation_steps=from_config.get('skip-validation', 1),
        skip_initial_validation=from_config.get(
            'skip-initial-validation', False),
        weights=[1.0, 1.0]
    )
    trainer.NCHW = from_config.get("nchw", False)

    trainer.train(
        epochs=epochs,
        train_ds=train_ds,
        val_ds=val_ds,
        evaluator=evaluator,

    )


def run_all(
    from_config: dict = None,
    dvclive_output=None
):
    """
    Main function that calls the api with the training configuration

    Parameters
    ----------
    from_config: dict, default None

    Returns
    -------
    None
    """

    from deepview.modelpack.callbacks import ModelPackTrainingCallback

    task = from_config.get("task", None)
    task = validate_task(task=task)

    if task in ["detection", "detect"]:
        train_detection(from_config=from_config, dvclive_output=dvclive_output,
                        callbacks=ModelPackTrainingCallback())
    elif task in ["segmentation", "segment"]:
        train_segmentation(from_config=from_config, dvclive_output=dvclive_output,
                           callbacks=ModelPackTrainingCallback())
    elif task in ["attitude", "head-pose"]:
        train_attitude(from_config=from_config, dvclive_output=dvclive_output,
                       callbacks=ModelPackTrainingCallback())
    elif task in ['detect-and-segment', 'segment-and-detect']:
        train_detect_and_segment(
            from_config=from_config, dvclive_output=dvclive_output, callbacks=ModelPackTrainingCallback())
    else:
        raise ValueError('ModelPack unsupported training task %s' % task)


def main():
    parser = argparse.ArgumentParser()
    """
        - task
        - input shape
        - dataset
        - checkpoints
        - logs
        - warmup epochs
        - epochs
        - batch size
    """
    parser.add_argument('--load',
                        type=str,
                        help='load parameters from yaml configuration file')
    parser.add_argument('--save',
                        type=str,
                        help='save parameters to yaml configuration file')
    parser.add_argument(
        '-t', '--task', help='Task definition; either ``detection`` or ``segmentation``', default='detection', type=str
    )
    parser.add_argument(
        '--weights', help='Initialization weights. It could be either a path to a keras file or `coco` word',
        default='coco', type=str
    )
    parser.add_argument(
        '-i', '--shape', help='Model input resolution: HWC format', type=str, default='320,320,3'
    )
    parser.add_argument(
        '-d', '--dataset', help='Absolute path to dataset.yaml file', type=str
    )
    parser.add_argument(
        '-c',
        '--checkpoints',
        help='Absolute path to checkpoints folder',
        type=str,
        default='out'
    )
    parser.add_argument(
        '-l',
        '--logs',
        help='Absolute path to logs folder',
        type=str,
        default='out'
    )
    parser.add_argument(
        '-e', '--epochs', help='Number of epochs', type=int, default=1
    )
    parser.add_argument(
        '-b', '--batch-size', help='Number of epochs', type=int, default=10
    )
    parser.add_argument(
        '-w', '--warmup-epochs', help='Number of warmup epochs', type=int, default=1
    )
    parser.add_argument(
        '--initial_lr', help='Initial learning rate', type=float, default=1e-3
    )
    parser.add_argument(
        '--warmup_lr', help='Warmup initial learning rate', type=float, default=1e-5
    )
    parser.add_argument(
        '--exponential_decay', help='Number of epochs to apply exponential decay. If this parameter is larger than 0',
        type=int, default=0
    )
    parser.add_argument(
        '--iou_threshold', help='NMS IoU Threshold value. Any float number between 0 and 1', type=float, default=0.5
    )
    parser.add_argument(
        '--score_threshold', help='NMS Score Threshold value. Any float number between 0 and 1', type=float,
        default=0.45
    )
    parser.add_argument(
        '--metric',
        help='Evaluation metric. It could be either ``acc`` or ``map`` or ``recall``. By default it is ``acc``',
        type=str,
        default='acc'
    )
    parser.add_argument(
        '--weighted-localization',
        help='Weight for localization loss',
        type=float,
        default=1.0
    )
    parser.add_argument(
        '--weighted-classification',
        help='Weight for classification loss',
        type=float,
        default=1.0
    )
    parser.add_argument(
        '--weighted-objectness',
        help='Weight for objectness loss',
        type=float,
        default=1.0
    )

    parser.add_argument(
        '--Flip',
        help='Augmentation: Probability of applying horizontal flip',
        type=float,
        default=0.5
    )
    parser.add_argument(
        '--RandomBrightnessContrast',
        help='Augmentation: Probability of applying RandomBrightnessContrast',
        type=float,
        default=0.2
    )
    parser.add_argument(
        '--ToGray',
        help='Augmentation: Probability of applying ToGray',
        type=float,
        default=0.2
    )
    parser.add_argument(
        '--ChannelShuffle',
        help='Augmentation: Probability of applying ChannelShuffle',
        type=float,
        default=0.01
    )
    parser.add_argument(
        '--RandomFog',
        help='Augmentation: Probability of applying RandomFog',
        type=float,
        default=0.01
    )
    parser.add_argument(
        '--ShiftScaleRotate',
        help='Augmentation: Probability of applying ShiftScaleRotate',
        type=float,
        default=0.3
    )
    parser.add_argument(
        '--Mosaic',
        help='Augmentation: Probability of applying Mosaic',
        type=float,
        default=0.0
    )
    parser.add_argument(
        '--display',
        help='The number of images to display in tensorboard. '
             'Requires an integer. -1 for displaying all the images',
        type=int,
        default=0
    )
    parser.add_argument(
        '--objects_size',
        help='Specify the size of the objects in dataset_tutorials.rst. '
             'It could be either of ``small``, ``medium`` or ``large``',
        type=str,
        default='large'
    )
    parser.add_argument(
        '--remove_background_class',
        help='This parameter eliminates the fake background class. '
             'For ModelPack detection it is recommended to have this additional class',
        action='store_true'
    )
    parser.add_argument(
        '--use_power_decoder',
        help='This function controls the decoder process by selecting either of power or exponential funciton',
        action='store_true'
    )
    parser.add_argument(
        '--encoding_iou',
        help='IoU used for encoding ground truth values',
        type=float,
        default=0.3
    )
    parser.add_argument(
        '--mlflow',
        help='Enable MLflow parameter, metrics, and artifacts logging',
        action='store_true'
    )
    parser.add_argument(
        '--mlflow-parent',
        help='MLflow parent session id',
        type=str
    )
    parser.add_argument(
        '--mlflow-experiment',
        help='MLflow experiment name',
        type=str
    )
    parser.add_argument(
        '--mlflow-name',
        help='MLflow iteration run name',
        type=str
    )
    parser.add_argument(
        '--focus',
        help='Applies space_to_depth transformation to input image.',
        action='store_true'
    )
    parser.add_argument(
        '--license',
        help='Path to the license file',
        type=str,
        default=None
    )
    parser.add_argument(
        '--dvclive',
        help='Generate DVCLive metrics during training',
        type=str,
        default=None
    )
    parser.add_argument(
        '--report',
        help='DVC report format (html, md, notebook)',
        type=str,
        default=None
    )
    parser.add_argument(
        '--enable-numerics-check',
        help='Enable numerics checking for NaN or Inf values for early stop. '
             '(WARNING: consumes a lot of memory)',
        action='store_true'
    )

    parser.add_argument(
        '--skip-validation',
        help='Number of epochs to skip validation',
        type=int,
        default=1
    )

    parser.add_argument(
        '--weight-decay',
        help='Weight decay or L2 kernel regularizaiton value',
        type=float,
        default=1e-5
    )

    parser.add_argument(
        '--skip-initial-validation',
        help='Skip validation happening before start training the model',
        action='store_true'
    )

    parser.add_argument(
        '--freeze-bn',
        help='Make BatchNormalization freezeable. It is nnly for finetuning',
        action='store_true'
    )

    parser.add_argument(
        '--freeze-backbone',
        help='Freeze entire backbone for two-stage training',
        action='store_true'
    )

    parser.add_argument(
        '--compute-anchors',
        help="Compute anchors for a given resolution",
        action='store_true'
    )

    parser.add_argument(
        '--save-anchors',
        help="Save the anchors to a file. Could be params.yaml",
        type=str,
        default=None
    )

    parser.add_argument(
        '--anchors',
        help='Path to the file containing the anchors file. If not provided, \
        anchors will be taken from params.yaml',
        type=str,
        default=None
    )

    parser.add_argument(
        '--upsample',
        help='Defines the upsampling method. Either of ``resize`` or ``conv``',
        action=enum_action(UpsampleMethod),
        default=UpsampleMethod.RESIZE
    )
    parser.add_argument(
        '--nchw',
        help="Export model in NCHW format, default is NHWC",
        action='store_true'
    )

    args = parser.parse_args()

    if args.load is not None:
        with open(args.load, 'r') as f:
            parser.set_defaults(**load_yaml(f))
            args = parser.parse_args()

    if args.save is not None:
        save_args = vars(args).copy()
        del save_args['save']
        del save_args['load']
        with open(args.save, 'w') as f:
            save_yaml(save_args, f)

    if args.enable_numerics_check:
        tf.debugging.enable_check_numerics()

    if args.mlflow:
        try:
            import mlflow
        except ImportError:
            Warning('MLflow is not installed. Please install it by running `pip install mlflow`')

        tags = {
            mlflow.utils.mlflow_tags.MLFLOW_PARENT_RUN_ID: args.mlflow_parent
        } if args.mlflow_parent else None
        mlflow.set_experiment(args.mlflow_experiment)
        mlflow.start_run(run_name=args.mlflow_name,
                         nested=args.mlflow_parent is not None,
                         tags=tags)
        print('ModelPack MLFLOW_RUN_ID=%s' % mlflow.active_run().info.run_id)

    from_config = {
        "task": args.task,
        "dataset": args.dataset,
        "weights": args.weights,
        "shape": [int(item) for item in args.shape.split(',')],
        "epochs": args.epochs,
        "batch-size": args.batch_size,
        "optimizer": {
            "method": "adam",
            "learning-rate": args.initial_lr,
            "strategy": {
                "name": "exponential" if args.exponential_decay > 0 else "warmup",
                "parameters": {
                    "decay": args.exponential_decay,
                    "warmup-learning-rate": args.warmup_lr,
                    "warmup-epochs": 0 if args.warmup_epochs < 1 else args.warmup_epochs
                }
            }
        },
        "metric": args.metric,
        "logs": args.logs,
        "checkpoints": args.checkpoints,
        "validation": {
            "iou": args.iou_threshold,
            "score": args.score_threshold
        },
        "loss_weights": {
            'w_obj': args.weighted_objectness,
            'w_cls': args.weighted_classification,
            'w_loc': args.weighted_localization
        },
        "display": args.display,
        "augmentation": {
            'Flip': args.Flip,
            'RandomBrightnessContrast': args.RandomBrightnessContrast,
            'ToGray': args.ToGray,
            'ChannelShuffle': args.ChannelShuffle,
            'RandomFog': args.RandomFog,
            'ShiftScaleRotate': args.ShiftScaleRotate,
            'Mosaic': args.Mosaic
        },
        "encoding_iou": args.encoding_iou,
        "objects-size": args.objects_size,
        "use_fake_background": not args.remove_background_class,
        "use_power_decoder": args.use_power_decoder,
        "focus": args.focus,
        "skip-validation": args.skip_validation,
        "skip-initial-validation": args.skip_initial_validation,
        "freeze-bn": args.freeze_bn,
        "weight-decay": args.weight_decay,
        "freeze-backbone": args.freeze_backbone,
        "anchors": args.anchors,
        "compute-anchors": args.compute_anchors,
        "save-anchors": args.save_anchors,
        "upsample": args.upsample.value,
        'NCHW': args.nchw
    }

    if args.license:
        os.environ['DEEPVIEW_LICENSES'] = args.license

    if args.report:
        os.environ['DVC_REPORT'] = args.report

    run_all(from_config=from_config, dvclive_output=args.dvclive)


if __name__ == '__main__':
    
    print(f"\t - Trainer using CUDA: {tf.test.is_built_with_cuda()}")
    print(f"\t - Trainer using GPU: {tf.test.is_gpu_available()}")
    
    main()

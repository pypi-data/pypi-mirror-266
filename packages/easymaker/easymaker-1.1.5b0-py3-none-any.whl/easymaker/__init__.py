import importlib_metadata

from easymaker import initializer
from easymaker.batch_inference import batch_inference
from easymaker.common import constants
from easymaker.endpoint import endpoint
from easymaker.experiment import experiment
from easymaker.log import logger
from easymaker.storage import objectstorage
from easymaker.training import hyperparameter_tuning, model, training

__version__ = importlib_metadata.version("easymaker")

easymaker_config = initializer.global_config

init = easymaker_config.init

logger = logger.Logger

Experiment = experiment.Experiment

Training = training.Training

HyperparameterTuning = hyperparameter_tuning.HyperparameterTuning

Model = model.Model

Endpoint = endpoint.Endpoint

BatchInference = batch_inference.BatchInference

download = objectstorage.download

upload = objectstorage.upload

ObjectStorage = objectstorage.ObjectStorage

TENSORFLOW = "TENSORFLOW"
PYTORCH = "PYTORCH"

HYPERPARAMETER_TYPE_CODE = constants.HYPERPARAMETER_TYPE_CODE
OBJECTIVE_TYPE_CODE = constants.OBJECTIVE_TYPE_CODE
TUNING_STRATEGY = constants.TUNING_STRATEGY
EARLY_STOPPING_ALGORITHM = constants.EARLY_STOPPING_ALGORITHM
INPUT_DATA_TYPE_CODE = constants.INPUT_DATA_TYPE_CODE

__all__ = (
    "init",
    "Training",
)

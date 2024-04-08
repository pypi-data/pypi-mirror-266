import time
from datetime import timedelta

import easymaker
from easymaker.common import constants, exceptions, utils
from easymaker.common.utils import status_code_utils


class Training:
    _framework_name = None
    _framework_version = None

    def __init__(self):
        self.easymaker_api_sender = easymaker.easymaker_config.api_sender
        self.instance_list = self.easymaker_api_sender.get_instance_list()
        self.image_list = self.easymaker_api_sender.get_image_list()
        self.algorithm_list = self.easymaker_api_sender.get_algorithm_list()

    def run(self, experiment_id=None, training_name=None, training_description=None, train_image_name=None, train_instance_name=None, distributed_node_count=1, data_storage_size=None, source_dir_uri=None, entry_point=None, algorithm_name=None, hyperparameter_list=None, dataset_list=None, check_point_input_uri=None, check_point_upload_uri=None, model_upload_uri=None, timeout_hours=720, tag_list=None, use_log=False, wait=True, use_torchrun=False, nproc_per_node=0):
        """
        Returns:
            training_id
        """

        # run training
        response = self.easymaker_api_sender.run_training(
            training_name=training_name,
            training_description=training_description,
            experiment_id=experiment_id,
            image_id=utils.from_name_to_id(self.image_list, train_image_name),
            flavor_id=utils.from_name_to_id(self.instance_list, train_instance_name),
            distributed_node_count=distributed_node_count,
            data_storage_size=data_storage_size,
            source_dir_uri=source_dir_uri,
            entry_point=entry_point,
            algorithm_id=utils.from_name_to_id(self.algorithm_list, algorithm_name) if algorithm_name else None,
            hyperparameter_list=hyperparameter_list,
            dataset_list=dataset_list,
            check_point_input_uri=check_point_input_uri,
            check_point_upload_uri=check_point_upload_uri,
            model_upload_uri=model_upload_uri,
            training_type_code="NORMAL",
            timeout_hours=timeout_hours,
            tag_list=tag_list,
            use_log=use_log,
            use_torchrun=use_torchrun,
            nproc_per_node=nproc_per_node,
        )

        training_id = response["training"]["trainingId"]
        if wait:
            waiting_time_seconds = 0
            training_status = status_code_utils.replace_status_code(response["training"]["trainingStatusCode"])
            while training_status != "COMPLETE":
                print(f"[AI EasyMaker] Training create status : {training_status} ({timedelta(seconds=waiting_time_seconds)}) Please wait...")
                time.sleep(constants.EASYMAKER_API_WAIT_INTERVAL_SECONDS)
                waiting_time_seconds += constants.EASYMAKER_API_WAIT_INTERVAL_SECONDS
                training = self.easymaker_api_sender.get_training_by_id(training_id)
                training_status = status_code_utils.replace_status_code(training["training"]["trainingStatusCode"])
                if "FAIL" in training_status or "STOPPED" in training_status:
                    training["training"]["trainingStatusCode"] = training_status
                    raise exceptions.EasyMakerError(training)
            print(f"[AI EasyMaker] Training create complete. Training Id : {training_id}")
        else:
            print(f"[AI EasyMaker] Training create request complete. Training Id : {training_id}")
        return training_id

    def delete(self, training_id):
        response = self.easymaker_api_sender.delete_training_by_id(training_id=training_id)
        print(f"[AI EasyMaker] Training delete request complete. Training Id : {training_id}")
        return response

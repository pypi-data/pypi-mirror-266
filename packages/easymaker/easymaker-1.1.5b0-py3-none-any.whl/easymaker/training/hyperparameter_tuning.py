import time
from datetime import timedelta

import easymaker
from easymaker.common import constants, exceptions, utils
from easymaker.common.utils import status_code_utils


class HyperparameterTuning:
    _framework_name = None
    _framework_version = None

    def __init__(self):
        self.easymaker_api_sender = easymaker.easymaker_config.api_sender
        self.instance_list = self.easymaker_api_sender.get_instance_list()
        self.image_list = self.easymaker_api_sender.get_image_list()
        self.algorithm_list = self.easymaker_api_sender.get_algorithm_list()

    def run(
        self,
        experiment_id=None,
        hyperparameter_tuning_name=None,
        hyperparameter_tuning_description=None,
        algorithm_name=None,
        image_name=None,
        instance_name=None,
        distributed_node_count=1,  # Integer
        parallel_trial_count=1,  # Integer
        data_storage_size=None,
        source_dir_uri=None,
        entry_point=None,
        hyperparameter_spec_list=None,  # [{"name": "","type": easymaker.HYPERPARAMETER_TYPE_CODE,"feasibleSpace": {"min": "","max": "","list": "","step": "",}}, ]
        dataset_list=None,
        check_point_input_uri=None,
        check_point_upload_uri=None,
        model_upload_uri=None,
        timeout_hours=720,
        tag_list=None,
        use_log=False,
        wait=True,
        metric_list=None,  # name 리스트만 입력받아  [{"name": ""}, {"name": ""}] 형태로 변경
        metric_regex=None,  # ""
        objective_metric_name=None,  # name 값만 입력받아 {"name": ""} 형태로 변경
        objective_type_code=None,  # easymaker.OBJECTIVE_TYPE_CODE.MINIMIZE, MAXIMIZE
        objective_goal=None,  # double
        max_failed_trial_count=None,  # Integer
        max_trial_count=None,  # Integer
        tuning_strategy_name=None,  # easymaker.TUNING_STRATEGY.BAYESIAN_OPTIMIZATION, RANDOM, GRID
        tuning_strategy_random_state=None,  # Integer
        early_stopping_algorithm=None,  # easymaker.EARLY_STOPPING_ALGORITHM.MEDIAN
        early_stopping_min_trial_count=3,
        early_stopping_start_step=4,
        use_torchrun=False,
        nproc_per_node=0,
    ):
        """
        Returns:
            hyperparameter_tuning_id
        """

        def convertMetricFormat(name):
            return {"name": name}

        # run hyperparameter tuning
        response = self.easymaker_api_sender.run_hyperparameter_tuning(
            hyperparameter_tuning_name=hyperparameter_tuning_name,
            hyperparameter_tuning_description=hyperparameter_tuning_description,
            experiment_id=experiment_id,
            algorithm_id=utils.from_name_to_id(self.algorithm_list, algorithm_name) if algorithm_name else None,
            image_id=utils.from_name_to_id(self.image_list, image_name),
            flavor_id=utils.from_name_to_id(self.instance_list, instance_name),
            distributed_node_count=distributed_node_count,
            parallel_trial_count=parallel_trial_count,
            data_storage_size=data_storage_size,
            source_dir_uri=source_dir_uri,
            entry_point=entry_point,
            hyperparameter_spec_list=hyperparameter_spec_list,
            dataset_list=dataset_list,
            check_point_input_uri=check_point_input_uri,
            check_point_upload_uri=check_point_upload_uri,
            model_upload_uri=model_upload_uri,
            timeout_hours=timeout_hours,
            tag_list=tag_list,
            use_log=use_log,
            metric_list=list(map(convertMetricFormat, metric_list)) if metric_list else None,
            metric_regex=metric_regex,
            objective_metric=convertMetricFormat(objective_metric_name) if objective_metric_name else None,
            objective_type_code=objective_type_code,
            objective_goal=objective_goal,
            max_failed_trial_count=max_failed_trial_count,
            max_trial_count=max_trial_count,
            tuning_strategy_name=tuning_strategy_name,
            tuning_strategy_random_state=tuning_strategy_random_state,
            early_stopping_algorithm=early_stopping_algorithm,
            early_stopping_min_trial_count=early_stopping_min_trial_count,
            early_stopping_start_step=early_stopping_start_step,
            use_torchrun=use_torchrun,
            nproc_per_node=nproc_per_node,
        )

        hyperparameter_tuning_id = response["hyperparameterTuning"]["hyperparameterTuningId"]
        if wait:
            waiting_time_seconds = 0
            hyperparameter_tuning_status = status_code_utils.replace_status_code(response["hyperparameterTuning"]["hyperparameterTuningStatusCode"])
            while hyperparameter_tuning_status != "COMPLETE":
                print(f"[AI EasyMaker] Hyperparameter Tuning create status : {hyperparameter_tuning_status} ({timedelta(seconds=waiting_time_seconds)}) Please wait...")
                time.sleep(constants.EASYMAKER_API_WAIT_INTERVAL_SECONDS)
                waiting_time_seconds += constants.EASYMAKER_API_WAIT_INTERVAL_SECONDS
                hyperparameter_tuning = self.easymaker_api_sender.get_hyperparameter_tuning_by_id(hyperparameter_tuning_id)
                hyperparameter_tuning_status = status_code_utils.replace_status_code(hyperparameter_tuning["hyperparameterTuning"]["hyperparameterTuningStatusCode"])
                if "FAIL" in hyperparameter_tuning_status or "STOPPED" in hyperparameter_tuning_status:
                    hyperparameter_tuning["hyperparameterTuning"]["hyperparameterTuningStatusCode"] = hyperparameter_tuning_status
                    raise exceptions.EasyMakerError(hyperparameter_tuning)
            print(f"[AI EasyMaker] Hyperparameter Tuning create complete. Hyperparameter Tuning Id : {hyperparameter_tuning_id}")
        else:
            print(f"[AI EasyMaker] Hyperparameter Tuning create request complete. Hyperparameter Tuning Id : {hyperparameter_tuning_id}")
        return hyperparameter_tuning_id

    def delete(self, hyperparameter_tuning_id):
        response = self.easymaker_api_sender.delete_hyperparameter_tuning_by_id(hyperparameter_tuning_id=hyperparameter_tuning_id)
        print(f"[AI EasyMaker] Hyperparameter Tuning delete request complete. Hyperparameter Tuning Id : {hyperparameter_tuning_id}")
        return response

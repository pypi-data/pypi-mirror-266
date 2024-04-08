import os
import ssl

import requests
from requests.adapters import HTTPAdapter, Retry
from requests.sessions import Session
from urllib3 import poolmanager

from easymaker.common import constants, exceptions
from easymaker.common.utils import status_code_utils


class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
        self.poolmanager = poolmanager.PoolManager(num_pools=connections, maxsize=maxsize, block=block, ssl_context=ctx)


class ApiSender:
    def __init__(self, region, appkey, secret_key=None):

        if os.environ.get("EM_PROFILE"):
            self._easymakerApiUrl = constants.EASYMAKER_DEV_API_URL.format(region, os.environ.get("EM_PROFILE")).rstrip("/")
            if os.environ.get("EM_PROFILE") == "local":
                self._easymakerApiUrl = "http://127.0.0.1:10090".rstrip("/")
        else:
            self._easymakerApiUrl = constants.EASYMAKER_API_URL.format(region).rstrip("/")

        self._appkey = appkey
        self._secret_key = secret_key

        self.session = Session()
        self.session.mount("https://", TLSAdapter(max_retries=Retry(total=3, backoff_factor=1)))
        self.session.headers.update(self._get_headers())

        try:
            requests.get(self._easymakerApiUrl + "/nhn-api-gateway")
        except Exception:
            raise exceptions.EasyMakerRegionError(f"Please provide a region")

    def _isSuccessful(self, response):
        isSuccess = response["header"]["isSuccessful"]
        if not isSuccess:
            raise exceptions.EasyMakerError(response["header"]["resultMessage"])

        return isSuccess

    def _get_headers(self):
        if os.environ.get("EM_TOKEN"):
            headers = {"X-EasyMaker-Token": os.environ.get("EM_TOKEN")}
        else:
            headers = {"X-Secret-Key": self._secret_key}
        return headers

    def _replace_status(self, obj, key):
        obj[key] = status_code_utils.replace_status_code(obj[key])
        return obj

    def _replace_status_code_in_dict_list(self, dict_list, status_key):
        return list(map(lambda d: self._replace_status(d, status_key), dict_list))

    def get_objectstorage_token(self, tenant_id=None, username=None, password=None):

        if os.environ.get("EM_TOKEN"):
            response = self.session.get(f'{self._easymakerApiUrl}/token/v1.0/appkeys/{self._appkey}/groups/{os.environ.get("EM_GROUP_ID")}/iaas-token').json()
            self._isSuccessful(response)
            return response
        else:
            if tenant_id and username and password:
                token_url = constants.OBJECT_STORAGE_TOKEN_URL
                req_header = {"Content-Type": "application/json"}
                body = {"auth": {"tenantId": tenant_id, "passwordCredentials": {"username": username, "password": password}}}
                response = self.session.post(token_url, headers=req_header, json=body).json()
                return response
            else:
                raise exceptions.EasyMakerError(f"Invalid object storage username/password")

    def get_instance_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/flavors").json()
        self._isSuccessful(response)

        flavor_dict_list = []
        for flavor in response["flavorList"]:
            flavor_dict_list.append({"id": flavor["id"], "name": flavor["name"]})
        return flavor_dict_list

    def get_image_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/images").json()
        self._isSuccessful(response)

        image_dict_list = []
        for image in response["imageList"]:
            if image["groupTypeCode"] == "TRAINING":
                image_dict_list.append({"id": image["imageId"], "name": image["imageName"]})
        return image_dict_list

    def get_algorithm_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/algorithms").json()
        self._isSuccessful(response)

        algorithm_dict_list = []
        image_dict = {image["id"]: image["name"] for image in self.get_image_list()}

        for algorithm in response["algorithmList"]:
            algorithm_dict_list.append({"id": algorithm["algorithmId"], "name": algorithm["algorithmName"], "availableTrainingImageList": [image_dict[algorithm["cpuTrainingImageId"]], image_dict[algorithm["gpuTrainingImageId"]]]})

        return algorithm_dict_list

    def get_experiment_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/experiments").json()
        self._isSuccessful(response)

        dict_list = []
        for experiment in response["experimentList"]:
            dict_list.append({"id": experiment["experimentId"], "name": experiment["experimentName"]})
        return dict_list

    def create_experiment(self, experiment_name, experiment_description):
        body = {"experimentName": experiment_name, "description": experiment_description}
        response = self.session.post(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/experiments", json=body).json()
        self._isSuccessful(response)

        return response

    def get_experiment_by_id(self, experiment_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/experiments/{experiment_id}").json()
        self._isSuccessful(response)

        return response

    def delete_experiment_by_id(self, experiment_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/experiments/{experiment_id}").json()
        self._isSuccessful(response)

        return response

    def run_training(self, training_name, training_description, experiment_id, image_id, flavor_id, distributed_node_count, data_storage_size, source_dir_uri, entry_point, algorithm_id, hyperparameter_list, dataset_list, check_point_input_uri, check_point_upload_uri, model_upload_uri, training_type_code, timeout_hours, tag_list, use_log, use_torchrun, nproc_per_node):
        body = {
            "trainingName": training_name,
            "description": training_description,
            "experimentId": experiment_id,
            "imageId": image_id,
            "flavorId": flavor_id,
            "instanceCount": distributed_node_count,
            "dataStorageSize": data_storage_size,
            "algorithmId": algorithm_id,
            "hyperparameterList": hyperparameter_list,
            "datasetList": dataset_list,
            "checkPointInputUri": check_point_input_uri,
            "checkPointUploadUri": check_point_upload_uri,
            "modelUploadUri": model_upload_uri,
            "trainingTypeCode": training_type_code,
            "timeoutMinutes": timeout_hours * 60,
            "tagList": tag_list,
            "useLog": use_log,
            "useTorchrun": use_torchrun,
            "nprocPerNode": nproc_per_node,
        }

        if algorithm_id is None:
            body["sourceDirUri"] = source_dir_uri
            body["entryPoint"] = entry_point

        response = self.session.post(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/trainings", json=body).json()

        self._isSuccessful(response)
        return response

    def get_training_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/trainings").json()
        self._isSuccessful(response)

        dict_list = []
        for training in response["trainingList"]:
            dict_list.append({"id": training["trainingId"], "name": training["trainingName"]})
        return dict_list

    def get_training_by_id(self, training_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/trainings/{training_id}").json()
        self._isSuccessful(response)

        return response

    def delete_training_by_id(self, training_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/trainings/{training_id}").json()
        self._isSuccessful(response)

        return response

    def run_hyperparameter_tuning(
        self,
        hyperparameter_tuning_name,
        hyperparameter_tuning_description,
        experiment_id,
        algorithm_id,
        image_id,
        flavor_id,
        distributed_node_count,
        parallel_trial_count,
        data_storage_size,
        source_dir_uri,
        entry_point,
        hyperparameter_spec_list,
        dataset_list,
        check_point_input_uri,
        check_point_upload_uri,
        model_upload_uri,
        timeout_hours,
        tag_list,
        use_log,
        metric_list,
        metric_regex,
        objective_metric,
        objective_type_code,
        objective_goal,
        max_failed_trial_count,
        max_trial_count,
        tuning_strategy_name,
        tuning_strategy_random_state,
        early_stopping_algorithm,
        early_stopping_min_trial_count,
        early_stopping_start_step,
        use_torchrun,
        nproc_per_node,
    ):
        body = {
            "hyperparameterTuningName": hyperparameter_tuning_name,
            "description": hyperparameter_tuning_description,
            "experimentId": experiment_id,
            "algorithmId": algorithm_id,
            "sourceDirUri": source_dir_uri,
            "entryPoint": entry_point,
            "hyperparameterSpecList": hyperparameter_spec_list,
            "imageId": image_id,
            "flavorId": flavor_id,
            "instanceCount": distributed_node_count * parallel_trial_count,
            "datasetList": dataset_list,
            "modelUploadUri": model_upload_uri,
            "checkPointInputUri": check_point_input_uri,
            "checkPointUploadUri": check_point_upload_uri,
            "dataStorageSize": data_storage_size,
            "timeoutMinutes": timeout_hours * 60,
            "useLog": use_log,
            "tagList": tag_list,
            "metricList": metric_list,
            "metricRegex": metric_regex,
            "objectiveMetric": objective_metric,
            "objectiveTypeCode": objective_type_code,
            "objectiveGoal": objective_goal,
            "maxFailedTrialCount": max_failed_trial_count,
            "maxTrialCount": max_trial_count,
            "parallelTrialCount": parallel_trial_count,
            "tuningStrategyName": tuning_strategy_name,
            "tuningStrategyRandomState": tuning_strategy_random_state,
            "earlyStoppingAlgorithm": early_stopping_algorithm,
            "earlyStoppingMinTrialCount": early_stopping_min_trial_count,
            "earlyStoppingStartStep": early_stopping_start_step,
            "useTorchrun": use_torchrun,
            "nprocPerNode": nproc_per_node,
        }
        response = self.session.post(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/hyperparameter-tunings", json=body).json()

        self._isSuccessful(response)
        return response

    def get_hyperparameter_tuning_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/hyperparameter-tunings").json()
        self._isSuccessful(response)

        dict_list = []
        for training in response["hyperparameterTuningList"]:
            dict_list.append({"id": training["hyperparameterTuningId"], "name": training["hyperparameterTuningName"]})
        return dict_list

    def get_hyperparameter_tuning_by_id(self, hyperparameter_tuning_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/hyperparameter-tunings/{hyperparameter_tuning_id}").json()
        self._isSuccessful(response)

        return response

    def delete_hyperparameter_tuning_by_id(self, hyperparameter_tuning_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/hyperparameter-tunings/{hyperparameter_tuning_id}").json()
        self._isSuccessful(response)

        return response

    def create_model(self, model_name, model_description=None, training_id=None, hyperparameter_tuning_id=None, framework_code=None, model_uri=None, tag_list=None):
        body = {
            "modelName": model_name,
            "description": model_description,
            "trainingId": training_id,
            "hyperparameterTuningId": hyperparameter_tuning_id,
            "frameworkCode": framework_code,
            "modelUploadUri": model_uri,
            "tagList": tag_list,
        }
        response = self.session.post(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/models", json=body).json()
        self._isSuccessful(response)

        return response

    def get_model_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/models").json()
        self._isSuccessful(response)

        dict_list = []
        for model in response["modelList"]:
            dict_list.append({"id": model["modelId"], "name": model["modelName"]})
        return dict_list

    def get_model_by_id(self, model_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/models/{model_id}").json()
        self._isSuccessful(response)

        return response

    def delete_model_by_id(self, model_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/models/{model_id}").json()
        self._isSuccessful(response)

        return response

    def create_endpoint(self, endpoint_name, endpoint_description, flavor_id, endpoint_model_resource_list, node_count, tag_list, use_log, ca_enable, ca_min_node_count, ca_max_node_count, ca_scale_down_enable, ca_scale_down_util_thresh, ca_scale_down_unneeded_time, ca_scale_down_delay_after_add):
        body = {
            "endpointName": endpoint_name,
            "description": endpoint_description,
            "flavorId": flavor_id,
            "endpointModelResourceList": endpoint_model_resource_list,
            "nodeCount": node_count,
            "tagList": tag_list,
            "useLog": use_log,
            "caEnable": ca_enable,
            "caMinNodeCount": ca_min_node_count,
            "caMaxNodeCount": ca_max_node_count,
            "caScaleDownEnable": ca_scale_down_enable,
            "caScaleDownUtilThresh": ca_scale_down_util_thresh,
            "caScaleDownUnneededTime": ca_scale_down_unneeded_time,
            "caScaleDownDelayAfterAdd": ca_scale_down_delay_after_add,
        }
        response = self.session.post(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoints", json=body).json()
        self._isSuccessful(response)

        return response

    def create_stage(self, endpoint_id, stage_name, stage_description, flavor_id, endpoint_model_resource_list, node_count, tag_list, use_log, ca_enable, ca_min_node_count, ca_max_node_count, ca_scale_down_enable, ca_scale_down_util_thresh, ca_scale_down_unneeded_time, ca_scale_down_delay_after_add):
        body = {
            "endpointId": endpoint_id,
            "apigwStageName": stage_name,
            "description": stage_description,
            "flavorId": flavor_id,
            "endpointModelResourceList": endpoint_model_resource_list,
            "nodeCount": node_count,
            "tagList": tag_list,
            "useLog": use_log,
            "caEnable": ca_enable,
            "caMinNodeCount": ca_min_node_count,
            "caMaxNodeCount": ca_max_node_count,
            "caScaleDownEnable": ca_scale_down_enable,
            "caScaleDownUtilThresh": ca_scale_down_util_thresh,
            "caScaleDownUnneededTime": ca_scale_down_unneeded_time,
            "caScaleDownDelayAfterAdd": ca_scale_down_delay_after_add,
        }

        response = self.session.post(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoint-stages", json=body).json()
        self._isSuccessful(response)

        return response

    def get_endpoint_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoints").json()
        self._isSuccessful(response)

        dict_list = response["endpointList"]
        dict_list = self._replace_status_code_in_dict_list(dict_list, "endpointStatusCode")

        for endpoint in dict_list:
            endpoint["id"] = endpoint["endpointId"]
            endpoint["name"] = endpoint["endpointName"]

        return dict_list

    def get_endpoint_by_id(self, endpoint_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoints/{endpoint_id}").json()
        self._isSuccessful(response)

        dict = response["endpoint"]
        dict = self._replace_status(dict, "endpointStatusCode")

        return dict

    def get_endpoint_stage_list(self, endpoint_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoint-stages", params={"endpointId": endpoint_id}).json()
        self._isSuccessful(response)

        dict_list = response["endpointStageList"]
        dict_list = self._replace_status_code_in_dict_list(dict_list, "endpointStageStatusCode")

        return dict_list

    def get_endpoint_stage_by_id(self, endpoint_stage_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoint-stages/{endpoint_stage_id}").json()
        self._isSuccessful(response)

        dict = response["endpointStage"]
        dict = self._replace_status(dict, "endpointStageStatusCode")

        return dict

    def get_endpoint_model_list(self, endpoint_stage_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoint-models", params={"endpointStageId": endpoint_stage_id}).json()
        self._isSuccessful(response)

        dict_list = response["endpointModelList"]
        dict_list = self._replace_status_code_in_dict_list(dict_list, "endpointModelStatusCode")

        return response

    def get_endpoint_model_by_id(self, endpoint_model_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoint-models/{endpoint_model_id}").json()
        self._isSuccessful(response)

        dict = response["endpointModel"]
        dict = self._replace_status(dict, "endpointModelStatusCode")

        return dict

    def delete_endpoint_by_id(self, endpoint_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoints/{endpoint_id}").json()
        self._isSuccessful(response)

        return response

    def delete_endpoint_stage_by_id(self, endpoint_stage_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoint-stages/{endpoint_stage_id}").json()
        self._isSuccessful(response)

        return response

    def delete_endpoint_model_by_id(self, endpoint_model_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/endpoint-models/{endpoint_model_id}").json()
        self._isSuccessful(response)

        return response

    def run_batch_inference(
        self,
        batch_inference_name,
        instance_count,
        timeout_minutes,
        flavor_id,
        model_id,
        #
        pod_count,
        max_batch_size,
        inference_timeout_seconds,
        #
        input_data_uri,
        input_data_type_code,
        include_glob_pattern,
        exclude_glob_pattern,
        output_upload_uri,
        #
        data_storage_size,
        #
        description,
        tag_list,
        use_log,
    ):
        body = {
            "batchInferenceName": batch_inference_name,
            "instanceCount": instance_count,
            "timeoutMinutes": timeout_minutes,
            "flavorId": flavor_id,
            "modelId": model_id,
            #
            "podCount": pod_count,
            "maxBatchSize": max_batch_size,
            "inferenceTimeoutSeconds": inference_timeout_seconds,
            #
            "inputDataUri": input_data_uri,
            "inputDataTypeCode": input_data_type_code,
            "includeGlobPattern": include_glob_pattern,
            "excludeGlobPattern": exclude_glob_pattern,
            "outputUploadUri": output_upload_uri,
            #
            "dataStorageSize": data_storage_size,
            #
            "description": description,
            "tagList": tag_list,
            "useLog": use_log,
        }

        response = self.session.post(
            f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/batch-inferences",
            json=body,
        ).json()

        self._isSuccessful(response)
        return response

    def get_batch_inference_list(self):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/batch-inferences").json()
        self._isSuccessful(response)

        dict_list = []
        for batch_inference in response["batchInferenceList"]:
            dict_list.append(
                {
                    "id": batch_inference["batchInferenceId"],
                    "name": batch_inference["batchInferenceName"],
                }
            )
        return dict_list

    def get_batch_inference_by_id(self, batch_inference_id):
        response = self.session.get(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/batch-inferences/{batch_inference_id}").json()
        self._isSuccessful(response)

        return response

    def delete_batch_inference_by_id(self, batch_inference_id):
        response = self.session.delete(f"{self._easymakerApiUrl}/v1.0/appkeys/{self._appkey}/batch-inferences/{batch_inference_id}").json()
        self._isSuccessful(response)

        return response

    def send_logncrash(self, logncrash_body):
        response = self.session.post(constants.LOGNCRASH_URL, json=logncrash_body).json()
        return response

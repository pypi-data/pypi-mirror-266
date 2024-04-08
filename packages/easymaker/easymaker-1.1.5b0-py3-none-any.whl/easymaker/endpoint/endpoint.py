import time
from datetime import timedelta

import requests

import easymaker
from easymaker.common import constants, exceptions, utils
from easymaker.common.utils import status_code_utils


class Endpoint:
    def __init__(self, endpoint_id=None):
        """
        Args:
            endpoint_id (str): Endpoint Id
        """
        self.easymaker_api_sender = easymaker.easymaker_config.api_sender
        if endpoint_id is not None:
            self.endpoint_id = endpoint_id

    def create(
        self,
        endpoint_name,
        endpoint_instance_name,
        endpoint_model_resource_list,
        endpoint_instance_count=1,
        endpoint_description=None,
        tag_list=None,
        use_log=False,
        wait=True,
        autoscaler_enable=False,
        autoscaler_min_node_count=1,
        autoscaler_max_node_count=10,
        autoscaler_scale_down_enable=True,
        autoscaler_scale_down_util_threshold=50,
        autoscaler_scale_down_unneeded_time=10,
        autoscaler_scale_down_delay_after_add=10,
    ):
        """
        Returns:
            endpoint_id(str)
        """

        self.instance_list = self.easymaker_api_sender.get_instance_list()
        response = self.easymaker_api_sender.create_endpoint(
            endpoint_name=endpoint_name,
            endpoint_description=endpoint_description,
            flavor_id=utils.from_name_to_id(self.instance_list, endpoint_instance_name),
            endpoint_model_resource_list=endpoint_model_resource_list,
            node_count=endpoint_instance_count,
            tag_list=tag_list,
            use_log=use_log,
            ca_enable=autoscaler_enable,
            ca_min_node_count=autoscaler_min_node_count,
            ca_max_node_count=autoscaler_max_node_count,
            ca_scale_down_enable=autoscaler_scale_down_enable,
            ca_scale_down_util_thresh=autoscaler_scale_down_util_threshold,
            ca_scale_down_unneeded_time=autoscaler_scale_down_unneeded_time,
            ca_scale_down_delay_after_add=autoscaler_scale_down_delay_after_add,
        )

        self.endpoint_id = response["endpoint"]["endpointId"]
        default_endpoint_stage_info = self.get_default_endpoint_stage()
        endpoint_stage_id = default_endpoint_stage_info["endpointStageId"]
        if wait:
            waiting_time_seconds = 0
            endpoint_status = status_code_utils.replace_status_code(response["endpoint"]["endpointStatusCode"])
            while endpoint_status != "ACTIVE":
                print(f"[AI EasyMaker] Endpoint create status : {endpoint_status} ({timedelta(seconds=waiting_time_seconds)}) Please wait...")
                time.sleep(constants.EASYMAKER_API_WAIT_INTERVAL_SECONDS)
                waiting_time_seconds += constants.EASYMAKER_API_WAIT_INTERVAL_SECONDS
                endpoint = self.easymaker_api_sender.get_endpoint_by_id(self.endpoint_id)
                endpoint_status = endpoint["endpointStatusCode"]
                if "FAIL" in endpoint_status:
                    endpoint["endpoint"]["endpointStatusCode"] = endpoint_status
                    raise exceptions.EasyMakerError(endpoint)

            endpoint_stage_status = "CREATE_REQUESTED"
            while endpoint_stage_status != "ACTIVE":
                print(f"[AI EasyMaker] Endpoint stage create status : {endpoint_stage_status} ({timedelta(seconds=waiting_time_seconds)}) Please wait...")
                time.sleep(constants.EASYMAKER_API_WAIT_INTERVAL_SECONDS)
                waiting_time_seconds += constants.EASYMAKER_API_WAIT_INTERVAL_SECONDS
                default_endpoint_stage_info = self.easymaker_api_sender.get_endpoint_stage_by_id(endpoint_stage_id)
                endpoint_stage_status = default_endpoint_stage_info["endpointStageStatusCode"]
                if "FAIL" in endpoint_stage_status:
                    raise exceptions.EasyMakerError(default_endpoint_stage_info)
            print(f"[AI EasyMaker] Endpoint create complete. Endpoint Id : {self.endpoint_id}, Default Stage Id : {endpoint_stage_id}")
        else:
            print(f"[AI EasyMaker] Endpoint create request complete. Endpoint Id : {self.endpoint_id}")
        return self.endpoint_id

    def create_stage(
        self,
        stage_name,
        endpoint_instance_name,
        endpoint_model_resource_list,
        endpoint_instance_count=1,
        stage_description=None,
        tag_list=None,
        use_log=False,
        wait=True,
        autoscaler_enable=False,
        autoscaler_min_node_count=1,
        autoscaler_max_node_count=10,
        autoscaler_scale_down_enable=True,
        autoscaler_scale_down_util_threshold=50,
        autoscaler_scale_down_unneeded_time=10,
        autoscaler_scale_down_delay_after_add=10,
    ):
        """
        Returns:
            endpoint_stage_id(str)
        """

        self.instance_list = self.easymaker_api_sender.get_instance_list()
        response = self.easymaker_api_sender.create_stage(
            endpoint_id=self.endpoint_id,
            stage_name=stage_name,
            stage_description=stage_description,
            flavor_id=utils.from_name_to_id(self.instance_list, endpoint_instance_name),
            endpoint_model_resource_list=endpoint_model_resource_list,
            node_count=endpoint_instance_count,
            tag_list=tag_list,
            use_log=use_log,
            ca_enable=autoscaler_enable,
            ca_min_node_count=autoscaler_min_node_count,
            ca_max_node_count=autoscaler_max_node_count,
            ca_scale_down_enable=autoscaler_scale_down_enable,
            ca_scale_down_util_thresh=autoscaler_scale_down_util_threshold,
            ca_scale_down_unneeded_time=autoscaler_scale_down_unneeded_time,
            ca_scale_down_delay_after_add=autoscaler_scale_down_delay_after_add,
        )
        endpoint_stage = {}
        endpoint_stage_id = response["endpointStage"]["endpointStageId"]
        if wait:
            waiting_time_seconds = 0
            endpoint_stage_status = "CREATE_REQUESTED"
            while endpoint_stage_status != "ACTIVE":
                print(f"[AI EasyMaker] Endpoint stage create status : {endpoint_stage_status} ({timedelta(seconds=waiting_time_seconds)}) Please wait...")
                time.sleep(constants.EASYMAKER_API_WAIT_INTERVAL_SECONDS)
                waiting_time_seconds += constants.EASYMAKER_API_WAIT_INTERVAL_SECONDS
                endpoint_stage = self.easymaker_api_sender.get_endpoint_stage_by_id(endpoint_stage_id)
                endpoint_stage_status = endpoint_stage["endpointStageStatusCode"]
                if "FAIL" in endpoint_stage_status:
                    raise exceptions.EasyMakerError(endpoint_stage)
            print(f"[AI EasyMaker] Stage create complete. Stage Id : {endpoint_stage_id}")
        else:
            print(f"[AI EasyMaker] Stage create request complete.")
        return endpoint_stage_id

    def get_endpoint_list(self):
        return self.easymaker_api_sender.get_endpoint_list()

    def get_endpoint_by_id(self):
        return self.easymaker_api_sender.get_endpoint_by_id(self.endpoint_id)

    def get_endpoint_stage_list(self):
        return self.easymaker_api_sender.get_endpoint_stage_list(self.endpoint_id)

    def get_default_endpoint_stage(self):
        endpoint_stage_list = self.easymaker_api_sender.get_endpoint_stage_list(self.endpoint_id)

        for endpoint_stage in endpoint_stage_list:
            if endpoint_stage["defaultStage"]:
                return endpoint_stage

        return None

    def get_endpoint_stage_by_id(self, endpoint_stage_id):
        return self.easymaker_api_sender.get_endpoint_stage_by_id(endpoint_stage_id=endpoint_stage_id)

    def get_endpoint_model_list(self, endpoint_stage_id):
        return self.easymaker_api_sender.get_endpoint_model_list(endpoint_stage_id=endpoint_stage_id)

    def get_endpoint_model_by_id(self, endpoint_model_id):
        return self.easymaker_api_sender.get_endpoint_model_by_id(endpoint_model_id=endpoint_model_id)

    def delete_endpoint(self, endpoint_id):
        response = self.easymaker_api_sender.delete_endpoint_by_id(endpoint_id=endpoint_id)
        print(f"[AI EasyMaker] Endpoint delete request complete. Endpoint Id : {endpoint_id}")
        return response

    def delete_endpoint_stage(self, endpoint_stage_id):
        response = self.easymaker_api_sender.delete_endpoint_stage_by_id(endpoint_stage_id=endpoint_stage_id)
        print(f"[AI EasyMaker] Endpoint stage delete request complete. Endpoint stage Id : {endpoint_stage_id}")
        return response

    def delete_endpoint_model(self, endpoint_model_id):
        response = self.easymaker_api_sender.delete_endpoint_model_by_id(endpoint_model_id=endpoint_model_id)
        print(f"[AI EasyMaker] Endpoint model delete request complete. Endpoint model Id : {endpoint_model_id}")
        return response

    def predict(self, endpoint_stage_info, model_id, json=None, files=None, data=None, headers=None):
        endpoint_url = "https://" + endpoint_stage_info["apigwStageUrl"]
        resource_uri = next((x for x in endpoint_stage_info["endpointModelList"] if x["modelId"] == model_id), {}).get("apigwResourceUri", "")
        endpoint_url = endpoint_url + resource_uri

        response = requests.post(endpoint_url, json=json, files=files, data=data, headers=headers).json()
        return response

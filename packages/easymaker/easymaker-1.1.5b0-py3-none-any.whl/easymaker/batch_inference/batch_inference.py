import time
from datetime import timedelta

import easymaker
from easymaker.common import constants, exceptions, utils
from easymaker.common.utils import status_code_utils


class BatchInference:

    def __init__(self):
        self.easymaker_api_sender = easymaker.easymaker_config.api_sender
        self.instance_list = self.easymaker_api_sender.get_instance_list()
        self.model_list = self.easymaker_api_sender.get_model_list()

    def run(
        self,
        batch_inference_name=None,
        instance_count=1,
        timeout_hours=720,
        instance_name=None,
        model_name=None,
        #
        pod_count=1,
        batch_size=32,
        inference_timeout_seconds=120,
        #
        input_data_uri=None,
        input_data_type=None,
        include_glob_pattern=None,
        exclude_glob_pattern=None,
        output_upload_uri=None,
        #
        data_storage_size=None,
        #
        description=None,
        tag_list=None,
        use_log=False,
        wait=True,
    ):
        """
        Returns:
            batch_inference_id
        """

        # run batch_inference
        response = self.easymaker_api_sender.run_batch_inference(
            batch_inference_name=batch_inference_name,
            instance_count=instance_count,
            timeout_minutes=timeout_hours * 60,
            flavor_id=utils.from_name_to_id(self.instance_list, instance_name),
            model_id=utils.from_name_to_id(self.model_list, model_name),
            #
            pod_count=pod_count,
            max_batch_size=batch_size,
            inference_timeout_seconds=inference_timeout_seconds,
            #
            input_data_uri=input_data_uri,
            input_data_type_code=input_data_type,
            include_glob_pattern=include_glob_pattern,
            exclude_glob_pattern=exclude_glob_pattern,
            output_upload_uri=output_upload_uri,
            #
            data_storage_size=data_storage_size,
            #
            description=description,
            tag_list=tag_list,
            use_log=use_log,
        )

        batch_inference_id = response["batchInference"]["batchInferenceId"]
        if wait:
            waiting_time_seconds = 0
            batch_inference_status = status_code_utils.replace_status_code(response["batchInference"]["batchInferenceStatusCode"])
            while batch_inference_status != "COMPLETE":
                print(f"[AI EasyMaker] Batch Inference create status : {batch_inference_status} ({timedelta(seconds=waiting_time_seconds)}) Please wait...")
                time.sleep(constants.EASYMAKER_API_WAIT_INTERVAL_SECONDS)
                waiting_time_seconds += constants.EASYMAKER_API_WAIT_INTERVAL_SECONDS
                batch_inference = self.easymaker_api_sender.get_batch_inference_by_id(batch_inference_id)
                batch_inference_status = status_code_utils.replace_status_code(batch_inference["batchInference"]["batchInferenceStatusCode"])
                if "FAIL" in batch_inference_status or "STOPPED" in batch_inference_status:
                    batch_inference["batchInference"]["batchInferenceStatusCode"] = batch_inference_status
                    raise exceptions.EasyMakerError(batch_inference)
            print(f"[AI EasyMaker] Batch Inference create complete. Batch Inference Id : {batch_inference_id}")
        else:
            print(f"[AI EasyMaker] Batch Inference create request complete. Batch Inference Id : {batch_inference_id}")
        return batch_inference_id

    def delete(self, batch_inference_id):
        response = self.easymaker_api_sender.delete_batch_inference_by_id(batch_inference_id=batch_inference_id)
        print(f"[AI EasyMaker] Batch Inference delete request complete. Batch Inference Id : {batch_inference_id}")
        return response

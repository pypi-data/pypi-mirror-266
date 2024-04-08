import time
from datetime import timedelta

import easymaker
from easymaker.common import constants, exceptions
from easymaker.common.utils import status_code_utils


class Experiment:
    def __init__(self):
        self.easymaker_api_sender = easymaker.easymaker_config.api_sender

    def create(self, experiment_name, experiment_description=None, wait=True):
        """
        Args:
            experiment_name (str): Experiment name
            experiment_description (str): Experiment description
            wait (bool): wait for the job to complete
        Returns:
            experiment_id
        """
        response = self.easymaker_api_sender.create_experiment(experiment_name=experiment_name, experiment_description=experiment_description)
        experiment_id = response["experiment"]["experimentId"]
        if wait:
            waiting_time_seconds = 0
            experiment_status = status_code_utils.replace_status_code(response["experiment"]["experimentStatusCode"])
            while experiment_status != "ACTIVE":
                print(f"[AI EasyMaker] Experiment create status : {experiment_status} ({timedelta(seconds=waiting_time_seconds)}) Please wait...")
                time.sleep(constants.EASYMAKER_API_WAIT_INTERVAL_SECONDS)
                waiting_time_seconds += constants.EASYMAKER_API_WAIT_INTERVAL_SECONDS
                experiment = self.easymaker_api_sender.get_experiment_by_id(experiment_id)
                experiment_status = status_code_utils.replace_status_code(experiment["experiment"]["experimentStatusCode"])
                if "FAIL" in experiment_status:
                    experiment["experiment"]["experimentStatusCode"] = experiment_status
                    raise exceptions.EasyMakerError(experiment)
            print(f"[AI EasyMaker] Experiment create complete. Experiment Id : {experiment_id}")
        else:
            print(f"[AI EasyMaker] Experiment create request complete. Experiment Id : {experiment_id}")

        return experiment_id

    def delete(self, experiment_id):
        response = self.easymaker_api_sender.delete_experiment_by_id(experiment_id=experiment_id)
        print(f"[AI EasyMaker] Experiment delete request complete. Experiment Id : {experiment_id}")
        return response

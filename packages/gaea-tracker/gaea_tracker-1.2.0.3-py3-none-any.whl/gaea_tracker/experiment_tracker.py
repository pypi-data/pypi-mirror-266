#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File          : experiment_tracker.py
@Date          : 2023/5/22
@Description   :
"""
import os
from typing import Dict, List
import json
from jsonschema import validate
import yaml

from windmillclient.client.windmill_client import WindmillClient
from windmilltrainingv1.client.training_api_job import parse_job_name
from windmilltrainingv1.client.training_api_project import parse_project_name


class ExperimentTracker(object):
    """
    Run object used for tracking metrics.
    """
    all_kind = ("Aim", "MLFlow")
    default_param_name = "config"

    def __init__(
            self,
            windmill_client: WindmillClient,
            tracking_uri: str,
            experiment_name: str,
            run_name: str = None,
            experiment_kind: str = "Aim",
            project_name: str = None):
        self.windmill_client = windmill_client
        self._experiment_name = experiment_name
        self.config_param = {}
        self._work_dir = ""
        self._job_work_dir = ""
        self._extra_work_dir = ""
        self._project_name = project_name
        self._job_kind = "train"

        self._job_name = None
        if self._project_name is not None:
            self._job_name = self._get_windmill_job()
        # 如果run name为空，则job name作为run name
        if run_name is None:
            run_name = self._job_name

        if experiment_kind == self.all_kind[0]:
            from .aim_tracker import AimTracker
            self.tracker = AimTracker(tracking_uri=tracking_uri, experiment_name=experiment_name, run_name=run_name)
        elif experiment_kind == self.all_kind[1]:
            from .mlflow_tracker import MLFlowTracker
            self.tracker = MLFlowTracker(tracking_uri=tracking_uri, experiment_name=experiment_name, run_name=run_name)
        else:
            raise KeyError(f'{experiment_kind} is not in the {self.all_kind}, please set one of.')

        if self._job_name is not None:
            self._update_run_id(run_id=self.run_id, name=self._job_name)
        self.log_params(self.config_param, name=self.default_param_name)
        self.log_tags(tags=[self.job_kind])

        os.environ["WINDMILL_EXPERIMENT_RUN_ID"] = self.run_id
        os.environ["WINDMILL_EXPERIMENT_WORK_DIR"] = self.job_work_dir

    @property
    def experiment_name(self):
        """
        Get experiment name.
        """
        return self._experiment_name

    @property
    def job_name(self):
        """
        Get job name.
        """
        return self._job_name

    @property
    def run_id(self):
        """
        Get the run id.
        """
        return self.tracker.get_run_id()

    @property
    def work_dir(self):
        """
        Get work dir.
        """
        return self._work_dir

    @property
    def extra_work_dir(self):
        """
        Get extra work dir.
        """
        return self._extra_work_dir

    @property
    def job_work_dir(self):
        """
        Get work dir.
        """
        return self._job_work_dir

    @property
    def job_kind(self):
        """
        Get job kind.
        """
        return self._job_kind

    @property
    def project_name(self):
        """
        Get project name.
        """
        return self._project_name

    @project_name.setter
    def project_name(self, name: str):
        """
        Set project name.
        """
        self._project_name = name

    def _update_run_id(self, run_id: str, name: str):
        """
        Update the run id.
        """
        job_instance = parse_job_name(name)
        workspace_id = job_instance.workspace_id
        project_name = job_instance.project_name
        local_name = job_instance.local_name
        response = self.windmill_client.get_job(workspace_id=workspace_id,
                                                project_name=project_name,
                                                local_name=local_name)
        experiment_runs = response.experimentRuns
        if experiment_runs is None:
            experiment_runs = {}
        experiment_runs.update({self.job_kind: run_id})
        self.windmill_client.update_job(workspace_id=workspace_id,
                                        project_name=project_name,
                                        display_name=response.displayName,
                                        local_name=local_name,
                                        experiment_runs=experiment_runs)

    def _get_windmill_job(self):
        """
        Get windmill job.
        """
        project_instance = parse_project_name(self.project_name)
        workspace_id, project_name = project_instance.workspace_id, project_instance.local_name
        if "PF_RUN_ID" in os.environ and "PF_STEP_NAME" in os.environ:
            paddleflow_run_id = os.environ["PF_RUN_ID"]
            self._job_kind = os.environ["PF_STEP_NAME"]
            self._work_dir = os.environ["PF_WORK_DIR"]
            self._extra_work_dir = os.environ.get("PF_EXTRA_WORK_DIR")
            response = self.windmill_client.get_job(workspace_id=workspace_id,
                                                    project_name=project_name,
                                                    local_name=paddleflow_run_id,
                                                    naming_kind="runID")
            assert response.name is not None, \
                f"The job name is empty, " \
                f"please check your request workspace_id={workspace_id} project_name={project_name} " \
                f"local_name={paddleflow_run_id} naming_kind=runID, " \
                f"response is {response}"
            name = response.name
            self.config_param = {"org_id": response.orgID, "project_name": response.projectName}
            self._job_work_dir = os.path.join(self.work_dir, name, self._job_kind)
            if not os.path.exists(self._job_work_dir):
                os.makedirs(self._job_work_dir, exist_ok=True)
        else:
            self.config_param = {"org_id": "", "project_name": ""}
            name = ""
            self._work_dir = ""
            self._job_work_dir = ""

        return name

    def log_tags(self, tags: List):
        """
        Add tag to run.
        """
        self.tracker.log_tags(tags)

    def log_params(self, params: Dict, name: str):
        """
        Log a batch of params for the current run.
        """
        if name == self.default_param_name:
            params.update(self.config_param)
        self.tracker.log_params(params, name)

    def log_metrics(self, metrics: Dict, epoch: int = None, step: int = None):
        """
        Log multiple metrics for the current run.
        """
        self.tracker.log_metrics(metrics=metrics, epoch=epoch, step=step)

    def save_metrics(self, metrics: Dict, file_name: str = "metric.json", schema_file: str = ""):
        """
        Write multiple metrics for the current run.
        """
        file_path = os.path.join(self._work_dir, file_name)
        if schema_file != "":
            with open(schema_file) as fp:
                schema_data = yaml.load(fp, Loader=yaml.Loader)

            validate(instance=metrics, schema=schema_data)
        with open(file_path, "w") as fp:
            json.dump(metrics, fp, indent=4, ensure_ascii=False)

    def log_predict(self):
        """
        Log model predict on image for the current run.
        """
        pass

    def close(self) -> None:
        """
        close
        """
        self.tracker.close()

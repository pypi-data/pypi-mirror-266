#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File          : mlflow_tracker.py
@Date          : 2023/5/22
@Description   :
"""
from typing import Dict, List
import mlflow


class MLFlowTracker(object):
    """
    MLFlow tracker to log parameters and metrics during the training and validation.
    """
    def __init__(self, tracking_uri: str, experiment_name: str, run_name: str = None):
        mlflow.set_tracking_uri(tracking_uri)
        experiment_name = mlflow.set_experiment(experiment_name=experiment_name)
        experiment_id = experiment_name.experiment_id
        self.active_run = mlflow.start_run(experiment_id=experiment_id, run_name=run_name)

    def get_run_id(self):
        """
        Get run id
        """
        return self.active_run.__hash__()

    def log_tags(self, tags: List):
        """
        Add tag to run.
        """
        pass

    def log_params(self, params: Dict, name: str):
        """
        Log a batch of params for the current run.
        """
        mlflow.log_params(params=params)

    def log_metrics(self, metrics: Dict, epoch: int, step: int):
        """
        Log multiple metrics for the current run.
        """
        mlflow.log_metrics(metrics=metrics, step=epoch)

    def log_predict(self):
        """
        Log model predict on image for the current run.
        """
        pass

    def close(self) -> None:
        """
        close
        """
        mlflow.end_run()

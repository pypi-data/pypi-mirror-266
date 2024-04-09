#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File          : aim_tracker.py
@Date          : 2023/5/22
@Description   :
"""
import aim
from typing import Dict, List


class AimTracker(object):
    """
    Aim tracker to log parameters and metrics during the training and validation.
    """
    def __init__(self, tracking_uri: str, experiment_name: str, run_name: str = None):
        self.aim_run = aim.Run(repo=tracking_uri,
                               experiment=experiment_name,
                               log_system_params=True,
                               capture_terminal_logs=True)
        if run_name is not None and len(run_name) > 0:
            self.aim_run.name = run_name

    def get_run_id(self):
        """
        Get run id.
        """
        return self.aim_run.hash

    def log_tags(self, tags: List):
        """
        Add tag to run.
        """
        for tag in tags:
            self.aim_run.add_tag(tag)

    def log_params(self, params: Dict, name: str):
        """
        Log a batch of params for the current run.
        """
        self.aim_run[name] = params

    def log_metrics(self, metrics: Dict, epoch: int, step: int):
        """
        Log multiple metrics for the current run.
        """
        for name, value in metrics.items():
            if isinstance(value, (int, float)):
                self.aim_run.track(value=value, name=name, epoch=epoch, step=step)

    def log_predict(self):
        """
        Log model predict on image for the current run.
        """
        pass

    def close(self) -> None:
        """
        close
        """
        self.aim_run.close()

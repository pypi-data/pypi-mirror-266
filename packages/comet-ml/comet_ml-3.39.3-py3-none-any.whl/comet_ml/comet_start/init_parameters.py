# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.com
#  Copyright (C) 2015-2023 Comet ML INC
#  This source code is licensed under the MIT license.
# *******************************************************
from typing import Optional, Union

from .._online import Experiment
from ..config import (
    get_api_key,
    get_config,
    get_previous_experiment,
    get_project_name,
    get_workspace,
)
from ..exceptions import InvalidExperimentModeUnsupported
from ..offline import OfflineExperiment
from .experiment_config import ExperimentConfig
from .start_modes import (
    RESUME_STRATEGY_CREATE,
    RESUME_STRATEGY_GET,
    RESUME_STRATEGY_GET_OR_CREATE,
    SUPPORTED_START_MODES,
)


class InitParameters:
    def __init__(
        self,
        api_key: Optional[str] = None,
        workspace: Optional[str] = None,
        project: Optional[str] = None,
        experiment_key: Optional[str] = None,
        mode: Optional[str] = None,
        online: Optional[bool] = None,
    ):
        config = get_config()
        self.api_key = get_api_key(api_key, config=config)
        self.workspace = get_workspace(workspace, config=config)
        self.project = get_project_name(project, config=config)
        self.experiment_key = get_previous_experiment(experiment_key, config=config)

        self.mode = mode
        if self.mode is None:
            self.mode = RESUME_STRATEGY_GET_OR_CREATE
        self.online = online
        if self.online is None:
            self.online = True

    def validate(self):
        if self.mode is None or self.mode not in SUPPORTED_START_MODES:
            raise InvalidExperimentModeUnsupported(
                mode=str(self.mode), supported_modes=SUPPORTED_START_MODES
            )

    def is_create(self) -> bool:
        return self.mode == RESUME_STRATEGY_CREATE

    def is_get_or_create(self) -> bool:
        return self.mode == RESUME_STRATEGY_GET_OR_CREATE

    def is_get(self) -> bool:
        return self.mode == RESUME_STRATEGY_GET

    def __str__(self):
        return "InitParameters: %r" % self.__dict__


class KeyParameters:
    """
    Holds key parameters to be compared when deciding if existing experiment is the same as requested.
    """

    def __init__(
        self,
        api_key: str,
        workspace: str,
        project: str,
        experiment_key: str,
        online: bool,
        disabled: bool,
        offline_directory: Optional[str],
        distributed_node_identifier: Optional[str],
    ):
        self.api_key = api_key
        self.workspace = workspace
        self.project = project
        self.experiment_key = experiment_key
        self.online = online
        self.disabled = disabled
        self.distributed_node_identifier = distributed_node_identifier
        if not online:
            self.offline_directory = offline_directory
        else:
            self.offline_directory = None

    def __eq__(self, other: "KeyParameters") -> bool:
        return self.__dict__ == other.__dict__

    def __str__(self) -> str:
        return "KeyParameters: %r" % self.__dict__

    @staticmethod
    def build(
        experiment_config: Optional[ExperimentConfig], init_params: InitParameters
    ) -> "KeyParameters":
        offline_directory = None
        distributed_node_identifier = None
        disabled = False
        if experiment_config is not None:
            offline_directory = experiment_config.offline_directory
            distributed_node_identifier = experiment_config.distributed_node_identifier
            disabled = experiment_config.disabled

        return KeyParameters(
            api_key=init_params.api_key,
            workspace=init_params.workspace,
            project=init_params.project,
            experiment_key=init_params.experiment_key,
            online=init_params.online,
            disabled=disabled,
            offline_directory=offline_directory,
            distributed_node_identifier=distributed_node_identifier,
        )


def key_parameters_matched(
    key_params: KeyParameters, experiment: Union[Experiment, OfflineExperiment]
) -> bool:
    offline_directory = None
    if isinstance(experiment, OfflineExperiment):
        offline_directory = experiment.offline_directory

    experiment_key_params = KeyParameters(
        api_key=experiment.api_key,
        workspace=experiment.workspace,
        project=experiment.project_name,
        experiment_key=experiment.get_key(),
        online=isinstance(experiment, Experiment),
        disabled=experiment.disabled,
        offline_directory=offline_directory,
        distributed_node_identifier=experiment.distributed_node_identifier,
    )

    return key_params == experiment_key_params

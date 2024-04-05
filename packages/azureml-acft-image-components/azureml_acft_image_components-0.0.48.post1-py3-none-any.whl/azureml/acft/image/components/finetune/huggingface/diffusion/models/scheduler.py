# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Create Noise scheduler."""

from typing import Dict, List

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.utils.error_handling.error_definitions import \
    ACFTUserError
from azureml.acft.common_components.utils.error_handling.exceptions import \
    ACFTValidationException
from azureml.acft.image.components.common.utils import get_input_params_name
from diffusers.schedulers import KarrasDiffusionSchedulers

logger = get_logger_app(__name__)


def filter_params(params: Dict, allowed_params: List[str], scheduler_name: str) -> Dict[str, any]:
    """Filter parameters based on allowed parameters for particular scheduler constructor.

    :param params: parameters
    :type params: Dict
    :param allowed_params: allowed parameters for scheduler
    :type allowed_params: List[str]
    :param scheduler_name: scheduler name
    :type scheduler_name: str
    :return: filtered parameters
    :rtype: Dict[str, any]
    """
    ignored_params = set(params.keys()) - set(allowed_params)
    if ignored_params:
        logger.warning(f"Ignored params while creating {scheduler_name}: {ignored_params}")
    return {k: v for k, v in params.items() if k in allowed_params}


class DDPMScheduler:
    """Create denoising diffusion probabilistic models scheduler."""

    @classmethod
    def get_scheduler(cls, **scheduler_args) -> "DDPMScheduler":
        """Get Denoising diffusion probabilistic models (DDPM) scheduler.

        :param scheduler_args: scheduler arguments, defaults to {}
        :type scheduler_args: dict, optional
        :return: DDPMScheduler instance
        :rtype: DDPMScheduler
        """
        from diffusers import DDPMScheduler

        allowed_params = get_input_params_name(DDPMScheduler)
        kwargs = filter_params(scheduler_args, allowed_params, "DDPMScheduler")
        return DDPMScheduler(**kwargs)


class DPMSolverMultistepScheduler:
    """Create Diffusion probabilistic models multistep scheduler."""

    @classmethod
    def get_scheduler(cls, **scheduler_args) -> "DPMSolverMultistepScheduler":
        """Get DPMSolverMultistepScheduler.

        :param scheduler_args: scheduler arguments, defaults to {}
        :type scheduler_args: dict, optional
        :return: DPMSolverMultistepScheduler instance
        :rtype: DPMSolverMultistepScheduler
        """
        from diffusers import DPMSolverMultistepScheduler

        allowed_params = get_input_params_name(DPMSolverMultistepScheduler)
        kwargs = filter_params(scheduler_args, allowed_params, "DPMSolverMultistepScheduler")

        return DPMSolverMultistepScheduler(**kwargs)


SCHEDULER_MAPPING = {
    KarrasDiffusionSchedulers.DPMSolverMultistepScheduler.name: DPMSolverMultistepScheduler,
    KarrasDiffusionSchedulers.DDPMScheduler.name: DDPMScheduler,
}


class NoiseSchedulerFactory:
    """Factory class to create noise scheduler."""

    @staticmethod
    def create_noise_scheduler(
        scheduler_type: KarrasDiffusionSchedulers, **scheduler_args: dict
    ) -> KarrasDiffusionSchedulers:
        """Create noise scheduler.

        :param scheduler_type: scheduler type
        :type scheduler_type: KarrasDiffusionSchedulers
        :param scheduler_args: scheduler arguments
        :type scheduler_args: dict
        :raises ACFTValidationException._with_error: Unsupported scheduler type
        :return: Scheduler instance
        :rtype: KarrasDiffusionSchedulers
        """
        if scheduler_type in SCHEDULER_MAPPING:
            return SCHEDULER_MAPPING[scheduler_type].get_scheduler(**scheduler_args)
        else:
            raise ACFTValidationException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=f"Unsupported scheduler type: {scheduler_type}."
                    f"Supported schedulers: {list(SCHEDULER_MAPPING.keys())}.",
                ),
            )

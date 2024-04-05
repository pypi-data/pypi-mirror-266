# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""File containing HF model related functions."""


from __future__ import annotations

from distutils.dir_util import copy_tree
from typing import Any, Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F
from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.huggingface.diffusion.models.constant import Literals
from azureml.acft.image.components.finetune.huggingface.diffusion.models.default_model_settings import DefaultSettings
from azureml.acft.image.components.finetune.huggingface.diffusion.models.scheduler import NoiseSchedulerFactory
from azureml.acft.image.components.finetune.huggingface.diffusion.models.text_encoder import TextEncoderFactory
from azureml.acft.image.components.finetune.huggingface.diffusion.models.tokenizer import TokenizerFactory
from diffusers import AutoencoderKL, DDPMScheduler, StableDiffusionPipeline, UNet2DConditionModel
from transformers import CLIPTextModel, PreTrainedTokenizer

logger = get_logger_app(__name__)


class AzuremlAutoEncoderKL:
    """File containing HF model related functions."""

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> AutoencoderKL:
        """Load Azureml AutoencoderKL pretrained model.

        :param hf_model_name_or_path: HF model name or path
        :type hf_model_name_or_path: str
        :param kwargs: Additional arguments
        :type kwargs: Dict
        :return: AutoencoderKL model
        :rtype: AutoencoderKL
        """
        revision = kwargs[Literals.REVISION]
        freeze_weights = kwargs.get(Literals.FREEZE_WEIGHTS, False)
        device: int = kwargs.get(Literals.DEVICE, torch.device(Literals.CUDA))
        weight_dtype: torch.dtype = kwargs.get(Literals.WEIGHT_DTYPE, torch.float32)

        vae = AutoencoderKL.from_pretrained(hf_model_name_or_path, subfolder=Literals.VAE, revision=revision)
        return AzuremlAutoEncoderKL._post_init(
            vae,
            freeze_weights=freeze_weights,
            device=device,
            weight_dtype=weight_dtype,
        )

    @staticmethod
    def _post_init(
        model: AutoencoderKL, freeze_weights: bool, device: int, weight_dtype: Union[str, torch.dtype]
    ) -> AutoencoderKL:
        if freeze_weights:
            model.requires_grad_(False)

        return model


class AzuremlUNet2DConditionModel:
    """Azueml UNet2DConditionModel class to handle the UNet2DConditionModel related operations."""

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> UNet2DConditionModel:
        """Load Azureml Unet2DCondition model.

        :param hf_model_name_or_path: HF model name or path
        :type hf_model_name_or_path: str
        :param kwargs: Additional arguments
        :type kwargs: Dict
        :return: UNet2DConditionModel model
        :rtype: UNet2DConditionModel
        """
        revision = kwargs[Literals.NON_EMA_REVISION]
        freeze_weights = kwargs.get(Literals.FREEZE_WEIGHTS, False)
        device: int = kwargs.get(Literals.DEVICE, torch.device(Literals.CUDA))
        weight_dtype: torch.dtype = kwargs.get(Literals.WEIGHT_DTYPE, torch.float32)

        unet = UNet2DConditionModel.from_pretrained(hf_model_name_or_path, subfolder=Literals.UNET, revision=revision)
        return AzuremlUNet2DConditionModel._post_init(
            unet,
            freeze_weights=freeze_weights,
            device=device,
            weight_dtype=weight_dtype,
        )

    @staticmethod
    def _post_init(
        model: UNet2DConditionModel, freeze_weights: bool, device: int, weight_dtype: Union[str, torch.dtype]
    ) -> UNet2DConditionModel:
        if freeze_weights:
            model.requires_grad_(False)

        return model


class AzuremlStableDiffusionPipeline(nn.Module):
    """AzuremlStableDiffusionPipeline class to handle the diffusion pipeline related operations."""

    def __init__(
        self,
        unet: UNet2DConditionModel,
        vae: AutoencoderKL,
        text_encoder: CLIPTextModel,
        noise_scheduler: DDPMScheduler,
        tokenizer: PreTrainedTokenizer,
        hf_model_name_or_path: str,
        revision: Optional[str] = None,
        weight_dtype: torch.dtype = torch.float32,
    ) -> None:
        """Initialize Azureml stable diffusion pipeline class.

        :param unet: UNet2DConditionModel model
        :type unet: UNet2DConditionModel
        :param vae: AutoencoderKL model
        :type vae: AutoencoderKL
        :param text_encoder: CLIPTextModel model
        :type text_encoder: CLIPTextModel
        :param noise_scheduler: DDPMScheduler model
        :type noise_scheduler: DDPMScheduler
        :param tokenizer: PreTrainedTokenizer model
        :type tokenizer: PreTrainedTokenizer
        :param hf_model_name_or_path: HF model name or path
        :type hf_model_name_or_path: str
        :param revision: Revision, defaults to None
        :type revision: Optional[str], optional
        :param weight_dtype: Weight dtype, defaults to torch.float32
        :type weight_dtype: torch.dtype, optional
        """
        super().__init__()

        self.unet = unet
        self.vae = vae  # require_grad set to False
        self.text_encoder = text_encoder  # require_grad set to False
        self.noise_scheduler = noise_scheduler
        self.weight_dtype = weight_dtype
        self.hf_model_name_or_path = hf_model_name_or_path
        self.revision = revision
        self.tokenizer = tokenizer

    def forward(self, input_ids: List[int], pixel_values: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass of the model.

        :param input_ids: Input ids
        :type input_ids: List[int]
        :param pixel_values: Pixel values
        :type pixel_values: torch.Tensor
        :return: Tuple of torch.Tensor and torch.Tensor
        :rtype: Tuple[torch.Tensor, torch.Tensor]
        """
        # Convert images to latent space
        latents = self.vae.encode(pixel_values.to(self.weight_dtype)).latent_dist.sample()
        latents = latents * 0.18215

        # Sample noise that we'll add to the latents
        noise = torch.randn_like(latents)
        bsz = latents.shape[0]
        # Sample a random timestep for each image
        timesteps = torch.randint(0, self.noise_scheduler.num_train_timesteps, (bsz,), device=latents.device)
        timesteps = timesteps.long()

        # Add noise to the latents according to the noise magnitude at each timestep
        # (this is the forward diffusion process)
        noisy_latents = self.noise_scheduler.add_noise(latents, noise, timesteps)

        # Get the text embedding for conditioning
        encoder_hidden_states = self.text_encoder(input_ids)[0]

        # Predict the noise residual and compute loss
        model_pred = self.unet(noisy_latents, timesteps, encoder_hidden_states).sample
        loss = F.mse_loss(model_pred.float(), noise.float(), reduction="mean")

        return loss, model_pred

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> "AzuremlStableDiffusionPipeline":
        """Get Azureml stable difffusion pipeline pretrained model.

        :param hf_model_name_or_path: HF model name or path
        :type hf_model_name_or_path: str
        :param kwargs: Additional arguments
        :type kwargs: Dict
        :return: AzuremlStableDiffusion Pipeline
        :rtype: AzuremlStableDiffusionPipeline
        """
        _ = kwargs.get(Literals.NON_EMA_REVISION, None)
        revision = kwargs.get(Literals.REVISION, None)
        weight_dtype = kwargs.get(Literals.WEIGHT_DTYPE, torch.float32)
        device = torch.device(Literals.CUDA if torch.cuda.is_available() else Literals.CPU)

        # set the vae, noise_scheduler and text encoder
        # freezing the weights for vae and text_encoder
        vae = AzuremlAutoEncoderKL.from_pretrained(
            hf_model_name_or_path, revision=revision, freeze_weights=True, weight_dtype=weight_dtype, device=device
        )

        unet: UNet2DConditionModel = AzuremlUNet2DConditionModel.from_pretrained(
            hf_model_name_or_path, non_ema_revision=revision
        )

        text_encoder_type = kwargs.pop(Literals.TEXT_ENCODER_TYPE, DefaultSettings.text_encoder_type)
        text_encoder_name_or_path = kwargs.pop(Literals.TEXT_ENCODER_NAME_OR_PATH, hf_model_name_or_path)
        text_encoder = TextEncoderFactory.get_text_encoder(
            text_encoder_type=text_encoder_type, text_encoder_name_or_path=text_encoder_name_or_path, **kwargs
        )

        scheduler_type = kwargs.pop(Literals.SCHEDULER_TYPE, DefaultSettings.scheduler_type)
        noise_scheduler = NoiseSchedulerFactory.create_noise_scheduler(scheduler_type, **kwargs)

        tokenizer_name_or_path = kwargs.pop(Literals.TOKENIZER_NAME_OR_PATH, hf_model_name_or_path)
        tokenizer = TokenizerFactory.from_pretrained(tokenizer_name_or_path, **kwargs)

        return cls(
            unet=unet,
            vae=vae,
            text_encoder=text_encoder,
            noise_scheduler=noise_scheduler,
            weight_dtype=weight_dtype,
            hf_model_name_or_path=hf_model_name_or_path,
            revision=revision,
            tokenizer=tokenizer,
        )

    def save_pretrained(self, output_dir: str, state_dict: Optional[Dict[str, Any]] = None) -> None:
        """Save the model to the output directory.

        :param output_dir: Output directory
        :type output_dir: str
        :param state_dict: State dictionary, defaults to None
        :type state_dict: Optional[Dict[str, Any]], optional
        """
        pipeline = StableDiffusionPipeline.from_pretrained(
            self.hf_model_name_or_path,
            text_encoder=self.text_encoder,
            vae=self.vae,
            unet=self.unet,
            revision=self.revision,
        )
        pipeline.save_pretrained(output_dir)

    @property
    def config(self) -> str:
        """Config property."""
        return ""

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Model specific settings literals."""


class Literals:
    """Model specific settings literals."""

    # Model loading specific constants
    SCHEDULER_NAME_OR_PATH = "scheduler_name_or_path"
    SCHEDULER_TYPE = "scheduler_type"
    TEXT_ENCODER_NAME_OR_PATH = "text_encoder_name_or_path"
    TEXT_ENCODER_TYPE = "text_encoder_type"
    TOKENIZER_NAME_OR_PATH = "tokenizer_name_or_path"
    REVISION = "revision"
    FREEZE_WEIGHTS = "freeze_weights"
    DEVICE = "device"
    CUDA = "cuda"
    CPU = "cpu"
    WEIGHT_DTYPE = "weight_dtype"
    NON_EMA_REVISION = "non_ema_revision"
    UNET = "unet"
    VAE = "vae"

    # Text encoder model names
    ROBERTA_SERIES_MODEL_WITH_TRANSFORMATION = "RobertaSeriesModelWithTransformation"
    CLIP_TEXT_MODEL = "CLIPTextModel"
    T5ENCODER_MODEL = "T5EncoderModel"

    # tokenizer names
    OPENAI_CLIP_VIT_LARGE_PATCH14 = "openai/clip-vit-large-patch14"

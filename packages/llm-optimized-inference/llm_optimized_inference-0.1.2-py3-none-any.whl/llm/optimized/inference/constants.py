# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""This module defines the EngineName and TaskType enums."""
from enum import Enum


class EngineName(str, Enum):
    """Enum representing the names of the engines."""

    HF = "hf"
    VLLM = "vllm"
    MII = "mii"
    MII_V1 = "mii-v1"

    def __str__(self):
        """Return the string representation of the engine name."""
        return self.value


class TaskType(str, Enum):
    """Enum representing the types of tasks."""

    TEXT_GENERATION = "text-generation"
    CONVERSATIONAL = "conversational"
    TEXT_TO_IMAGE = "text-to-image"
    TEXT_CLASSIFICATION = "text-classification"
    TEXT_CLASSIFICATION_MULTILABEL = "text-classification-multilabel"
    NER = "text-named-entity-recognition"
    SUMMARIZATION = "text-summarization"
    QnA = "question-answering"
    TRANSLATION = "text-translation"
    TEXT_GENERATION_CODE = "text-generation-code"
    FILL_MASK = "fill-mask"
    CHAT_COMPLETION = "chat-completion"
    TEXT_TO_IMAGE_INPAINTING = "text-to-image-inpainting"

    def __str__(self):
        """Return the string representation of the task type."""
        return self.value


class SupportedTask:
    """Supported tasks by text-generation-inference."""

    TEXT_GENERATION = "text-generation"
    CHAT_COMPLETION = "chat-completion"
    TEXT_TO_IMAGE = "text-to-image"
    TEXT_CLASSIFICATION = "text-classification"
    TEXT_CLASSIFICATION_MULTILABEL = "text-classification-multilabel"
    NER = "token-classification"
    SUMMARIZATION = "summarization"
    QnA = "question-answering"
    TRANSLATION = "translation"
    TEXT_GENERATION_CODE = "text-generation-code"
    FILL_MASK = "fill-mask"
    TEXT_TO_IMAGE_INPAINTING = "text-to-image-inpainting"


class ServerSetupParams:
    """Parameters for setting up the server."""

    WAIT_TIME_MIN = 15  # time to wait for the server to become healthy
    DEFAULT_WORKER_COUNT = 1


class VLLMSupportedModels:
    """VLLM Supported Models List."""

    Models = {
        "AquilaForCausalLM",
        "BaiChuanForCausalLM",
        "BloomForCausalLM",
        "ChatGLMModel",
        "DeciLMForCausalLM",
        "FalconForCausalLM",
        "GemmaForCausalLM",
        "GPT2LMHeadModel",
        "GPTBigCodeForCausalLM",
        "GPTJForCausalLM",
        "GPTNeoXForCausalLM",
        "InternLMForCausalLM",
        "InternLM2ForCausalLM",
        "LlamaForCausalLM",
        "MistralForCausalLM",
        "MixtralForCausalLM",
        "MPTForCausalLM",
        "OLMoForCausalLM",
        "OPTForCausalLM",
        "OrionForCausalLM",
        "QWenLMHeadModel",
        "Qwen2ForCausalLM",
        "RWForCausalLM",
        "StableLmForCausalLM",
        "DbrxForCausalLM"
    }


class MIISupportedModels:
    """MII Supported Models."""

    # TODO: Add more models from different tasks

    Models = {
        "BloomForCausalLM",
        "GPT2LMHeadModel",
        "GPTBigCodeForCausalLM",
        "GPTJForCausalLM",
        "GPTNeoXForCausalLM",
        "LlamaForCausalLM",
        "OPTForCausalLM",
        "FalconForCausalLM",
        "MistralForCausalLM",
        "MixtralForCausalLM",
        "PhiForCausalLM",
        "QWenLMHeadModel"
    }


class VLLMSpecialModels:
    """Models Types that require additional parameters to work with vllm."""

    # TODO: Remove "RefinedWebModel" and "RefinedWeb" once falcon models are updated to latest huggingface commit

    Models = {
        "falcon": {"kwargs": {"gpu-memory-utilization": .95}, "args": ["trust-remote-code"]},
        "RefinedWebModel": {"kwargs": {"gpu-memory-utilization": .95}, "args": ["trust-remote-code"]},
        "RefinedWeb": {"kwargs": {"gpu-memory-utilization": .95}, "args": ["trust-remote-code"]},
        "dbrx": {"args": ["trust-remote-code"]},
        "deci_lm": {"args": ["trust-remote-code"]}
    }

    @classmethod
    def get_kwargs(cls, model_type: str):
        """Get the kwargs the vllm server needs for the model type."""
        params = cls.Models.get(model_type, {})
        return params.get("kwargs", {})

    @classmethod
    def get_args(cls, model_type: str):
        """Get the args the vllm server needs for the model type."""
        params = cls.Models.get(model_type, {})
        return params.get("args", [])


ALL_TASKS = [
    SupportedTask.TEXT_TO_IMAGE,
    SupportedTask.TEXT_CLASSIFICATION,
    SupportedTask.TEXT_CLASSIFICATION_MULTILABEL,
    SupportedTask.NER,
    SupportedTask.SUMMARIZATION,
    SupportedTask.QnA,
    SupportedTask.TRANSLATION,
    SupportedTask.FILL_MASK,
    SupportedTask.TEXT_GENERATION,
    SupportedTask.CHAT_COMPLETION,
]

VLLM_MII_TASKS = [
    SupportedTask.TEXT_GENERATION,
    SupportedTask.CHAT_COMPLETION,
    TaskType.CONVERSATIONAL
]

MULTILABEL_SET = [
    SupportedTask.TEXT_CLASSIFICATION_MULTILABEL,
]

CLASSIFICATION_SET = [
    SupportedTask.TEXT_CLASSIFICATION,
    SupportedTask.TEXT_CLASSIFICATION_MULTILABEL
]

MULTIPLE_OUTPUTS_SET = [
    SupportedTask.NER,
    SupportedTask.TEXT_CLASSIFICATION_MULTILABEL
]

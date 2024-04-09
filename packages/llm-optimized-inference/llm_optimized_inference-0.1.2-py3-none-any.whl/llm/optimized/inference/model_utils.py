# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
"""This module provides mlflow model realted utilities."""
import json
import os


from llm.optimized.inference.constants import SupportedTask, ALL_TASKS, TaskType, VLLM_MII_TASKS
from llm.optimized.inference.constants import EngineName, VLLMSupportedModels, MIISupportedModels
from llm.optimized.inference.model_config_factory import ModelConfigFactory
from llm.optimized.inference.utils import map_env_vars_to_vllm_server_args
from llm.optimized.inference.logging_config import configure_logger
from copy import deepcopy

logger = configure_logger(__name__)


def get_generator_params(params: dict):
    """Return accumulated generator params."""
    updated_params = {}
    # map 'max_gen_len' to 'max_new_tokens' if present
    if "max_gen_len" in params:
        logger.warning("max_gen_len is deprecated. Use max_new_tokens")
        params["max_new_tokens"] = params["max_gen_len"]
        del params["max_gen_len"]

    updated_params.update(params)
    return updated_params


def get_model_size(model_path):
    """Funciton to estimate the size of model in GBs."""
    size = 0
    # get size
    for path, dirs, files in os.walk(model_path):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)
    size /= (pow(1024, 3))
    return size


def get_best_engine(config_path):
    """Get best engine based on architecture."""
    if not os.path.exists(config_path):
        logger.info("No config file found.\
                    Passing the default HF engine as best engine.")
        return EngineName.HF
    with open(config_path) as f:
        model_config = json.load(f)
    model_class = model_config["architectures"][0]
    best_engine = EngineName.HF
    if model_class in VLLMSupportedModels.Models:
        best_engine = EngineName.VLLM
    elif model_class in MIISupportedModels.Models:
        best_engine = EngineName.MII
    return best_engine


def build_configs_from_model(mlmodel, model_path, config_path, tokenizer_path):
    """Build engine and task config from mlflow model."""
    default_generator_configs = ""
    ml_model_info = {}

    default_engine = get_best_engine(config_path)
    tensor_parallel = os.getenv("TENSOR_PARALLEL", None)
    if tensor_parallel:
        try:
            tensor_parallel = int(tensor_parallel)
        except ValueError:
            tensor_parallel = None
    engine_config = {
        "engine_name": os.getenv("ENGINE_NAME", default_engine),
        "model_id": model_path,
        "tensor_parallel": tensor_parallel
    }
    engine_config["hf_config_path"] = os.path.dirname(config_path)
    engine_config["tokenizer"] = tokenizer_path
    task_config = {}

    if mlmodel:
        flavors = mlmodel.get("flavors", {})

        if "transformers" in flavors:
            task_type = flavors["transformers"]["task"]
            flavors_dict = flavors.get("transformers")
            ml_model_info = deepcopy(flavors_dict)
            if ml_model_info.get("tokenizer_type", None):
                ml_model_info["hf_tokenizer_class"] = ml_model_info.get("tokenizer_type")
            if ml_model_info.get("pipeline_model_type", None):
                ml_model_info["hf_pretrained_class"] = ml_model_info.get("pipeline_model_type")
            model_generator_configs = {}
            if os.path.exists(os.path.join(model_path, "generation_config.json")):
                with open(os.path.join(model_path, "generation_config.json")) as f:
                    model_generator_configs.update(json.load(f))
            default_generator_configs = get_generator_params(
                model_generator_configs
            )
        elif "hftransformersv2" in flavors:
            task_type = flavors["hftransformersv2"]["task_type"]
            model_generator_configs = flavors["hftransformersv2"].get(
                "generator_config",
                {},
            )
            ml_model_info = flavors["hftransformersv2"].copy()
            if task_type not in ALL_TASKS:
                raise Exception(f"Unsupported task_type {task_type}")

            # update default gen configs with model configs
            default_generator_configs = get_generator_params(
                model_generator_configs,
            )
        elif "python_function" in flavors:
            task_type = mlmodel["metadata"]["base_model_task"]
            if task_type not in [TaskType.TEXT_TO_IMAGE, TaskType.TEXT_TO_IMAGE_INPAINTING]:
                raise Exception(f"Unsupported task_type {task_type}")

            model_type = mlmodel["metadata"].get("model_type", "")

            model_config_builder = ModelConfigFactory.get_config_builder(task=task_type, model_type=model_type)
            engine_config.update(
                {
                    "engine_name": model_config_builder.engine,
                    "mii_config": model_config_builder.get_optimization_config(),
                    "custom_model_config_builder": model_config_builder,
                    "model_id": os.path.join(os.getenv("AZUREML_MODEL_DIR", ""), model_config_builder.model_path),
                    "tokenizer": os.path.join(os.getenv("AZUREML_MODEL_DIR", ""),
                                              model_config_builder.MLFLOW_MODEL_PATH,
                                              "tokenizer"),
                    "tensor_parallel": model_config_builder.tensor_parallel
                }
            )
            task_config = model_config_builder.get_task_config()

    if task_type != TaskType.TEXT_TO_IMAGE:
        if engine_config["engine_name"] in [EngineName.MII, EngineName.VLLM] and task_type not in VLLM_MII_TASKS:
            engine_config["engine_name"] = EngineName.HF

    if engine_config["engine_name"] == EngineName.MII or engine_config["engine_name"] == EngineName.MII_V1:
        mii_engine_config = {
            "deployment_name": os.getenv("DEPLOYMENT_NAME", "llama-deployment"),
            "mii_configs": {},
        }

        engine_config["mii_config"] = mii_engine_config

    if engine_config["engine_name"] == EngineName.VLLM:
        model_config = {}
        vllm_config = map_env_vars_to_vllm_server_args()
        if config_path and os.path.exists(config_path):
            with open(config_path) as config_content:
                model_config = json.load(config_content)
        engine_config["vllm_config"] = vllm_config
        engine_config["model_config"] = model_config

    engine_config["ml_model_info"] = ml_model_info

    task_config = {
        "task_type": TaskType.CONVERSATIONAL
        if task_type == SupportedTask.CHAT_COMPLETION
        else task_type,
    }
    return engine_config, task_config, default_generator_configs, task_type

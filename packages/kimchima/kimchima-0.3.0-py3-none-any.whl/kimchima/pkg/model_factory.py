# coding=utf-8
# Copyright [2024] [SkywardAI]
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from transformers import AutoModel, AutoModelForCausalLM
from kimchima.pkg import logging

logger = logging.get_logger(__name__)


class ModelFactory:
    r"""
    ModelFactory class to get the model from the specified model.

    Args:
        pretrained_model_name_or_path: pretrained model name or path
    """
    def __init__(self):
        raise EnvironmentError(
            "ModelFactory is designed to be instantiated "
            "using the `ModelFactory.from_pretrained(pretrained_model_name_or_path)` method."
        )

    @classmethod                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
    def auto_model(cls, *args, **kwargs)-> AutoModel:
        r"""
        It is used to get the model from the Hugging Face Transformers AutoModel.
        
        Args:
            pretrained_model_name_or_path: pretrained model name or path

        """
        pretrained_model_name_or_path=kwargs.pop("pretrained_model_name_or_path", None)
        if pretrained_model_name_or_path is None:
            raise ValueError("pretrained_model_name_or_path cannot be None")

        quantization_config=kwargs.pop("quantization_config", None)
        model = AutoModel.from_pretrained(
            pretrained_model_name_or_path,
            quantization_config,
            **kwargs
        )
        logger.debug(f"Loaded model: {pretrained_model_name_or_path}")
        return model
    
    @classmethod
    def auto_model_for_causal_lm(cls, *args, **kwargs)-> AutoModelForCausalLM:
        r"""
        It is used to get the model from the Hugging Face Transformers AutoModelForCausalLM.
        
        Args:
            pretrained_model_name_or_path: pretrained model name or path

        """
        pretrained_model_name_or_path=kwargs.pop("pretrained_model_name_or_path", None)
        if pretrained_model_name_or_path is None:
            raise ValueError("pretrained_model_name_or_path cannot be None")

        quantization_config=kwargs.pop("quantization_config", None)
        model = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path, 
            quantization_config=quantization_config,
            device_map='auto',
            **kwargs
        )
        logger.debug(f"Loaded model: {pretrained_model_name_or_path}")
        return model


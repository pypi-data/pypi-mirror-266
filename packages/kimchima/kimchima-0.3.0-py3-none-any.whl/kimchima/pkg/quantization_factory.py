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

from kimchima.pkg import logging

import torch
from transformers import BitsAndBytesConfig

logger = logging.get_logger(__name__)

class QuantizationFactory:
    r"""
    """

    def __init__(self):
        raise EnvironmentError(
            "QuantizationFactory is designed to be instantiated "
            "using the `QuantizationFactory.from_pretrained(pretrained_model_name_or_path)` method."
        )
    
    @classmethod
    def quantization_4bit(cls, *args, **kwargs)-> BitsAndBytesConfig:
        r"""
        """
        #TODO support more parameters
        config=BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            **kwargs
            )

        return config
    
    @classmethod
    def quantization_8bit(cls, *args, **kwargs)-> BitsAndBytesConfig:
        r"""
        """
        config=BitsAndBytesConfig(
            load_in_8bit=True,
            bnb_8bit_compute_dtype=torch.bfloat16,
            **kwargs
            )

        return config

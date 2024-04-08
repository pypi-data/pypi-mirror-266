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

from enum import Enum
import torch
import platform

from typing import Tuple


class Devices(Enum):
    Silicon = 'mps'
    CPU = 'cpu'
    # only Nvidia GPU is supported currently
    GPU = 'cuda'


    @classmethod
    def get_device(cls)-> Devices:
        """
        Only support Single GPU for now
        """
        if platform.system() == 'Darwin':
            return Devices.Silicon
        elif torch.cuda.is_available():
            return Devices.GPU
        return Devices.CPU

    @classmethod
    def get_capability(cls)-> Tuple[int, int]:
        """
        Get the capability of the device(GPU) for current env, this is used for support latest quantization techniques like: Marlin
        
        Returns:
            tuple: The capability of the device(GPU) for current env.

        For not GPU env, return (0, 0)
        """
        if cls.get_device() == Devices.GPU:
            return torch.cuda.get_device_capability()
        return (0, 0)

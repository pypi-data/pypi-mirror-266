# coding=utf-8
# Copyright [2024] [Aisuko]
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import platform
import torch

from kimchima.pkg import Devices

class TestDevices(unittest.TestCase):

    def test_get_device(self):

        # Test if the device is a Mac silicon
        if platform.system() == 'Darwin':
            self.assertEqual(Devices.get_device(), Devices.Silicon)
        
        # Test if the device is a GPU
        if platform.system() != 'Darwin' and torch.cuda.is_available():
            self.assertEqual(Devices.get_device(), Devices.GPU)
        
        # Test if the device is a CPU
        if platform.system() != 'Darwin' and not torch.cuda.is_available():
            self.assertEqual(Devices.get_device(), Devices.CPU)


    def test_get_capability(self):

        # Test if the device is a GPU
        if Devices.get_device() == Devices.GPU:
            self.assertIsInstance(Devices.get_capability(), tuple)
            self.assertEqual(len(Devices.get_capability()), 2)
            self.assertIsInstance(Devices.get_capability()[0], int)
            self.assertIsInstance(Devices.get_capability()[1], int)
        
        # Test if the device is not a GPU
        if Devices.get_device() != Devices.GPU:
            self.assertEqual(Devices.get_capability(), (0, 0))

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

import unittest

from kimchima.pkg import QuantizationFactory

class TestQuantizationFactory(unittest.TestCase):

    def test_quantization_4bit(self):
        """
        Test quantization_4bit method. This function is also test the quantization dependencies
        were installed correctly.
        """

        quantization_config = QuantizationFactory.quantization_4bit()

        self.assertIsNotNone(quantization_config)
        self.assertEqual(quantization_config.load_in_4bit, True)
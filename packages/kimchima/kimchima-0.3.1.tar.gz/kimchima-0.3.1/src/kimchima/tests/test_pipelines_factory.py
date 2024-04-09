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

from kimchima.pipelines import PipelinesFactory
from kimchima.pkg import (
    ModelFactory,
    TokenizerFactory,
    StreamerFactory,
    QuantizationFactory
)


class TestPipelinesFactory(unittest.TestCase):
    
        model_name = 'gpt2'
        model=None
        tokenizer=None
        streamer=None
        quantization_config=None
    
        @classmethod
        def setUpClass(cls):
            cls.model = ModelFactory.auto_model_for_causal_lm(pretrained_model_name_or_path=cls.model_name)
            cls.tokenizer = TokenizerFactory.auto_tokenizer(pretrained_model_name_or_path=cls.model_name)
            cls.streamer = StreamerFactory.text_streamer(tokenizer=cls.tokenizer)
            cls.quantization_config = QuantizationFactory.quantization_4bit()
    
    
        @classmethod
        def tearDownClass(cls):
            pass
    
    
        def test_text_generation(self):
            """
            Test text_generation method
            """
    
            self.assertIsNotNone(self.model)
    
            pipe = PipelinesFactory.text_generation(
                model=self.model,
                tokenizer=self.tokenizer,
                text_streamer=self.streamer,
                quantization_config=self.quantization_config
                )
    
            self.assertIsNotNone(pipe)
            self.assertEqual(pipe.task, 'text-generation')

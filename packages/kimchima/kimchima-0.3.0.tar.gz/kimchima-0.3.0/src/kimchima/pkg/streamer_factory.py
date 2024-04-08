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

from transformers import (
    TextStreamer,
    TextIteratorStreamer
    )

logger = logging.get_logger(__name__)

class StreamerFactory:
    r"""
    StreamerFactory class to create Huggingface Transformers Streamer for different ML tasks.
    """

    def __init__(self):
        raise EnvironmentError(
            "StreamerFactory is designed to be instantiated "
            "using the `StreamerFactory.from_pretrained(pretrained_model_name_or_path)` method."
        )
    
    @classmethod
    def text_streamer(cls, *args, **kwargs)-> TextStreamer:
        r"""
        Get streamer for text generation task.

        Args:
            skip_prompt: skip prompt
            skip_prompt_tokens: skip prompt tokens
        """
        #TODO support more parameters
        tokenizer=kwargs.pop('tokenizer', None)
        if tokenizer is None:
            raise ValueError("tokenizer is required")
        skip_prompt=kwargs.pop('skip_prompt', False)
        skip_prompt_tokens=kwargs.pop('skip_prompt_tokens', False)

        streamer=TextStreamer(
            tokenizer=tokenizer,
            skip_prompt=skip_prompt,
            skip_prompt_tokens=skip_prompt_tokens
            )
        logger.info("TextStreamer created")

        return streamer
    
    @classmethod
    def text_iterator_streamer(cls, *args, **kwargs)-> TextIteratorStreamer:
        r"""
        Get streamer for text generation task.

        Args:
            skip_prompt: skip prompt
            skip_prompt_tokens: skip prompt tokens
        """
        #TODO support more parameters
        tokenizer=kwargs.pop('tokenizer', None)
        if tokenizer is None:
            raise ValueError("tokenizer is required")
        skip_prompt=kwargs.pop('skip_prompt', False)
        skip_prompt_tokens=kwargs.pop('skip_prompt_tokens', False)

        streamer=TextIteratorStreamer(
            tokenizer=tokenizer,
            skip_prompt=skip_prompt,
            skip_prompt_tokens=skip_prompt_tokens
            )
        logger.info("TextIteratorStreamer created")

        return streamer

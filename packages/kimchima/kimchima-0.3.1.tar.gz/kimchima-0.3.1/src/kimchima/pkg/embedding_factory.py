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

import torch
import torch.nn.functional as F
from kimchima.pkg import logging


logger = logging.get_logger(__name__)


class EmbeddingsFactory:
    r"""

    Embeddings class to get embeddings from the specified model and tokenizer.
    The embeddings mean pooling is used to get the embeddings from the model,
    and the embeddings are normalized using L2 normalization.

    Args:
        pretrained_model_name_or_path: pretrained model name or path

    Returns:
        sentence_embeddings: sentence embeddings type torch.Tensor

    """

    def __init__(self):
        raise EnvironmentError(
            "Embeddings is designed to be instantiated "
            "using the `Embeddings.from_pretrained(pretrained_model_name_or_path)` method."
        )


    @classmethod
    def get_text_embeddings(cls, *args, **kwargs)-> torch.Tensor:
        r"""
        Get embeddings from the model.

        Args:
            prompt: prompt text
            device: device to run the model
            max_length: maximum length of the input text
        """
        model=kwargs.pop('model', None)
        tokenizer=kwargs.pop('tokenizer', None)
        prompt = kwargs.pop('prompt', None)
        device = kwargs.pop('device', 'cpu')
        max_length = kwargs.pop('max_length', 512)


        inputs_ids = tokenizer(prompt, return_tensors='pt',max_length=max_length, padding=True, truncation=True).to(device)

        model=model.to(device)
        with torch.no_grad():
            output = model(**inputs_ids)

        embeddings=cls.mean_pooling(model_output=output, attention_mask=inputs_ids['attention_mask'])
        logger.debug(f"Embedding mean pooling: {embeddings.shape}")

        # Normalize embeddings
        sentence_embeddings = F.normalize(embeddings, p=2, dim=1)

        return sentence_embeddings


    @classmethod
    #Mean Pooling - Take attention mask into account for correct averaging
    def mean_pooling(cls, **kwargs) -> torch.Tensor:
        r"""
        Mean Pooling - Take attention mask into account for correct averaging.

        Args:
            model_output: model output
            attention_mask: attention mask
        """
        model_output = kwargs.get('model_output')
        attention_mask = kwargs.get('attention_mask')
        token_embeddings = model_output[0] #First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

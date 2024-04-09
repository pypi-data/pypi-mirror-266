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

from huggingface_hub import hf_hub_download, snapshot_download

from kimchima.pkg import logging

logger = logging.get_logger(__name__)


class DownloadHub:
    r"""
    DownloadFactory is a class that provides methods to download files or repositories from Hugging Face Hub.
    """

    def __init__(self):
        raise EnvironmentError(
            "DownloadFactory is designed to be instantiated "
            "using the `DownloadFactory.from_pretrained(pretrained_model_name_or_path)` method."
        )
    
    @classmethod
    def download_specific_file(cls, *args, **kwargs)-> str:
        r"""
        Download a specific file from a repository through hf_hub_download.
        """

        repo_id=kwargs.pop("repo_id", None)
        if repo_id is None:
            raise ValueError("repo_id cannot be None")
        filename=kwargs.pop("filename", None)
        if filename is None:
            raise ValueError("filename cannot be None")
        # revison supports a specific commit SHA
        revision=kwargs.pop("revision", 'main')
        folder_name=kwargs.pop("folder_name", None)
        if folder_name is None:
            raise ValueError("folder_name cannot be None")
        
        logger.debug(f"Downloading {filename} from {repo_id} at revision {revision} to {folder_name}")

        folder_path=hf_hub_download(
            repo_id=repo_id, 
            filename=filename, 
            revision=revision,
            cache_dir=folder_name,
            local_dir=folder_name
            )
        
        logger.debug(f"Downloaded {filename} from {repo_id} at revision {revision} to {folder_name}")
        
        return folder_path
    
    @classmethod
    def download_repo(cls, *args, **kwargs)-> str:
        r"""
        Download the entire repository to a folder through snapshot_download.

        """

        repo_id=kwargs.pop("repo_id", None)
        if repo_id is None:
            raise ValueError("repo_id cannot be None")
        # revison supports a specific commit SHA
        revision=kwargs.pop("revision", 'main')
        folder_name=kwargs.pop("folder_name", None)
        if folder_name is None:
            raise ValueError("folder_name cannot be None")

        logger.debug(f"Downloading {repo_id} at revision {revision} to {folder_name}")

        folder_path=snapshot_download(
            repo_id=repo_id, 
            revision=revision,
            cache_dir=folder_name,
            local_dir=folder_name
            )
        
        logger.debug(f"Downloaded {repo_id} at revision {revision} to {folder_name}")

        return folder_path

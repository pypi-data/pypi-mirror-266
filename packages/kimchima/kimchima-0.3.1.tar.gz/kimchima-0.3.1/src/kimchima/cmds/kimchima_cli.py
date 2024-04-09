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

import argparse

from kimchima.cmds.auto_cli import CommandAutoModel


def main():
    """
    Main function for kimchima.
    """
    parser = argparse.ArgumentParser(
        prog="kimchima",
        description="A command line tool for natural language processing."
    )
    subparsers = parser.add_subparsers(help="sub-command help")


    parser_auto=subparsers.add_parser("auto", help="auto help")
    parser_auto.add_argument("model_name_or_path", default="sentence-transformers/all-MiniLM-L6-v2", help="model name or path")
    parser_auto.add_argument("text", help="text str or list of text str")
    parser_auto.set_defaults(func=CommandAutoModel.auto)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
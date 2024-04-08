##
#   Copyright 2021 Alibaba, Inc. and its affiliates. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
##

# -*- coding: utf-8 -*-

from dashtext.tokenizer._base import BaseTokenizer

class TextTokenizer:
    @classmethod
    def from_pretrained(cls,
                        pretrained_model_name_or_path: str,
                        *inputs, **kwargs) -> BaseTokenizer:
        if pretrained_model_name_or_path == "Jieba" or pretrained_model_name_or_path == "JiebaTokenizer":
            from dashtext.tokenizer._jieba import JiebaTokenizer
            return JiebaTokenizer(*inputs, **kwargs)

        raise ModuleNotFoundError(f"input pretrained_model_name_or_path({pretrained_model_name_or_path}) not found")


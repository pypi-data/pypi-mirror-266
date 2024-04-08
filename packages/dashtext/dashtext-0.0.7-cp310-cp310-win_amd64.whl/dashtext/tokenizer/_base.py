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

from abc import abstractmethod
from typing import Union, List, Dict, Set, Any

from dashtext.tokenizer._stopwords import StopWords


class BaseTokenizer(object):
    def __init__(self, *,
                 stop_words: Union[bool, Dict[str, Any], List[str], Set[str]] = None):
        self._stop_words = None if stop_words is None else StopWords(
            vocab=stop_words)

    @abstractmethod
    def tokenize(self, sentence: str) -> List[str]:
        pass

    @abstractmethod
    def encode(self, sentence: str) -> List[int]:
        pass

    @abstractmethod
    def decode(self, tokens: List[int]) -> str:
        pass

    @classmethod
    def hash(cls, text: Union[str, int]) -> int:
        if isinstance(text, int):
            return text

        if not isinstance(text, str):
            raise TypeError(f"input text({text}) must be a str or int")

        import mmh3
        return mmh3.hash(text, signed=False)

    @classmethod
    def hash_to_bucket(cls, hash_value: int, hash_bucket_num: int = None) -> int:
        if not isinstance(hash_value, int):
            raise TypeError(f"input hash_value({hash_value}) must be a integer")

        if hash_bucket_num is None:
            return hash_value
        elif not isinstance(hash_bucket_num, int):
            raise TypeError(f"input hash_bucket_num({hash_bucket_num}) must be a integer")
        elif hash_bucket_num <= 0:
            raise TypeError(f"input hash_bucket_num({hash_bucket_num}) must be greater than 0")

        return hash_value % hash_bucket_num

    def _is_stop_word(self, word: str) -> bool:
        if self._stop_words is None:
            return False

        return self._stop_words.check(word)


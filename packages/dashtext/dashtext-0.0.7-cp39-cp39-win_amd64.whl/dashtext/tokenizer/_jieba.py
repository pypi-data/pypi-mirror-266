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

import os
from typing import Any, Union, Dict, List, Set

from dashtext.tokenizer._base import BaseTokenizer
import dashtext.pydashtext as pydashtext

class JiebaTokenizer(BaseTokenizer):
    def __init__(self, *,
                 dict: str = "data/jieba/dict.txt.big",
                 user_dict: str = "data/jieba/user_dict.txt",
                 stop_words: Union[bool, Dict[str, Any], List[str], Set[str]] = None):
        """

        Args:
            dict (str, optional): dict path. Defaults to https://raw.githubusercontent.com/fxsjy/jieba/master/extra_dict/dict.txt.big.
            user_dict (str, optional): extra user dict path. Defaults to "data/jieba/user_dict.txt"(empty file).
            stop_words (Union[bool, Dict, List, Set], optional): set stop words of tokenizer. Defaults to None.
                True/False: 'True' means using pre-defined stopwords, 'False' means not using any stopwords
                Dict/List/Set: user defined stopwords. Type [Dict]/[List] will transfer to [Set]
        """

        super().__init__(stop_words=stop_words)
        
        # dict path
        self._dict_path = dict
        if isinstance(dict, str) and not os.path.isfile(dict):
            self._dict_path = os.path.dirname(os.path.realpath(__file__)) + "/" + dict
        
        # user dict path
        self._user_dict_path = user_dict
        if isinstance(user_dict, str) and not os.path.isfile(user_dict):
            self._user_dict_path = os.path.dirname(os.path.realpath(__file__)) + "/" + user_dict

        hmm_path = os.path.dirname(os.path.realpath(__file__)) + "/data/jieba/hmm_model.txt"
        idf_path = os.path.dirname(os.path.realpath(__file__)) + "/data/jieba/idf.txt.big"
        stop_word_path = os.path.dirname(os.path.realpath(__file__)) + "/data/jieba/stop_words.txt"

        self._tokenizer = pydashtext.Jieba(dict_path=self._dict_path,
                                           hmm_path=hmm_path,
                                           user_dict_path=self._user_dict_path,
                                           idf_path=idf_path,
                                           stop_word_path=stop_word_path)

    def tokenize(self, sentence: str) -> List[str]:
        if not isinstance(sentence, str):
            raise TypeError(f"input sentence({sentence}) must be str")

        if len(sentence) <= 0:
            return []

        words = []
        for word in self._tokenizer.cut(sentence):
            if word == ' ' or word == ' ':
                continue
            if self._is_stop_word(word):
                continue
            words.append(word)
        return words

    def encode(self, sentence: str) -> List[int]:
        if not isinstance(sentence, str):
            raise TypeError(f"input sentence({sentence}) must be str")

        if len(sentence) <= 0:
            return []

        tokens = []
        for word in self.cut(sentence):
            tokens.append(BaseTokenizer.hash(word))
        return tokens

    def decode(self, tokens: List[int]) -> str:
        raise NotImplementedError("decode method is not implemented")

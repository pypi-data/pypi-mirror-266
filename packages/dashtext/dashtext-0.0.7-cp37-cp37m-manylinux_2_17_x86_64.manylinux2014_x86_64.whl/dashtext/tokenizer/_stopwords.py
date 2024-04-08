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
from typing import Union, Dict, List, Set, Any


class StopWords(object):
    def __init__(self, *,
                 vocab: Union[bool, Dict[str, Any], List[str], Set[str]] = None):

        self._set = set([])
        if isinstance(vocab, bool) and vocab is True:
            with open(file=os.path.dirname(os.path.realpath(__file__)) + "/data/stopwords.txt", mode="r", encoding="utf-8") as f:
                for line in f:
                    self._set.add(line.rstrip())
        elif isinstance(vocab, str):
            if not os.path.isfile(vocab):
                vocab = os.path.dirname(os.path.realpath(__file__)) + vocab
            with open(file=vocab, mode="r") as f:
                for line in f:
                    self._set.add(line.rstrip())
        elif isinstance(vocab, (dict, list)):
            self._set = set(vocab)
        elif isinstance(vocab, set):
            self._set = vocab
        else:
            self._set = None

    def check(self, word: str) -> bool:
        if self._set is None:
            return False

        return self._set.__contains__(word)

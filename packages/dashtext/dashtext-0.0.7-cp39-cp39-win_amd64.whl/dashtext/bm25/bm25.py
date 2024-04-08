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
from typing import Union, List, Dict


class BM25:
    def __init__(self,
                 b: float = 0.75,
                 k1: float = 1.2):
        import dashtext.pydashtext as pydashtext
        self.bm25 = pydashtext.BM25(b, k1)
        
    @property
    def b(self) -> float:
        return self.bm25.b()
    
    @b.setter
    def b(self, b:float) -> None:
        self.bm25.b(b)
        
    @property
    def k1(self) -> float:
        return self.bm25.k1()
    
    @k1.setter
    def k1(self, k1: float) -> None:
        self.bm25.k1(k1)


    def train(self, corpus: Union[List[str], List[int]]) -> None:
        if not corpus:
            return

        if isinstance(corpus, list):
            if isinstance(corpus[0], int) or isinstance(corpus[0], str):
                self.bm25.train(corpus)
            else:
                raise TypeError("input corpus must be List[str] or List[int]")
        else:
            raise TypeError("input corpus must be List[str] or List[int]")

    def load(self, json_data: str) -> None:
        if not isinstance(json_data, str):
            raise TypeError("input json data must be str")

        if len(json_data) <= 0:
            raise ValueError("input json data should not be empty")

        try:
            self.bm25.load(json_data)
        except Exception as e:
            raise RuntimeError("json data load error: " + str(e))

    def dump(self, path: str) -> None:
        if not isinstance(path, str):
            raise TypeError("input path must be str")

        if len(path) <= 0:
            raise ValueError("input path should not be empty")

        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        except Exception as e:
            raise OSError("create dump path error: " + str(e))

        try:
            self.bm25.dump(path)
        except Exception as e:
            raise RuntimeError("dump error: " + str(e))

    def encode_documents(self, texts: Union[List[str], List[int]]) -> Dict:
        if not texts:
            return {}

        if isinstance(texts, list):
            if isinstance(texts[0], int) or isinstance(texts[0], str):
                return self.bm25.encode_document(texts)
            else:
                raise TypeError("input texts must be List[str] or List[int]")
        else:
            raise TypeError("input texts must be List[str] or List[int]")

    def encode_queries(self, texts: Union[List[int], List[str]]) -> Dict:
        if not texts:
            return {}

        if isinstance(texts, list):
            if isinstance(texts[0], int) or isinstance(texts[0], str):
                return self.bm25.encode_query(texts)
            else:
                raise TypeError("input texts must be List[str] or List[int]")
        else:
            raise TypeError("input texts must be List[str] or List[int]")

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
import socket
import urllib
import urllib.request
from typing import Union, List, Dict, Callable
from urllib.error import URLError

from dashtext.bm25.bm25 import BM25
from dashtext.tokenizer.auto import TextTokenizer
from dashtext.tokenizer._base import BaseTokenizer


class SparseVectorEncoder:
    """
        SparseVectorEncoder is implementation of a OKAPI BM25 implementation and a Tokenizer/Hash interface.
    """

    def __init__(self, *,
                 b: float = 0.75,
                 k1: float = 1.2,
                 tokenize_function: Callable[[str], List[str]] = TextTokenizer.from_pretrained("Jieba", stop_words=True).tokenize,
                 hash_function: Callable[[Union[str, int]], int] = BaseTokenizer.hash,
                 hash_bucket_function: Callable[[int], int] = None):
        """
        Args:
            b (float): default = 0.75.
                Controls the effect of document length on the calculation of the score. a larger b parameter indicates that the document length has a greater effect on the score, and vice versa.
            k1 (float): default = 1.2.
                Controls the effect of query item frequency on the computed score. a larger k1 parameter indicates a larger effect of query item frequency on the score and vice versa.
            tokenize_function: default = jieba tokenizer.
                Support for user-defined incoming tokenize method, see the example for specific usage. [optional]
            hash_function: default = mmh3 hash.
                Support for user-defined method of passing hash, the specific use of the method see example. [optional]
            hash_bucket_function: default = None.
                If you want to use the hash bucket function of indices, you have to specify hash_bucket_function. [optional]

        Return:
            SparseVectorEncoder.
        """

        if not isinstance(b, float):
            raise TypeError("input b must be float")

        if not isinstance(k1, float):
            raise TypeError("input k1 must be float")

        if tokenize_function is not None and not hasattr(tokenize_function, '__call__'):
            raise TypeError("input tokenize_function must be a function")

        if hash_function is not None and not hasattr(hash_function, '__call__'):
            raise TypeError("input hash_function must be a function")

        if hash_bucket_function is not None and not hasattr(hash_bucket_function, '__call__'):
            raise TypeError("input hash_bucket_function must be a function")

        self._b = b
        self._k1 = k1
        self._encoder = BM25(b, k1)
        self._tokenize_function = tokenize_function
        self._hash_function = hash_function
        self._hash_bucket_function = hash_bucket_function

    @property
    def b(self) -> float:
        return self._b
    
    @b.setter
    def b(self, b:float) -> None:
        self._b = b
        self._encoder.b = b
        
    @property
    def k1(self) -> float:
        return self._k1
    
    @k1.setter
    def k1(self, k1: float) -> None:
        self._k1 = k1
        self._encoder.k1 = k1
    
    def train(self, corpus: Union[str, List[str], List[int], List[List[int]]]) -> None:
        """
        train a OKAPI BM25 Model.

        Args:
            corpus (Union[str, List[str], List[int], List[List[int]]])): a single or list of documents.

        Return:
            None.
        """

        if not corpus:
            return

        if isinstance(corpus, str):
            return self._train_corpus(corpus)

        if isinstance(corpus, list):
            if all(isinstance(text, (str, list)) for text in corpus):
                [self._train_corpus(text) for text in corpus]
                return

            if all(isinstance(text, int) for text in corpus):
                return self._train_corpus(corpus)

        raise TypeError(
            "input corpus must be str, List[str], List[int], List[List[int]]")

    def load(self, path: str) -> None:
        """
        load a OKAPI BM25 Model.

        Args:
            path: (str): load model path(file or URL).

        Return:
            None.
        """

        if not isinstance(path, str):
            raise TypeError("input path must be str")

        if len(path) <= 0:
            raise ValueError("input path should not be empty")

        load_data: str = ""
        is_http: bool = path.startswith('http://')
        if not is_http:
            if path.startswith('https://'):
                import ssl
                ssl._create_default_https_context = ssl._create_unverified_context
                is_http = True

        if is_http:
            max_retries = 3
            for i in range(max_retries):
                try:
                    response = urllib.request.urlopen(path, timeout=60)
                    load_data = response.read().decode('utf-8')
                    break
                except URLError as e:
                    if isinstance(e.reason, socket.timeout):
                        if i == max_retries - 1:
                            raise RuntimeError(f"load url({path}) timeout")
                    else:
                        raise RuntimeError(
                            f"load url({path}) failed, error:{e}")
                except Exception as e:
                    raise RuntimeError(f"load url({path}) failed, error:{e}")
        else:
            try:
                with open(path, 'r') as file:
                    load_data = file.read()
            except Exception as e:
                raise RuntimeError(f"load file({path}) failed, error:{e}")

        if len(load_data) <= 0:
            raise RuntimeError(f"load data({path}) should not be empty")

        self._encoder.load(load_data)

    def dump(self, path: str) -> None:
        """
        dump a OKAPI BM25 Model.

        Args:
            path:(str): dump model path.

        Return:
            None.
        """

        if not isinstance(path, str):
            raise TypeError("input path must be str")

        if not path:
            raise ValueError("input path should not be empty")

        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        except OSError as error:
            raise RuntimeError(f"create directory error: {error}")
        self._encoder.dump(path)

    @staticmethod
    def default(name: str = 'zh') -> "SparseVectorEncoder":
        """
        get a SparseVectorEncoder with default OKAPI BM25 Model.

        Args:
            name:(str): model name.

        Return:
            SparseVectorEncoder with default OKAPI BM25 Model.
        """

        if name == 'zh':
            url = "http://dashvector-data.oss-cn-beijing.aliyuncs.com/public/sparsevector/bm25_zh_default.json"
        elif name == 'en':
            url = "http://dashvector-data.oss-cn-beijing.aliyuncs.com/public/sparsevector/bm25_en_default.json"
        else:
            raise ValueError("input name be 'zh' or 'en'")

        encoder = SparseVectorEncoder()
        try:
            encoder.load(url)
        except Exception as e:
            raise RuntimeError(f"load error: {e}")
        return encoder

    def encode_documents(self, texts: Union[str, List[str], List[int], List[List[int]]]) -> Union[Dict, List[Dict]]:
        """
        encode documents to a sparse vector.

        Args:
            texts (Union[str, List[str], List[int], List[List[int]]])): a single or list of documents to encode as a string.

        Return:
            one or more document sparse vectors.
        """

        if not texts:
            raise ValueError("input texts should not be empty")

        if isinstance(texts, str):
            return self._encode_documents(texts)

        if isinstance(texts, list):
            if all(isinstance(text, (str, list)) for text in texts):
                return [self._encode_documents(text) for text in texts]
            if all(isinstance(text, int) for text in texts):
                return self._encode_documents(texts)

        raise TypeError(
            "input texts must be str, List[str], List[int], List[List[int]]")

    def encode_queries(self, texts: Union[str, List[str], List[int], List[List[int]]]) -> Union[Dict, List[Dict]]:
        """
        encode queries to a sparse vector.

        Args:
            texts (Union[str, List[str], List[int], List[List[int]]])): a single or list of queries to encode as a string.

        Return:
            one or more query sparse vectors.
        """

        if not texts:
            raise ValueError("input texts should not be empty")

        if isinstance(texts, str):
            return self._encode_queries(texts)

        if isinstance(texts, list):
            if all(isinstance(text, (str, list)) for text in texts):
                return [self._encode_queries(text) for text in texts]
            if all(isinstance(text, int) for text in texts):
                return self._encode_queries(texts)

        raise TypeError(
            "input texts must be str, List[str], List[int], List[List[int]]")

    def _text_to_tokens(self, text: Union[str, List[int]]) -> Union[List[str], List[int]]:
        if len(text) <= 0:
            return []

        tokens = []
        if isinstance(text, str):
            for word in self._tokenize_function(text):
                if self._hash_function is not None:
                    word = self._hash_function(word)
                if self._hash_bucket_function is not None:
                    word = self._hash_bucket_function(word)
                tokens.append(word)
        elif isinstance(text, list) and all(isinstance(word, int) for word in text):
            if self._hash_bucket_function is not None:
                for word in text:
                    tokens.append(self._hash_bucket_function(word))
            else:
                tokens = text
        else:
            raise TypeError("input text must be str, List[int]")

        return tokens

    def _train_corpus(self, text: Union[str, List[int]]) -> None:
        tokens = self._text_to_tokens(text)
        if len(tokens) <= 0:
            return
        self._encoder.train(tokens)

    def _encode_documents(self, text: Union[str, List[int]]) -> Dict:
        return self._encoder.encode_documents(self._text_to_tokens(text))

    def _encode_queries(self, text: Union[str, List[int]]) -> Dict:
        return self._encoder.encode_queries(self._text_to_tokens(text))

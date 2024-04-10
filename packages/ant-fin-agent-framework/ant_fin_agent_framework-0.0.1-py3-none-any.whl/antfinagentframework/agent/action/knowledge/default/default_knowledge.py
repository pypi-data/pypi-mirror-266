# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/26 11:05
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: default_knowledge.py

from antfinagentframework.agent.action.knowledge.embedding.openai_embedding import OpenAIEmbedding
from antfinagentframework.agent.action.knowledge.knowledge import Knowledge
from antfinagentframework.agent.action.knowledge.reader.file.file_reader import FileReader
from antfinagentframework.agent.action.knowledge.store.chroma_store import ChromaStore


class DefaultKnowledge(Knowledge):
    """The finCo default knowledge module."""

    def __init__(self, **kwargs):
        """The __init__ method.

        Some parameters, such as name and description,
        are injected into this class by the default_knowledge.yaml configuration.


        Args:
            name (str): Name of the knowledge.

            description (str): Description of the knowledge.

            store (Store): Store of the knowledge, store class is used to store knowledge
            and provide retrieval capabilities, such as ChromaDB store or Redis Store,
            default knowledge uses ChromaDB as the knowledge storage.

            reader (Reader): Reader is used to load data,
            the default knowledge uses FileReader to load data from files.
        """
        super().__init__(**kwargs)
        self.store = ChromaStore(collection_name="chroma_store", embedding_model=OpenAIEmbedding(
            embedding_model_name='text-embedding-ada-002'))
        self.reader = FileReader()

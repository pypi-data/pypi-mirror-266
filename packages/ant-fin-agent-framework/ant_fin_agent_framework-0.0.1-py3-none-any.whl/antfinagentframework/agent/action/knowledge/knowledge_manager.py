# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/18 11:24
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: knowledge_manager.py
from antfinagentframework.base.annotation.singleton import singleton
from antfinagentframework.base.component.component_enum import ComponentEnum
from antfinagentframework.base.component.component_manager_base import ComponentManagerBase


@singleton
class KnowledgeManager(ComponentManagerBase):
    """The KnowledgeManager class, which is used to manage the knowledge."""

    def __init__(self):
        """Initialize the KnowledgeManager."""
        super().__init__(ComponentEnum.KNOWLEDGE)

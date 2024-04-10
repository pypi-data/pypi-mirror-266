# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/13 14:00
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: component_configer_util.py
import importlib
from typing import Type, Callable

from antfinagentframework.agent.action.knowledge.knowledge_manager import KnowledgeManager
from antfinagentframework.agent.action.tool.tool_manager import ToolManager
from antfinagentframework.agent.agent_manager import AgentManager
from antfinagentframework.agent.memory.memory_manager import MemoryManager
from antfinagentframework.agent.plan.planner.planner_manager import PlannerManager
from antfinagentframework.agent_serve.service_manager import ServiceManager
from antfinagentframework.agent_serve.service_configer import ServiceConfiger
from antfinagentframework.base.config.component_configer.component_configer import ComponentConfiger
from antfinagentframework.base.config.component_configer.configers.agent_configer import AgentConfiger
from antfinagentframework.base.config.component_configer.configers.knowledge_configer import KnowledgeConfiger
from antfinagentframework.base.config.component_configer.configers.memory_configer import MemoryConfiger
from antfinagentframework.base.config.component_configer.configers.planner_configer import PlannerConfiger
from antfinagentframework.base.config.component_configer.configers.tool_configer import ToolConfiger
from antfinagentframework.base.config.config_type_enum import ConfigTypeEnum
from antfinagentframework.base.config.component_configer.configers.llm_configer import LLMConfiger
from antfinagentframework.base.component.component_enum import ComponentEnum
from antfinagentframework.llm.llm_manager import LLMManager


class ComponentConfigerUtil(object):
    """The ComponentConfigerUtil class, which is used to load and manage the component configuration."""

    __COMPONENT_CONFIGER_CLZ_MAP = {
        ComponentEnum.AGENT: AgentConfiger,
        ComponentEnum.KNOWLEDGE: KnowledgeConfiger,
        ComponentEnum.LLM: LLMConfiger,
        ComponentEnum.PLANNER: PlannerConfiger,
        ComponentEnum.TOOL: ToolConfiger,
        ComponentEnum.MEMORY: MemoryConfiger,
        ComponentEnum.SERVICE: ServiceConfiger,
        ComponentEnum.DEFAULT: ComponentConfiger
    }

    __COMPONENT_MANAGER_CLZ_MAP = {
        ComponentEnum.AGENT: AgentManager,
        ComponentEnum.KNOWLEDGE: KnowledgeManager,
        ComponentEnum.LLM: LLMManager,
        ComponentEnum.PLANNER: PlannerManager,
        ComponentEnum.TOOL: ToolManager,
        ComponentEnum.MEMORY: MemoryManager,
        ComponentEnum.SERVICE: ServiceManager
    }

    @classmethod
    def get_component_config_clz_by_type(cls, component_type_enum: ComponentEnum) -> \
            Type[ComponentConfiger | LLMConfiger]:
        """Get the ComponentConfiger object by the component type.
        Args:
            component_type_enum(ConfigTypeEnum): the component type
        Returns:
            ComponentConfiger: the sub object of ComponentConfiger
        """
        component_config_clz = cls.__COMPONENT_CONFIGER_CLZ_MAP.get(component_type_enum)
        if component_config_clz is None:
            raise Exception(f"Failed to get the ComponentConfiger class by the component type: {component_type_enum}")
        return component_config_clz

    @classmethod
    def get_component_object_clz_by_component_configer(cls, component_configer: ComponentConfiger) -> Callable:
        """Get the component object by the ComponentConfiger object.
        Args:
            component_configer(ComponentConfiger): the ComponentConfiger object
        Returns:
            object: the component object
        """
        module = importlib.import_module(component_configer.metadata_module)
        clz = getattr(module, component_configer.metadata_class)
        return clz

    @classmethod
    def get_component_manager_clz_by_type(cls, component_type_enum: ComponentEnum) -> Callable:
        """Get the ComponentManager object by the component type.
        Args:
            component_type_enum(ConfigTypeEnum): the component type
        Returns:
            object: the ComponentManager object
        """
        return cls.__COMPONENT_MANAGER_CLZ_MAP.get(component_type_enum)

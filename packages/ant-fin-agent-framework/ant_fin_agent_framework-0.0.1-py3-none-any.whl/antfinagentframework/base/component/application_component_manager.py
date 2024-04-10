# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/14 12:08
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: component_manager.py
from antfinagentframework.agent.action.knowledge.knowledge_manager import KnowledgeManager
from antfinagentframework.agent.action.tool.tool_manager import ToolManager
from antfinagentframework.agent.plan.planner.planner_manager import PlannerManager
from antfinagentframework.agent.agent_manager import AgentManager
from antfinagentframework.base.annotation.singleton import singleton
from antfinagentframework.llm.llm_manager import LLMManager


@singleton
class ApplicationComponentManager(object):
    """The ComponentManager class, which is used to manage the components."""

    def __init__(self):
        """Initialize the ComponentManager."""
        self.__agent_manager: AgentManager = AgentManager()
        self.__llm_manager: LLMManager = LLMManager()
        self.__planner_manager: PlannerManager = PlannerManager()
        self.__knowledge: KnowledgeManager = KnowledgeManager()
        self.__tool_manager: ToolManager = ToolManager()

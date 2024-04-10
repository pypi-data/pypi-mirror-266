# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/21 18:12
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: default_tool.py


from antfinagentframework.agent.action.tool.tool import Tool, ToolInput


class DefaultTool(Tool):
    """The finCo default tool module.

    Tool parameters, such as name/description/tool_type/input_keys,
    are injected into this class by the default_tool.yaml configuration.
    """

    def execute(self, tool_input: ToolInput):
        """Demonstrates the execute method of the Tool class."""

        return "The specific execution results of the tool"

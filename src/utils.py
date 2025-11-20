import inspect
import re
from typing import NamedTuple, Callable, Optional


class ToolInfo(NamedTuple):
    """Information about a tool extracted from a function."""
    name: str
    params: str
    docstring: str


class ParsedResponse(NamedTuple):
    """Parsed response from the LLM."""
    answer: Optional[str]
    tool: Optional[str]
    params: Optional[str]


def function_to_tool(func: Callable) -> ToolInfo:
    """Convert a Python function to a ToolInfo namedtuple.

    Extracts the function name, parameters signature, and docstring
    to create a structured representation for the LLM.

    Args:
        func: The function to convert to a tool

    Returns:
        ToolInfo with name, params, and docstring
    """
    name = func.__name__
    sig = inspect.signature(func)
    params = ", ".join([
        f"{param_name}: {param.annotation.__name__ if param.annotation != inspect.Parameter.empty else 'any'}"
        for param_name, param in sig.parameters.items()
    ])
    docstring = inspect.getdoc(func) or "No description available"

    return ToolInfo(name=name, params=params, docstring=docstring)


def add_tools_to_prompt(system_prompt: str, tool_infos: list[ToolInfo]) -> str:
    """Add tool descriptions to the system prompt.

    Takes a list of ToolInfo namedtuples and serializes them into
    a formatted string appended to the system prompt.

    Args:
        system_prompt: The base system prompt
        tool_infos: List of ToolInfo namedtuples

    Returns:
        The full system prompt with tool descriptions
    """
    if not tool_infos:
        return system_prompt

    tools_description = "\n\nAvailable Tools:\n"
    for tool_info in tool_infos:
        tools_description += f"- {tool_info.name}({tool_info.params}): {tool_info.docstring}\n"

    return system_prompt + tools_description


def parse_response(response_text: str) -> ParsedResponse:
    """Parse the LLM response for answer or tool call.

    Extracts either:
    - A final answer between <answer></answer> tags
    - A tool call with <tool></tool> and <parameters></parameters> tags

    Args:
        response_text: The raw response from the LLM

    Returns:
        ParsedResponse with answer, tool, and params (all optional)
    """
    answer = None
    tool = None
    params = None

    # Check for answer
    answer_match = re.search(r'<answer>(.*?)</answer>', response_text, re.DOTALL)
    if answer_match:
        answer = answer_match.group(1).strip()

    # Check for tool call
    tool_match = re.search(r'<tool>(.*?)</tool>', response_text)
    if tool_match:
        tool = tool_match.group(1).strip()

        # Check for parameters
        params_match = re.search(r'<parameters>(.*?)</parameters>', response_text)
        if params_match:
            params = params_match.group(1).strip()

    return ParsedResponse(answer=answer, tool=tool, params=params)

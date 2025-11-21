"""
Text to Tool to Text - Two-Step Process

This script demonstrates a structured two-step interaction:
1. User asks question → LLM returns tool call
2. Execute tool → LLM uses result to provide final answer

This is more structured than a loop but shows the core pattern:
Text (user) → Tool (agent decision) → Text (final answer)

No while loops, just explicit steps showing the tool calling pattern.
"""

import litellm
from utils import function_to_tool, add_tools_to_prompt, parse_response
from prompts import SYSTEM_PROMPT
from tools import get_weather


def run_two_step_agent(
    system_prompt: str,
    user_request: str,
    tools: dict,
    model: str
) -> str:
    """
    Run a two-step agent: query → tool → final answer.

    Step 1: Ask LLM, expect a tool call
    Step 2: Execute tool, ask LLM again for final answer

    Args:
        system_prompt: The system prompt defining agent behavior
        user_request: The user's question
        tools: Dictionary of available tool functions
        model: The model identifier

    Returns:
        The final answer from the LLM
    """
    # Convert tools to ToolInfo namedtuples
    tool_infos = [function_to_tool(tool_func) for tool_func in tools.values()]

    # Build full system prompt with tools
    full_system_prompt = add_tools_to_prompt(system_prompt, tool_infos)

    # Step 1: Initial query - expect tool call
    print("\n=== Step 1: Initial LLM Query ===")
    messages = [
        {"role": "system", "content": full_system_prompt},
        {"role": "user", "content": user_request}
    ]

    response = litellm.completion(model=model, messages=messages)
    assistant_message = response.choices[0].message.content
    print(f"LLM Response: {assistant_message}")

    # Parse the response
    parsed = parse_response(assistant_message)
    
    # Make sure we have a tool call
    assert parsed.tool is not None and parsed.answer is None, "Expected a tool call in the first step."

    # Step 2: Execute tool
    print("\n=== Step 2: Execute Tool ===")
    tool_name = parsed.tool
    params_str = parsed.params or ""    
    assert tool_name in tools, f"Tool '{tool_name}' not found. Available: {', '.join(tools.keys())}"

    # Parse parameters and execute tool
    params = [p.strip() for p in params_str.split(',')] if params_str else []
    tool_result = tools[tool_name](*params)
    print(f"Tool '{tool_name}' returned: {tool_result}")

    # Step 3: Query LLM with tool result for final answer
    print("\n=== Step 3: Final LLM Query with Tool Result ===")
    messages.append({"role": "assistant", "content": assistant_message})
    messages.append({"role": "user", "content": f"Tool '{tool_name}' returned: {tool_result}"})

    response = litellm.completion(model=model, messages=messages)
    assistant_message = response.choices[0].message.content
    print(f"LLM Response: {assistant_message}")

    # Parse final answer
    parsed_final = parse_response(assistant_message)
    assert parsed_final.answer is not None, "Expected a final answer in the last step."

    return parsed_final.answer


if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Two-step tool calling example for travel recommendations")
    parser.add_argument(
        "-q", "--question",
        type=str,
        default="what activity do you suggest to book if I travel to honolulu next week?",
        help="User question for the travel agent"
    )
    args = parser.parse_args()

    # Define available tools
    tools = {
        "get_weather": get_weather
    }

    # Run the two-step agent
    print(f"\n=== Question: {args.question} ===")

    result = run_two_step_agent(
        system_prompt=SYSTEM_PROMPT,
        user_request=args.question,
        tools=tools,
        model="claude-sonnet-4-5-20250929"
    )

    print("\n=== Final Answer ===")
    print(result)
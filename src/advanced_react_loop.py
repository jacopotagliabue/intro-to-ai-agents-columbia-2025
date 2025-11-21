"""
Advanced ReAct Loop - Pedagogical Example

This script extends the simple ReAct loop to demonstrate more sophisticated agent
behavior with multiple tools and structured reasoning.

Key enhancements over simple_react_loop.py:
1. Multiple tools: weather checking AND availability checking
2. Required reasoning: Agent must always express its thought process in <reasoning> tags
3. Multi-step decision making: Consider both weather and availability before recommending

The agent iteratively:
1. Expresses reasoning about what it needs (REQUIRED in every response)
2. Calls tools to gather weather and availability information
3. Uses the results to make informed recommendations
4. Provides a final answer considering all constraints

This demonstrates how the same ReAct pattern naturally extends to more complex scenarios.
"""

from utils import function_to_tool, add_tools_to_prompt, parse_response
from prompts import ADVANCED_SYSTEM_PROMPT
from tools import get_weather, check_availability_activity
import litellm


def run_agent(
    system_prompt: str,
    user_request: str,
    tools: dict,
    model: str,
    max_iterations: int = 10
):
    # Convert tools to ToolInfo namedtuples
    tool_infos = [function_to_tool(tool_func) for tool_func in tools.values()]

    # Build full system prompt with tools
    full_system_prompt = add_tools_to_prompt(system_prompt, tool_infos)

    # Initialize conversation context
    messages = [
        {"role": "system", "content": full_system_prompt},
        {"role": "user", "content": user_request}
    ]

    # Main agent loop
    for iteration in range(max_iterations):
        # Call LLM
        response = litellm.completion(model=model, messages=messages)
        assistant_message = response.choices[0].message.content

        print(f"\n--- Iteration {iteration + 1} ---")
        print(f"Agent: {assistant_message}")

        # Add assistant response to messages
        messages.append({"role": "assistant", "content": assistant_message})

        # Parse response using utility function
        parsed = parse_response(assistant_message)

        # Display reasoning if present
        if parsed.reasoning:
            print(f"\nReasoning: {parsed.reasoning}")

        # Check if we have a final answer - if so we return early
        if parsed.answer:
            print(f"\nFinal Answer: {parsed.answer}")
            return parsed.answer

        # Check if we have a tool call
        if parsed.tool:
            tool_name = parsed.tool
            params_str = parsed.params or ""

            # Check if tool exists
            if tool_name in tools:
                # Parse parameters (simple comma-separated for now)
                params = [p.strip() for p in params_str.split(',')] if params_str else []
                # Execute tool
                try:
                    tool_result = tools[tool_name](*params)
                    print(f"Tool Result: {tool_result}")
                    # Add tool result to messages
                    messages.append({"role": "user", "content": f"Tool '{tool_name}' returned: {tool_result}"})
                except Exception as e:
                    error_msg = f"Error executing tool '{tool_name}': {str(e)}"
                    print(error_msg)
                    messages.append({"role": "user", "content": error_msg})
            else:
                error_msg = f"Tool '{tool_name}' not found. Available tools: {', '.join(tools.keys())}"
                print(error_msg)
                messages.append({"role": "user", "content": error_msg})
        else:
            # No tool call found, but also no answer
            # Check if reasoning was provided
            if not parsed.reasoning:
                messages.append({"role": "user", "content": "Please provide your reasoning in <reasoning> tags, and either an <answer> or a <tool> call."})
            else:
                messages.append({"role": "user", "content": "Please provide either an <answer> or a <tool> call based on your reasoning."})

    print("\n\n!!! Maximum iterations reached without final answer !!!\n\n")

    return "No answer could be found"


if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    # Load environment variables
    load_dotenv()
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Advanced ReAct agent with reasoning and multiple tools")
    parser.add_argument(
        "-q", "--question",
        type=str,
        default="what activity do you suggest to book if I travel to honolulu next week?",
        help="User question for the travel agent"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=10,
        help="Maximum number of agent iterations (default: 10)"
    )
    args = parser.parse_args()

    # Define available tools
    tools = {
        "get_weather": get_weather,
        "check_availability_activity": check_availability_activity
    }

    # Run the agent
    print(f"\n=== Question: {args.question}")
    result = run_agent(
        system_prompt=ADVANCED_SYSTEM_PROMPT,
        user_request=args.question,
        tools=tools,
        model="claude-sonnet-4-5-20250929",
        max_iterations=args.max_iterations
    )
    # Print out what we got:
    print("\n=== Final Answer ===")
    print(result)

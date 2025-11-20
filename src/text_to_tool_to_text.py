from utils import function_to_tool, add_tools_to_prompt, parse_response
import litellm


SYSTEM_PROMPT = """You are a helpful travel agent assistant. Your role is to suggest activities based on the destination and the current weather conditions there.

When you need information (like weather), you should use available tools.
When you have a final answer, provide it in <answer>your answer here</answer> tags.
When you need to use a tool, specify it as <tool>tool_name</tool> with <parameters>param1,param2</parameters>.
Please limit your suggestion to 3 activities maximum.

Available tools will be listed below."""


def get_weather(location: str) -> str:
    """Tool to get the current weather for a location.
    Parameters: location (string) - the city or location to get weather for.
    Returns the current temperature and conditions."""
    return "80 degrees fahrenheit, clear skies"


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

        # Check if we have a final answer - if so we return early
        if parsed.answer:
            print(parsed.answer)
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
            # No answer or tool found, prompt for clarification
            messages.append({"role": "user", "content": "Please provide either an <answer> or a <tool> call."})

    print("\n\n!!! Maximum iterations reached without final answer !!!\n\n")

    return "No answer could be found"


if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    # Load environment variables
    load_dotenv()
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Simple ReAct agent for travel recommendations")
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
        "get_weather": get_weather
    }

    # Run the agent
    print(f"\n=== Question: {args.question}")
    result = run_agent(
        system_prompt=SYSTEM_PROMPT,
        user_request=args.question,
        tools=tools,
        model="claude-sonnet-4-5-20250929",
        max_iterations=args.max_iterations
    )
    # Print out what we got:
    print("\n=== Final Answer ===")
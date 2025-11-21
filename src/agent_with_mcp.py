"""
Agent with MCP (Model Context Protocol) - Pedagogical Example

This script demonstrates how to integrate MCP tools with the smolagents framework,
showcasing a production-ready approach to extending agent capabilities with custom tools.

Key concepts:
1. MCP (Model Context Protocol): Standard protocol for exposing tools to LLM agents
2. smolagents: High-level framework that handles the ReAct loop automatically
3. LiteLLM: Unified interface for calling different LLM providers
4. Structured outputs: MCP tools can return Pydantic models for type-safe responses

The agent automatically:
1. Discovers available tools from the MCP server
2. Decides when to call tools based on the user's question
3. Executes tools and incorporates results
4. Provides a final answer using all gathered information

This demonstrates how the manual ReAct patterns from simple_react_loop.py and
advanced_react_loop.py are abstracted away by production frameworks like smolagents.
"""

from smolagents import MCPClient, CodeAgent, LiteLLMModel
from mcp import StdioServerParameters
from pathlib import Path


def run_agent(question: str, model_id: str = "claude-sonnet-4-5-20250929"):
    """Run the agent with MCP tools.

    Args:
        question: The question to ask the agent
        model_id: The LiteLLM model ID to use

    Returns:
        The agent's final answer
    """
    # Initialize the LiteLLM model
    model = LiteLLMModel(model_id=model_id)

    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    mcp_server_path = script_dir / "fast_mcp" / "server.py"

    # Configure MCP server parameters
    server_parameters = StdioServerParameters(
        command="uv", args=["run", "python", str(mcp_server_path)]
    )

    # Run agent with MCP tools
    with MCPClient(server_parameters, structured_output=True) as tools:
        agent = CodeAgent(tools=tools, model=model)
        result = agent.run(question)

        return result


if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Agent with MCP tools for answering questions"
    )
    parser.add_argument(
        "-q",
        "--question",
        type=str,
        default="what activity do you suggest to book if I travel to honolulu next week?",
        help="User question for the agent",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="claude-sonnet-4-5-20250929",
        help="LiteLLM model ID to use (default: claude-sonnet-4-5-20250929)",
    )
    args = parser.parse_args()

    # Run the agent
    print("\n=== Starting Agent with MCP Tools ===")
    print(f"Question: {args.question}\n")
    result = run_agent(question=args.question, model_id=args.model)

    # Print final answer
    print(f"\n{'=' * 60}")
    print("=== Final Answer ===")
    print(f"{'=' * 60}")
    print(result)
    print(f"{'=' * 60}\n")

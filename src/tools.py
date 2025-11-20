"""
Available tools for the agent examples.

Each tool is a Python function with:
- Clear docstring (used by LLM to understand the tool)
- Type hints for parameters
- Simple return values
"""


def get_weather(location: str) -> str:
    """Tool to get the current weather for a location.
    Parameters: location (string) - the city or location to get weather for.
    Returns the current temperature and conditions."""
    return "80 degrees fahrenheit, clear skies"

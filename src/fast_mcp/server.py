from fastmcp import FastMCP
from pydantic import BaseModel, Field


mcp = FastMCP("MCP Demo 🚀")


class WeatherInfo(BaseModel):
    location: str = Field(description="The location name")
    temperature: float = Field(description="Temperature in Celsius")
    conditions: str = Field(description="Weather conditions")
    humidity: int = Field(description="Humidity percentage", ge=0, le=100)


@mcp.tool(name="get_weather")
def get_weather(location: str) -> WeatherInfo:
    """Tool to get the current weather for a location.
    Parameters: location (string) - the city or location to get weather for.
    Returns the current temperature and conditions."""
    return WeatherInfo(
        location=location, temperature=26.7, conditions="clear skies", humidity=65
    )


if __name__ == "__main__":
    mcp.run()

from fastmcp import FastMCP

# Initialize the server
mcp = FastMCP("MySimpleAgentTools")

@mcp.tool()
def get_weather(city: str) -> str:
    """Returns the current weather for a given city."""
    # In a real app, you'd call an API here
    return f"The weather in {city} is currently 72°F and sunny."

@mcp.tool()
def calculate_growth(initial: float, rate: float) -> float:
    """Calculates growth based on an initial value and a rate."""
    return initial * (1 + rate)

if __name__ == "__main__":
    mcp.run()
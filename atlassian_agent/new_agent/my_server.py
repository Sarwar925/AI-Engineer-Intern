from fastmcp import FastMCP

# Initialize the server with a name
mcp = FastMCP("my-first-server", stateless_http=True)
# mcp = FastMCP("my-first-server")

# Define a tool using the @mcp.tool decorator
@mcp.tool
def get_weather(city: str) -> dict:
    """Get the current weather for a city."""
    # In production, you'd call a real weather API
    # For now, we'll return mock data
    weather_data = {
        "new york": {"temp": 72, "condition": "sunny"},
        "london": {"temp": 59, "condition": "cloudy"},
        "tokyo": {"temp": 68, "condition": "rainy"},
    }
    
    city_lower = city.lower()
    if city_lower in weather_data:
        return {"city": city, **weather_data[city_lower]}
    else:
        return {"city": city, "temp": 70, "condition": "unknown"}

# Run the server
# if __name__ == "__main__":
    # mcp.run(transport="stdio")

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8040)
import FastMCP

mcp = FastMCP("MYCP")

@mcp.tool()
def retrieve_data(user_id: str = "default") -> str:
    """Look up the active status of a specific user by their ID."""
    # Replace with your actual database or API logic
    return f"User {user_id} is currently active."

if __name__ == "__main__":
    mcp.run()
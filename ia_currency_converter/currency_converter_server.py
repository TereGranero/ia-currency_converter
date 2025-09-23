from dotenv import load_dotenv
import os, requests
from mcp.server.fastmcp import FastMCP

# Initialize environment variables and server
load_dotenv()
mcp = FastMCP('currency-converter-server', port=8081)
api_key: str = os.getenv("EXCHANGE_RATE_API_KEY")

# Define the currency conversion tool logic
@mcp.tool()
def convert_currency(
   amount: float, 
   from_currency: str, 
   to_currency: str
) -> str:
   """Convert currency using real-time exchange rates."""
   url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}/{amount}"
   response = requests.get(url)
   
   if response.status_code != 200:
      return f"Error: Unable to fetch exchange rates. Status code: {response.status_code}"
   
   data = response.json()
   
   return ( 
      f"{amount} {from_currency.upper()} = "
      f"{data['conversion_result']:.2f} {to_currency.upper()} "
      f"(Exchange Rate: {data['conversion_rate']:.4f})"
   )

# Run the server with Server-Sent Events (SSE) transport at http://localhost:8081/sse
if __name__ == "__main__":
   mcp.run(transport="sse")
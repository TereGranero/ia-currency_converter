from dotenv import load_dotenv
load_dotenv()
from crewai import LLM
import os, requests
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from IPython.display import Markdown


server_params = {
   "url": f"http://localhost:8081/sse",
}


# Crear el adaptador MCP y obtener las herramientas
mcp_adapter = MCPServerAdapter({"url": "http://localhost:8081/sse"})
mcp_tools = mcp_adapter.tools

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Initialize the Gemini LLM
gemini_llm =  LLM(
    model='gemini/gemini-2.5-pro',
    api_key=gemini_api_key,
    temperature=0.0
)
   
# Define the agent that uses the CurrencyConverterTool      
current_analyst = Agent(
   role = "Currency Analyst",
   goal = "To provide real-time currency conversions and finacial insigths.",
   backstory = (
      "You are a finance expert with deep knowledge of global exchange rate."
      "You help users with currency conversion and financial decision-making."
   ),
   allow_delegation = False,
   tools=[mcp_tools["convert_currency"]],
   llm=gemini_llm
)

# Assign a task to the agent
currency_conversion_task = Task(
   description=(
      "Convert {amount} {from_currency} to {to_currency} "
      "using real-time exchange rates."
      "Provide the equivalent amount and "
      "explain any relevant financial context."
   ),
   expected_output=("A detailed response including the "
                    "converted amount and financial insights."),
   agent=current_analyst
)

# Create a crew to manage the agent and task
crew = Crew(
   agents=[current_analyst],
   tasks=[currency_conversion_task],
   process=Process.sequential
)

# Run the crew to execute the task
response = crew.kickoff(inputs={
   "amount": 100,
   "from_currency": "USD",
   "to_currency": "EUR"})

# Display the response 

print(response.raw)
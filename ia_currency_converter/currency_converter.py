from dotenv import load_dotenv
load_dotenv()
from crewai import LLM
import os
import requests
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process
from IPython.display import Markdown

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Initialize the Gemini LLM
gemini_llm =  LLM(
    model='gemini/gemini-2.5-pro',
    api_key=gemini_api_key,
    temperature=0.0
)

# Define the input schema for the tool
class CurrencyConverterInput(BaseModel):
   """Input schema for CurrencyConverterTool."""
   amount: float = Field(..., description="The amount of money to convert.")
   from_currency: str = Field(..., description="The currency code to convert from (e.g., 'USD').")
   to_currency: str = Field(..., description="The currency code to convert to (e.g., 'EUR').")
    
# Define the tool    
class CurrencyConverterTool(BaseTool):
    name: str = "Currency Converter Tool"
    description: str = "A tool to convert currency amounts from one currency to another using real-time exchange rates."
    args_schema: Type[BaseModel] = CurrencyConverterInput
    api_key: str = os.getenv("EXCHANGE_RATE_API_KEY")

    def _run(self, amount: float, from_currency: str, to_currency: str) -> str:
        
      url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/{from_currency}"
      response = requests.get(url)
      
      if response.status_code != 200:
         return f"Error: Unable to fetch exchange rates. Status code: {response.status_code}"
      
      data = response.json()
      if "conversion_rates" not in data or to_currency not in data["conversion_rates"]:
         return f"Invalid currency code: {to_currency}"
      
      rate = data["conversion_rates"][to_currency]
      converted_amount = amount * rate
      return f"{amount} {from_currency} is equivalent to {converted_amount:.2f} {to_currency}."
   
# Define the agent that uses the CurrencyConverterTool      
current_analyst = Agent(
   role = "Currency Analyst",
   goal = "To provide real-time currency conversions and finacial insigths.",
   backstory = (
      "You are a finance expert with deep knowledge of global exchange rate."
      "You help users with currency conversion and financial decision-making."
   ),
   tools=[CurrencyConverterTool()],
   verbose = True,
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

# Display the response in Markdown format
Markdown(response.raw)
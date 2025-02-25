from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Iterator, Optional
from phi.agent import Agent, RunResponse
from phi.tools.sql import SQLTools
from phi.model.groq import Groq
from phi.model.google import Gemini
from tools_gpt import SQLStatsTools
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from selenium_main import get_policy_info

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8050"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
db_url = 'sqlite:///insurance_data.db'

# Initialize the AI agent
# policy_finder = Agent(
#     tools=[get_policy_info],
#         # model=Gemini(id='gemini-1.5-flash'),
#         model = Groq(id='llama3-70b-8192'),
#         # model=Ollama(id='gemma2'),
#         markdown=True,
#         instructions=[
#             'The user will give you a Vehicle number or policy number'
#             'When Given the query find the car number or Policy number and insert it into the tool function paramater as a string and run',
#             'Give the Tool results to the user',
#             'Return the details in a well formatted clean markdown and not json '
#             'Add a line break for every policy detail item'

#         ],
#         add_context=True
#     )
sql_agent = Agent(
    tools=[SQLStatsTools(db_url=db_url)],
    model=Groq(id='llama3-70b-8192'),
    # model=Gemini(id='gemini-1.5-flash'),
    markdown=True,
    description="You are a data and sql analyst good in running database queries and also an Insurance Service Assistant",
    instructions=[
        'the database is called insurance_db and the table is called insurance_transactions',
        '''columns and their datatypes are [Transaction Date] TEXT, [Policy No] TEXT, [Trans Type] TEXT, 
        Branch TEXT, Class TEXT, [Dr/Cr No] TEXT, [Risk ID] TEXT,
        Insured TEXT, [Intermediary Type] TEXT, Intermediary TEXT,
        Marketer TEXT, WEF TEXT, WET TEXT, CURRENCY TEXT,
        [Sum Insured] REAL, Premium REAL, PAID REAL,
        Year INTEGER, [Month Name] TEXT, Month INTEGER,
        Quarter INTEGER, Weeks INTEGER''',
        'When given a question use your mind to know which query need to be done based on the question',
        'Use the tool provided to do any in depth analysis if any',
        'You are an sqlite database expert in running queries',
        'Answer like an customer service and an analyst',
        "Make your answers simple and short",
        "Provide Summary and Suggestions if necessary",
        "Any Questions Out of Context tell them to review their question",
        "With the intermediary, if the user asked for ranking exclude DIRECT or DIRECT DIRECT",
        'Learn from the user sometimes and also minimize error',
        'The currency is GH₵'
        "" 
    ],
    add_context=True,
    add_history_to_messages=True,
    # Number of historical responses to add to the messages.
    num_history_responses=3
)
# bd_team = Agent(
#     team=[policy_finder, sql_agent],
#     model=Gemini(id='gemini-1.5-flash'),
#     instructions=[
#         "First When the user gives you a prompt or question use agent_1",
#         "Unless the prompt or question is about Finding a policy use agent_0",
#         "My Currency sign is GH₵",
#         "Answer it like it is from you"
#     ],
#     markdown=True,
#     add_history_to_messages=True,
#     num_history_responses=3
# )
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = sql_agent.run(request.message)
        return {"response": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
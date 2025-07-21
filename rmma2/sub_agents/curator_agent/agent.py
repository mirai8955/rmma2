from .prompt import CURATOR_AGENT_PROMPT
from google.adk.agents import LlmAgent, Agent
from google.adk.tools import google_search, agent_tool
from os import getenv
from dotenv import load_dotenv

load_dotenv()
MODEL = getenv("MODEL_PRO")



search_agent = Agent(
    model=MODEL or "gemini-2.5-flash",
    name='SearchAgent',
    instruction="""
    You're a specialist in Google Search
    """,
    tools=[google_search],
)

curator_agent=LlmAgent(
    model=MODEL or "gemini-2.5-flash",
    name="CuratorAgent",
    description=(
        "web検索ツールを使用し，"
        "楽天モバイルに関するキャンペーンや利用者にとってお得な最新情報を常に取得し，"
        "その結果をまとめます．"
    ),
    instruction=CURATOR_AGENT_PROMPT,
    output_key="curator_agent_output",
    tools=[agent_tool.AgentTool(agent=search_agent)],
)
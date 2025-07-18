from google.adk.agents import LlmAgent

from . import prompt
from rmma2.sub_agents.posting_agent.agent import posting_agent
from rmma2.sub_agents.reply_agent.agent import reply_pipeline_agent
from rmma2.sub_agents.curator_agent.agent import curator_agent
from os import getenv
from dotenv import load_dotenv

load_dotenv()
MODEL = getenv("MODEL")

rmma = LlmAgent(
    name="RMMA",
    model=MODEL or "gemini-2.5-flash",
    description=(
    "楽天モバイルに関するキャンペーン情報を調べ、"
    "楽天モバイルを契約したくなるような投稿を考え、"
    "複数のエージェントと協力しながらXでツイートを投稿します。"
    ),
    instruction=prompt.RAKUTEN_MOBILE_MARKETING_AGENT_PROMPT,
    sub_agents=[
        posting_agent,
        reply_pipeline_agent,
        curator_agent,
    ],
    output_key="rmma_output",
)

root_agent = rmma
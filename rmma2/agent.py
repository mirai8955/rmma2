from google.adk.agents import LlmAgent

from . import prompt
from rmma2.sub_agents.posting_agent.agent import posting_agent
from rmma2.sub_agents.reply_agent.agent import reply_pipeline_agent
from rmma2.sub_agents.rmresearch_agent.agent import rmresearch_agent
from rmma2.sub_agents.persona_agent.agent import persona_agent
from prompt.prompt_manager import PromptManager
from os import getenv
from dotenv import load_dotenv

load_dotenv()
MODEL = getenv("MODEL")

def get_prompt(ctx=None):
    pm = PromptManager()
    return pm.get_prompt("rakuten_mobile_marketing_agent_prompt")


rmma = LlmAgent(
    name="RMMA",
    model=MODEL or "gemini-2.5-flash",
    description=(
    "楽天モバイルに関するキャンペーン情報を調べ、"
    "楽天モバイルを契約したくなるような投稿を考え、"
    "複数のエージェントと協力しながらXでツイートを投稿します。"
    ),
    instruction=get_prompt,
    sub_agents=[
        posting_agent,
        reply_pipeline_agent,
        rmresearch_agent,
        persona_agent,
    ],
    output_key="rmma_output",
)

root_agent = rmma
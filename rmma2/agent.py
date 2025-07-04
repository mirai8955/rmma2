from google.adk.agents import LlmAgent

from . import prompt
from rmma2.sub_agents.posting_agent.agent import posting_agent

MODEL = "gemini-2.5-flash"

rmma = LlmAgent(
    name="rakuten_mobile_marketing_agent",
    model=MODEL,
    description=(
    "楽天モバイルに関するキャンペーン情報を調べ、"
    "楽天モバイルを契約したくなるような投稿を考え、"
    "複数のエージェントと協力しながらXでツイートを投稿します。"
    ),
    instruction=prompt.RAKUTEN_MOBILE_MARKETING_AGENT_PROMPT,
    sub_agents=[
        posting_agent,
    ],
    output_key="rmma_output",
)

root_agent = rmma
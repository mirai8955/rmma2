from google.adk.agents import LlmAgent

from . import prompt

MODEL = "gemini-2.5-flash"

rmma = LlmAgent(
    name="Rakuten Mobile Marketing Agent",
    model=MODEL,
    description=(
    "楽天モバイルに関するキャンペーン情報を調べ、"
    "楽天モバイルを契約したくなるような投稿を考え、"
    "複数のエージェントと協力しながらXでツイートを投稿します。"
    ),
    instruction=prompt.RAKUTEN_MOBILE_MARKETING_AGENT_PROMPT,
    output_key="rmma_output",
)

root_agent = rmma
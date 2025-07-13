from os import getenv
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from .tools import post_on_x, search_on_x

from . import prompt


load_dotenv()
MODEL = getenv("MODEL")

posting_agent = LlmAgent(
    model=MODEL or "gemini-2.5-flash",
    name="PostingAgent",
    description=(
        "楽天モバイルの新規契約獲得のための投稿内容を考え，"
        "虚偽の投稿を生成していないかをチェックし，"
        "実際にxに投稿をポストします．"
        "または，ユーザの希望に応じてXの投稿を検索します．"
    ),
    instruction=prompt.RMMA_POSTING_PROMPT,
    output_key="posting_agent_output",
    tools=[post_on_x, search_on_x],
)
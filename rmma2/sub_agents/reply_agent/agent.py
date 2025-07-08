from google.adk.agents import LlmAgent, SequentialAgent
from .prompt import RMMA_REPLY_PROMPT,  TWEET_SEARCH_AGENT_PROMPT
from os import getenv
from dotenv import load_dotenv
from .tools import post_on_x, search_on_x

load_dotenv()
MODEL = getenv("MODEL")

tweet_search_agent = LlmAgent(
    name="TweetSearchAgent",
    model=MODEL,
    descritption="XのAPIを使用して投稿を検索するエージェント",
    instructions=TWEET_SEARCH_AGENT_PROMPT,
    output_key="search_result",
    tool=search_on_x
)

# arrange_schema_agent = LlmAgent(
#     name="ArrangeSchemaAgent",
#     model=MODEL,
#     description="与えられた検索結果を整形して出力します"，
#     instructions="""
#     jsonで投稿の検索結果が与えられます．それらを全てTEXTの形に変更し，
#     一つの出力にまとめてください
#     """
#     output_schema=
# )

reply_generation_agent = LlmAgent(
    name="ReplyGenerationAgent",
    model=MODEL,
    description="検索結果から楽天モバイルをおすすめする返信を考えるエージェント",
    instructions="""
    あなたは優秀なマーケターであるだけでなく，優秀な返信エージェントです．
    あなたの目的はより多くの人に楽天モバイルに興味を持ってもらうように，Xの投稿に返信する内容を考慮することです．
    **検索結果**
    ```
    {search_result}
    ```

    **タスク**
    検索結果から，投稿した人が楽天モバイルに興味を持ってもらうような返信内容を生成してください．
    返信内容は信頼性と親しみやすさを兼ね備えた文章です．
    虚偽の発言は控えており，必ず事実が確認できる内容の返信しか生成しません．
    """,
    tools=[search_on_x],
)

reply_pipeline_agent = SequentialAgent(
    name="ReplyPipelineAgent",
    model=MODEL,
    description="Xから該当する投稿を検索し，返信内容を考え，返信するエージェント",
    instructions=RMMA_REPLY_PROMPT,
    sub_agents=[tweet_search_agent, reply_generation_agent],
)

# root_agent = reply_pipeline_agent
from google.adk.agents import LlmAgent, SequentialAgent
from .prompt import REPLY_GENERATION_AGENT, RMMA_REPLY_PROMPT,  TWEET_SEARCH_AGENT_PROMPT, REPLY_POST_AGENT
from os import getenv
from dotenv import load_dotenv
from rmma2.sub_agents.posting_agent.tools import search_on_x, reply_on_x

load_dotenv()
MODEL = getenv("MODEL")

tweet_search_agent = LlmAgent(
    name="TweetSearchAgent",
    model=MODEL or "gemini-2.5-flash",
    description="XのAPIを使用して投稿を検索するエージェント",
    instruction=TWEET_SEARCH_AGENT_PROMPT,
    output_key="search_result",
    tools=[search_on_x],
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
    model=MODEL or "gemini-2.5-flash",
    description="検索結果から楽天モバイルをおすすめする返信を考えるエージェント",
    instruction=REPLY_GENERATION_AGENT,
    output_key="reply_content"
)

reply_post_agent = LlmAgent(
    name="ReplyPostAgent",
    model=MODEL or "gemini-2.5-flash",
    description="生成した文章で実際に返信を実行するエージェント",
    instruction=REPLY_POST_AGENT,
    tools=[reply_on_x],
)

reply_pipeline_agent = SequentialAgent(
    name="ReplyPipelineAgent",
    # model=MODEL,
    description="Xから該当する投稿を検索し，返信内容を考え，返信するエージェント",
    # instruction=RMMA_REPLY_PROMPT,
    sub_agents=[tweet_search_agent, reply_generation_agent, reply_post_agent],
)

# root_agent = reply_pipeline_agent